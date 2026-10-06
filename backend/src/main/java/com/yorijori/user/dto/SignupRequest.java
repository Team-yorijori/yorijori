package com.yorijori.user.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record SignupRequest(
        @NotBlank(message = "이메일을 입력하세요.") @Email(message = "이메일 형식을 확인하세요.") String email,
        @NotBlank(message = "비밀번호를 입력하세요.") @Size(min = 8, max = 64, message = "비밀번호는 8자 이상입니다.") String password,
        @Size(max = 30, message = "닉네임은 30자 이하입니다.") String nickname) {}
