package com.yorijori.user;

import com.yorijori.common.response.ApiResponse;
import com.yorijori.common.security.LoginUser;
import com.yorijori.user.dto.AvoidSettings;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 내 설정
 * GET /api/me/avoid      못 먹는 재료 (v9)
 * PUT /api/me/avoid      못 먹는 재료 저장 (전체 교체)
 * PUT /api/me/anim       애니메이션 On/Off (v7)  { "on": true }
 */
@RestController
@RequestMapping("/api/me")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/avoid")
    public ApiResponse<AvoidSettings> avoid(@AuthenticationPrincipal LoginUser me) {
        return ApiResponse.ok(userService.getAvoid(me.getId()));
    }

    @PutMapping("/avoid")
    public ApiResponse<AvoidSettings> saveAvoid(@AuthenticationPrincipal LoginUser me, @RequestBody AvoidSettings req) {
        return ApiResponse.ok(userService.saveAvoid(me.getId(), req));
    }

    @PutMapping("/anim")
    public ApiResponse<Void> anim(@AuthenticationPrincipal LoginUser me, @RequestBody Map<String, Boolean> body) {
        userService.setAnim(me.getId(), Boolean.TRUE.equals(body.get("on")));
        return ApiResponse.ok(null);
    }
}
