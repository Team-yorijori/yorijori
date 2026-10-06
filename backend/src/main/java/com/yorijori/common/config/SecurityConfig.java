package com.yorijori.common.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.yorijori.common.exception.ErrorCode;
import com.yorijori.common.response.ApiResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.HeadersConfigurer;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.security.web.context.SecurityContextRepository;

/**
 * 세션 로그인.
 * - 화면(/, /fridge …)과 정적 파일, 레시피·재료 조회는 로그인 없이 볼 수 있다 (데모처럼 둘러보기)
 * - 내 냉장고·만든 요리·장보기 API는 로그인해야 한다 → 401 JSON
 * - CSRF: 화면 폼은 보호하고, /api/** 는 JSON + 같은 사이트 쿠키라 우선 제외한다.
 *   TODO(백) 배포 전에 CSRF 토큰 헤더 방식(X-XSRF-TOKEN)으로 바꾸는 것을 검토한다.
 */
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http, ObjectMapper om) throws Exception {
        http
            .csrf(c -> c.ignoringRequestMatchers("/api/**", "/h2-console/**"))
            .headers(h -> h.frameOptions(HeadersConfigurer.FrameOptionsConfig::sameOrigin)) // h2-console
            .authorizeHttpRequests(a -> a
                .requestMatchers("/", "/fridge", "/recipes", "/recipes/*", "/dishes", "/cart", "/items",
                                 "/login", "/signup", "/error").permitAll()
                .requestMatchers("/css/**", "/js/**", "/models/**", "/img/**", "/favicon.ico").permitAll()
                .requestMatchers("/h2-console/**").permitAll()
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/recipes/recommend").authenticated()
                .requestMatchers(HttpMethod.GET, "/api/ingredients/**", "/api/scan/classes",
                                 "/api/recipes/data", "/api/recipes/*").permitAll()
                .anyRequest().authenticated())
            // API는 로그인 페이지로 보내지 않고 401 JSON
            .exceptionHandling(e -> e.authenticationEntryPoint((req, res, ex) -> {
                if (req.getRequestURI().startsWith("/api/")) {
                    res.setStatus(401);
                    res.setContentType(MediaType.APPLICATION_JSON_VALUE);
                    res.setCharacterEncoding("UTF-8");
                    om.writeValue(res.getWriter(), ApiResponse.fail(ErrorCode.UNAUTHORIZED.name(), ErrorCode.UNAUTHORIZED.message()));
                } else {
                    res.sendRedirect("/login");
                }
            }))
            .formLogin(f -> f.disable())          // 로그인은 /api/auth/login (AuthController)
            .httpBasic(b -> b.disable())
            .logout(l -> l.logoutUrl("/api/auth/logout")
                          .logoutSuccessHandler((req, res, auth) -> {
                              res.setContentType(MediaType.APPLICATION_JSON_VALUE);
                              res.setCharacterEncoding("UTF-8");
                              om.writeValue(res.getWriter(), ApiResponse.ok(null, "로그아웃했습니다."));
                          }));
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration cfg) throws Exception {
        return cfg.getAuthenticationManager();
    }

    @Bean
    public SecurityContextRepository securityContextRepository() {
        return new HttpSessionSecurityContextRepository();
    }
}
