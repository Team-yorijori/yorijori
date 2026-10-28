package com.yorijori.dish;

import jakarta.persistence.*;

/** 요리할 때 쓴 재료와 그때 남은 소비기한 일수 — "임박 재료를 얼마나 살렸나" 분석용 */
@Entity
@Table(name = "cooking_log_ingredient")
public class CookingLogIngredient {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "log_id")
    private CookingLog log;

    @Column(name = "ingredient_name", nullable = false, length = 50)
    private String ingredientName;

    @Column(name="ingredient_id")
    private Long ingredientId;

    @Column(nullable = false)
    private double qty;

    @Column(name = "days_left")
    private Long daysLeft;

    protected CookingLogIngredient() {}

    CookingLogIngredient(CookingLog log, String ingredientName, double qty, Long daysLeft, Long ingredientId) {
        this.log = log;
        this.ingredientName = ingredientName;
        this.ingredientId = ingredientId;
        this.qty = qty;
        this.daysLeft = daysLeft;
    }

    public String getIngredientName() { return ingredientName; }
    public double getQty() { return qty; }
    public Long getDaysLeft() { return daysLeft; }
}
