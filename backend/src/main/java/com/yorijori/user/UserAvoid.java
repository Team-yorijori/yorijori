package com.yorijori.user;

import jakarta.persistence.*;

/**
 * v9 못 먹는 재료 (알레르기·기피).
 * kind = GROUP → value 는 알레르기 묶음 이름(avoid_group.name, 예: "대두")
 * kind = ITEM  → value 는 사용자가 직접 넣은 재료 이름(예: "오이")
 */
@Entity
@Table(name = "user_avoid",
       uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "kind", "avoid_value"}))
public class UserAvoid {

    public enum Kind { GROUP, ITEM }

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private Kind kind;

    @Column(name = "avoid_value", nullable = false, length = 50)
    private String value;

    protected UserAvoid() {}

    public UserAvoid(Long userId, Kind kind, String value) {
        this.userId = userId;
        this.kind = kind;
        this.value = value;
    }

    public Long getId() { return id; }
    public Long getUserId() { return userId; }
    public Kind getKind() { return kind; }
    public String getValue() { return value; }
}
