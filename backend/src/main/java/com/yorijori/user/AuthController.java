package com.yorijori.user;

import com.yorijori.common.exception.ApiException;
import com.yorijori.common.exception.ErrorCode;
import com.yorijori.common.response.ApiResponse;
import com.yorijori.common.security.LoginUser;
import com.yorijori.user.dto.LoginRequest;
import com.yorijori.user.dto.SignupRequest;
import com.yorijori.user.dto.UserResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.SecurityContextRepository;
import org.springframework.web.bind.annotation.*;

/**
 * POST /api/auth/signup  회원가입 (가입 후 바로 로그인)
 * POST /api/auth/login   로그인 (세션)
 * POST /api/auth/logout  로그아웃 (SecurityConfig)
 * GET  /api/auth/me      로그인한 회원 (없으면 data = null)
 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserService userService;
    private final AuthenticationManager authManager;
    private final SecurityContextRepository contextRepo;

    public AuthController(UserService userService, AuthenticationManager authManager, SecurityContextRepository contextRepo) {
        this.userService = userService;
        this.authManager = authManager;
        this.contextRepo = contextRepo;
    }

    @PostMapping("/signup")
    public ApiResponse<UserResponse> signup(@Valid @RequestBody SignupRequest req,
                                            HttpServletRequest httpReq, HttpServletResponse httpRes) {
        User u = userService.signup(req);
        login(new LoginRequest(req.email(), req.password()), httpReq, httpRes);
        return ApiResponse.ok(UserResponse.of(u), u.getNickname() + " 님, 가입을 환영합니다.");
    }

    @PostMapping("/login")
    public ApiResponse<UserResponse> login(@Valid @RequestBody LoginRequest req,
                                           HttpServletRequest httpReq, HttpServletResponse httpRes) {
        Authentication auth;
        try {
            auth = authManager.authenticate(
                    new UsernamePasswordAuthenticationToken(req.email().trim().toLowerCase(), req.password()));
        } catch (AuthenticationException e) {
            throw new ApiException(ErrorCode.LOGIN_FAILED);
        }
        SecurityContext ctx = SecurityContextHolder.createEmptyContext();
        ctx.setAuthentication(auth);
        SecurityContextHolder.setContext(ctx);
        contextRepo.saveContext(ctx, httpReq, httpRes);
        LoginUser me = (LoginUser) auth.getPrincipal();
        return ApiResponse.ok(UserResponse.of(userService.get(me.getId())), me.getNickname() + " 님, 환영합니다.");
    }

    @GetMapping("/me")
    public ApiResponse<UserResponse> me(@AuthenticationPrincipal LoginUser me) {
        return ApiResponse.ok(me == null ? null : UserResponse.of(userService.get(me.getId())));
    }
}
