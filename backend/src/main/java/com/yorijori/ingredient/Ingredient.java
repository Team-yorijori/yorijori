package com.yorijori.ingredient;

import jakarta.persistence.*;

/**
 * 재료 기준표 — 데모의 MASTER { 이름: [분류, 냉장 보관일수, 단위, 기본수량, 접시 색] }
 * 재료는 이름이 아니라 이 id로 연결한다. 기준표에 없는 재료는 fridge_item.name 만 저장한다.
 */
@Entity
@Table(name = "ingredient")
public class Ingredient {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String name;

    /** 채소 · 과일 · 육류 · 해산물 · 유제품·알 · 가공식품 · 반찬 · 곡류 · 기타 */
    @Column(nullable = false, length = 20)
    private String category;

    /** 냉장 보관 일수 — 소비기한 자동 안내(참고용) */
    @Column(name = "fridge_days", nullable = false)
    private int fridgeDays;

    @Column(nullable = false, length = 10)
    private String unit;

    @Column(name = "default_qty", nullable = false)
    private double defaultQty;

    /** 접시 그림·애니메이션 색 */
    @Column(length = 7)
    private String color;

    /** 영수증 무게 → 개수 환산: 1개당 g (예: 양파 200). 없으면 null */
    @Column(name = "each_gram")
    private Integer eachGram;

    protected Ingredient() {}

    public Ingredient(String name, String category, int fridgeDays, String unit, double defaultQty, String color) {
        this.name = name;
        this.category = category;
        this.fridgeDays = fridgeDays;
        this.unit = unit;
        this.defaultQty = defaultQty;
        this.color = color;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getCategory() { return category; }
    public int getFridgeDays() { return fridgeDays; }
    public String getUnit() { return unit; }
    public double getDefaultQty() { return defaultQty; }
    public String getColor() { return color; }
    public Integer getEachGram() { return eachGram; }
}
