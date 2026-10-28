package com.yorijori.user;

import com.yorijori.ingredient.AvoidGroup;
import jakarta.persistence.*;

/** 알레르기 묶음의 이름이 바뀌어도 사용자 선택을 유지하는 ID 관계. */
@Entity
@Table(name = "user_avoid_group",
       uniqueConstraints = @UniqueConstraint(columnNames = {"user_id", "group_id"}))
public class UserAvoidGroup {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "group_id", nullable = false)
    private AvoidGroup group;

    protected UserAvoidGroup() {}

    public UserAvoidGroup(Long userId, AvoidGroup group) {
        this.userId = userId;
        this.group = group;
    }

    public AvoidGroup getGroup() { return group; }
}
