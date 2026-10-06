package com.yorijori.fridge;

import jakarta.persistence.*;

/** 냉장고 구성원. 지금은 가입할 때 만든 냉장고의 OWNER 한 명뿐이다. TODO(백) 가족 초대 */
@Entity
@Table(name = "fridge_member",
       uniqueConstraints = @UniqueConstraint(columnNames = {"fridge_id", "user_id"}))
public class FridgeMember {

    public enum Role { OWNER, MEMBER }

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "fridge_id", nullable = false)
    private Long fridgeId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private Role role;

    protected FridgeMember() {}

    public FridgeMember(Long fridgeId, Long userId, Role role) {
        this.fridgeId = fridgeId;
        this.userId = userId;
        this.role = role;
    }

    public Long getFridgeId() { return fridgeId; }
    public Long getUserId() { return userId; }
    public Role getRole() { return role; }
}
