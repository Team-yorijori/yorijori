package com.yorijori.cart;

import jakarta.persistence.*;
import com.yorijori.ingredient.Ingredient;

import java.time.LocalDateTime;

/** 재료별·쇼핑몰별 가격 이력 — "최근 30일 중 가장 쌀 때" 판단과 그래프용 */
@Entity
@Table(name = "price_history")
public class PriceHistory {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "ingredient_name", nullable = false, length = 50)
    private String ingredientName;

    /** NAVER · COUPANG(승인 후) */
    @Column(nullable = false, length = 20)
    private String channel;

    /** 판매처 (네이버 쇼핑 mallName) */
    @Column(name = "mall_name", length = 50)
    private String mallName;

    @Column(nullable = false)
    private int price;

    @Column(name = "product_title", length = 300)
    private String productTitle;

    @Column(name = "product_url", length = 500)
    private String productUrl;

    @Column(name = "checked_at", nullable = false)
    private LocalDateTime checkedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ingredient_id")
    private Ingredient ingredient;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    private Product product;

    public void link(Ingredient ingredient, Product product) {
        this.ingredient = ingredient;
        this.product = product;
    }

    protected PriceHistory() {}

    public PriceHistory(String ingredientName, String channel, String mallName, int price,
                        String productTitle, String productUrl, LocalDateTime checkedAt) {
        this.ingredientName = ingredientName;
        this.channel = channel;
        this.mallName = mallName;
        this.price = price;
        this.productTitle = productTitle;
        this.productUrl = productUrl;
        this.checkedAt = checkedAt;
    }

    public String getIngredientName() { return ingredientName; }
    public String getChannel() { return channel; }
    public String getMallName() { return mallName; }
    public int getPrice() { return price; }
    public String getProductTitle() { return productTitle; }
    public String getProductUrl() { return productUrl; }
    public LocalDateTime getCheckedAt() { return checkedAt; }
}
