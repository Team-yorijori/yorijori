package com.yorijori.user;

import jakarta.persistence.*;

/**
 * v9 못 먹는 재료 (알레르기·기피).
 * 현재는 ITEM만 저장하며 value는 사용자가 직접 넣은 재료 이름(예: "오이")이다.
 * 알레르기 묶음 선택은 UserAvoidGroup에서 ID로 연결한다.
 * GROUP enum 값은 V5 이전 데이터 표현과의 호환을 위해 남겨 둔다.
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
