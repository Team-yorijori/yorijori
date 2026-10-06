package com.yorijori.ingredient;

import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.List;

/**
 * v9 알레르기 묶음 (식품 알레르기 표시 대상 위주) — 데모의 AVOID_GROUPS
 * 예: 대두 → 두부, 콩, 된장, 간장, 두유, 유부
 */
@Entity
@Table(name = "avoid_group")
public class AvoidGroup {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 30)
    private String name;

    @Column(name = "sort_no", nullable = false)
    private int sortNo;

    /** 고를 때 보여 줄 주의 문구 (예: 대두 → 간장·된장까지 빠진다) */
    @Column(length = 200)
    private String warning;

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "avoid_group_term", joinColumns = @JoinColumn(name = "group_id"))
    @Column(name = "term", length = 30)
    @OrderColumn(name = "sort_no")
    private List<String> terms = new ArrayList<>();

    protected AvoidGroup() {}

    public Long getId() { return id; }
    public String getName() { return name; }
    public int getSortNo() { return sortNo; }
    public String getWarning() { return warning; }
    public List<String> getTerms() { return terms; }
}
