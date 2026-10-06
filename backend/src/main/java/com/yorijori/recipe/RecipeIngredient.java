package com.yorijori.recipe;

import com.yorijori.ingredient.Ingredient;
import jakarta.persistence.*;

/** 레시피 재료 — 데모 ings: [표준 재료명, 냉장고 단위 수량, 선택(1)/필수(0), 원래 표기] */
@Entity
@Table(name = "recipe_ingredient")
public class RecipeIngredient {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "recipe_id")
    private Recipe recipe;

    /** 기준표에 있는 재료면 연결 (없으면 null, 이름으로만 매칭) */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ingredient_id")
    private Ingredient ingredient;

    /** 표준 재료명 — 냉장고 재료와 이 이름으로 매칭한다 */
    @Column(name = "ingredient_name", nullable = false, length = 50)
    private String ingredientName;

    /** 냉장고 단위로 환산한 수량 (차감 기본값) */
    private Double amount;

    /** 원래 표기 (예: "안심 200g · 양지머리 100g") */
    @Column(name = "amount_text", length = 200)
    private String amountText;

    @Enumerated(EnumType.STRING)
    @Column(name = "ingredient_type", nullable = false, length = 10)
    private IngredientType type;

    @Column(name = "is_optional", nullable = false)
    private boolean optional;

    @Column(name = "sort_no", nullable = false)
    private int sortNo;

    protected RecipeIngredient() {}

    public Long getId() { return id; }
    public Recipe getRecipe() { return recipe; }
    public Ingredient getIngredient() { return ingredient; }
    public String getIngredientName() { return ingredientName; }
    public Double getAmount() { return amount; }
    public String getAmountText() { return amountText; }
    public IngredientType getType() { return type; }
    public boolean isOptional() { return optional; }
    public int getSortNo() { return sortNo; }
}
