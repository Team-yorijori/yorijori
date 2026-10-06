package com.yorijori.ingredient;

import jakarta.persistence.*;

/**
 * 동의어·상품명 표기 → 표준 재료 (달걀 → 계란, 한돈 삼겹살 → 돼지고기)
 * source: SYNONYM(일반 동의어) / RECEIPT(영수증 상품명 규칙, 데모 RC_ALIAS)
 */
@Entity
@Table(name = "ingredient_alias")
public class IngredientAlias {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "ingredient_id")
    private Ingredient ingredient;

    @Column(nullable = false, unique = true, length = 100)
    private String alias;

    @Column(nullable = false, length = 10)
    private String source;

    protected IngredientAlias() {}

    public Long getId() { return id; }
    public Ingredient getIngredient() { return ingredient; }
    public String getAlias() { return alias; }
    public String getSource() { return source; }
}
