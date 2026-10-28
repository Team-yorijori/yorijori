package com.yorijori.cart;

import com.yorijori.ingredient.Ingredient;
import jakarta.persistence.*;
import java.math.BigDecimal;

/** 외부 채널의 안정적인 상품 ID. 가격은 별도 이력으로 보존한다. */
@Entity
@Table(name = "product", uniqueConstraints = @UniqueConstraint(columnNames = {"channel", "external_id"}))
public class Product {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false, length = 20)
    private String channel;
    @Column(name = "external_id", nullable = false, length = 100)
    private String externalId;
    @Column(nullable = false, length = 300)
    private String title;
    @Column(name = "product_url", length = 500)
    private String productUrl;
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ingredient_id")
    private Ingredient ingredient;
    @Column(name = "package_qty", precision = 12, scale = 3)
    private BigDecimal packageQty;
    @Column(name = "package_unit", length = 20)
    private String packageUnit;

    protected Product() {}

    public Product(String channel, String externalId, String title, String productUrl, Ingredient ingredient) {
        this.channel = channel;
        this.externalId = externalId;
        this.title = title;
        this.productUrl = productUrl;
        this.ingredient = ingredient;
    }

    public void observe(String title, String url, Ingredient resolved) {
        this.title = title;
        this.productUrl = url;
        // 같은 외부 상품이 다른 검색어에 등장해도 기존 재료 연결을 덮어쓰지 않는다.
        if (ingredient == null && resolved != null) ingredient = resolved;
    }

    public Long getId() { return id; }
    public Ingredient getIngredient() { return ingredient; }
}
