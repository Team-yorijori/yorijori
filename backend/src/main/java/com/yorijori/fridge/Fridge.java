package com.yorijori.fridge;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/** 냉장고. 회원과 직접 묶지 않고 fridge_member 로 연결한다 (가족 공유 대비) */
@Entity
@Table(name = "fridge")
public class Fridge {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String name;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    protected Fridge() {}

    public Fridge(String name) { this.name = name; }

    public Long getId() { return id; }
    public String getName() { return name; }
    public void rename(String name) { this.name = name; }
}
