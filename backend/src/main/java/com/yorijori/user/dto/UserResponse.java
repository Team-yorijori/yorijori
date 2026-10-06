package com.yorijori.user.dto;

import com.yorijori.user.User;

public record UserResponse(Long id, String email, String nickname, boolean animOn) {
    public static UserResponse of(User u) {
        return new UserResponse(u.getId(), u.getEmail(), u.getNickname(), u.isAnimOn());
    }
}
