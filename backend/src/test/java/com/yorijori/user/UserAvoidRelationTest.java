package com.yorijori.user;

import com.yorijori.common.exception.ApiException;
import com.yorijori.user.dto.AvoidSettings;
import com.yorijori.user.dto.SignupRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
class UserAvoidRelationTest {
    @Autowired UserService users;
    @Autowired JdbcTemplate jdbc;
    private Long userId;

    @BeforeEach
    void signup() {
        userId = users.signup(new SignupRequest(UUID.randomUUID() + "@avoid.test", "password1", "알레르기검증")).getId();
    }

    @Test
    void selectedGroupRenameKeepsSelectionAndRecommendationTerms() {
        users.saveAvoid(userId, new AvoidSettings(List.of("대두"), List.of("오이"), false));
        jdbc.update("UPDATE avoid_group SET name = ? WHERE name = ?", "대두이름변경", "대두");
        try {
            assertThat(users.getAvoid(userId).groups()).containsExactly("대두이름변경");
            assertThat(users.avoidTerms(userId)).contains("두부", "간장", "오이");
        } finally {
            jdbc.update("UPDATE avoid_group SET name = ? WHERE name = ?", "대두", "대두이름변경");
        }
    }

    @Test
    void groupNamesRoundTripWithIdsAndItemsStaySeparate() {
        AvoidSettings result = users.saveAvoid(userId,
                new AvoidSettings(List.of("대두", "대두", "계란"), List.of(" 오이 ", " 오이 "), true));

        assertThat(result.groups()).containsExactlyInAnyOrder("대두", "계란");
        assertThat(result.items()).containsExactly("오이");
        assertThat(users.getAvoid(userId)).isEqualTo(result);
        assertThat(result.show()).isTrue();
        assertThat(jdbc.queryForList("SELECT g.name FROM user_avoid_group uag JOIN avoid_group g ON g.id = uag.group_id WHERE uag.user_id = ?", String.class, userId))
                .containsExactlyInAnyOrder("대두", "계란");
        assertThat(jdbc.queryForList("SELECT kind FROM user_avoid WHERE user_id = ?", String.class, userId))
                .containsExactly("ITEM");

        assertThat(users.saveAvoid(userId, new AvoidSettings(null, null, false)))
                .isEqualTo(new AvoidSettings(List.of(), List.of(), false));
        assertThat(users.avoidTerms(userId)).isEmpty();
    }

    @Test
    void invalidGroupReplacementPreservesAllPriorPreferences() {
        AvoidSettings original = new AvoidSettings(List.of("대두"), List.of("오이"), true);
        users.saveAvoid(userId, original);

        assertThatThrownBy(() -> users.saveAvoid(userId,
                new AvoidSettings(List.of("계란", "존재하지않는묶음"), List.of("당근"), false)))
                .isInstanceOf(ApiException.class);

        assertThat(users.getAvoid(userId)).isEqualTo(original);
        assertThat(users.avoidTerms(userId)).contains("두부", "오이").doesNotContain("당근");
    }

    @Test
    void trimsAndDeduplicatesCustomItemsBeforeApplyingUniqueKey() {
        var result=users.saveAvoid(userId,new AvoidSettings(List.of("대두"),
                java.util.Arrays.asList("오이"," 오이 ",null,""),false));
        assertThat(result.items()).containsExactly("오이");
        assertThat(result.groups()).containsExactly("대두");
    }
}
