package com.yorijori.user;

import com.yorijori.common.exception.ApiException;
import com.yorijori.common.exception.ErrorCode;
import com.yorijori.fridge.FridgeService;
import com.yorijori.ingredient.AvoidGroupService;
import com.yorijori.user.dto.AvoidSettings;
import com.yorijori.user.dto.SignupRequest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Service
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository users;
    private final UserAvoidRepository avoids;
    private final PasswordEncoder encoder;
    private final FridgeService fridgeService;
    private final AvoidGroupService avoidGroups;

    public UserService(UserRepository users, UserAvoidRepository avoids, PasswordEncoder encoder,
                       FridgeService fridgeService, AvoidGroupService avoidGroups) {
        this.users = users;
        this.avoids = avoids;
        this.encoder = encoder;
        this.fridgeService = fridgeService;
        this.avoidGroups = avoidGroups;
    }

    /** 가입하면 기본 냉장고를 하나 만들어 주인으로 넣는다 (가족 공유 대비 구조) */
    @Transactional
    public User signup(SignupRequest req) {
        String email = req.email().trim().toLowerCase();
        if (users.existsByEmail(email)) throw new ApiException(ErrorCode.DUPLICATE_EMAIL);
        String nick = req.nickname() == null || req.nickname().isBlank() ? email.substring(0, email.indexOf('@')) : req.nickname().trim();
        if (nick.length() > 30) nick = nick.substring(0, 30);
        User u = users.save(new User(email, encoder.encode(req.password()), nick));
        fridgeService.createDefaultFridge(u.getId(), nick + "의 냉장고");
        return u;
    }

    public User get(Long userId) {
        return users.findById(userId).orElseThrow(() -> new ApiException(ErrorCode.USER_NOT_FOUND));
    }

    @Transactional
    public void setAnim(Long userId, boolean on) {
        get(userId).setAnimOn(on);
    }

    /* ---------- v9 못 먹는 재료 ---------- */

    public AvoidSettings getAvoid(Long userId) {
        List<UserAvoid> list = avoids.findByUserId(userId);
        return new AvoidSettings(
                list.stream().filter(a -> a.getKind() == UserAvoid.Kind.GROUP).map(UserAvoid::getValue).toList(),
                list.stream().filter(a -> a.getKind() == UserAvoid.Kind.ITEM).map(UserAvoid::getValue).toList(),
                get(userId).isAvoidShow());
    }

    /** 통째로 바꾼다 (화면에서 칩을 누를 때마다 전체를 보낸다) */
    @Transactional
    public AvoidSettings saveAvoid(Long userId, AvoidSettings req) {
        avoids.deleteByUserId(userId);
        avoids.flush();
        Set<String> known = avoidGroups.groupNames();
        for (String g : new LinkedHashSet<>(nullSafe(req.groups()))) {
            if (!known.contains(g)) throw new ApiException(ErrorCode.INVALID_INPUT, "알 수 없는 알레르기 묶음: " + g);
            avoids.save(new UserAvoid(userId, UserAvoid.Kind.GROUP, g));
        }
        for (String it : new LinkedHashSet<>(nullSafe(req.items()))) {
            String name = it.trim();
            if (!name.isEmpty() && name.length() <= 50) avoids.save(new UserAvoid(userId, UserAvoid.Kind.ITEM, name));
        }
        get(userId).setAvoidShow(req.show());
        return getAvoid(userId);
    }

    /** 추천·경고에 쓰는 실제 이름 목록: 묶음을 펼친 이름 + 직접 넣은 이름 */
    public List<String> avoidTerms(Long userId) {
        Set<String> terms = new LinkedHashSet<>();
        for (UserAvoid a : avoids.findByUserId(userId)) {
            if (a.getKind() == UserAvoid.Kind.GROUP) terms.addAll(avoidGroups.termsOf(a.getValue()));
            else terms.add(a.getValue());
        }
        return List.copyOf(terms);
    }

    private static <T> List<T> nullSafe(List<T> l) { return l == null ? List.of() : l; }
}
