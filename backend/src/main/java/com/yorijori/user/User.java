package com.yorijori.user;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(name = "password_hash", nullable = false, length = 100)
    private String passwordHash;

    @Column(nullable = false, length = 30)
    private String nickname;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private Role role = Role.USER;

    /** v9 못 먹는 재료: true면 추천에서 빼지 않고 빨갛게 표시만 한다 */
    @Column(name = "avoid_show", nullable = false)
    private boolean avoidShow = false;

    /** 애니메이션 On/Off (데모 v7) */
    @Column(name = "anim_on", nullable = false)
    private boolean animOn = true;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    protected User() {}

    public User(String email, String passwordHash, String nickname) {
        this.email = email;
        this.passwordHash = passwordHash;
        this.nickname = nickname;
    }

    public Long getId() { return id; }
    public String getEmail() { return email; }
    public String getPasswordHash() { return passwordHash; }
    public String getNickname() { return nickname; }
    public Role getRole() { return role; }
    public boolean isAvoidShow() { return avoidShow; }
    public boolean isAnimOn() { return animOn; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    public void setAvoidShow(boolean avoidShow) { this.avoidShow = avoidShow; }
    public void setAnimOn(boolean animOn) { this.animOn = animOn; }
    public void changeNickname(String nickname) { this.nickname = nickname; }
}
