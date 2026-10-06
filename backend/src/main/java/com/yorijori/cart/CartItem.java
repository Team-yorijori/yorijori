package com.yorijori.cart;

import com.yorijori.ingredient.Ingredient;
import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/** 장보기 목록 (데모 v6) — 목표가, 알림 여부, 마지막으로 확인한 최저가 */
@Entity
@Table(name = "cart_item")
public class CartItem {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ingredient_id")
    private Ingredient ingredient;

    @Column(nullable = false, length = 50)
    private String name;

    /** 사고 싶은 가격 (원) */
    @Column(name = "target_price")
    private Integer targetPrice;

    /** 목표가 알림 받기 */
    @Column(name = "notify", nullable = false)
    private boolean alert = true;

    @Column(name = "lowest_price")
    private Integer lowestPrice;

    @Column(name = "lowest_shop", length = 30)
    private String lowestShop;

    @Column(name = "lowest_url", length = 500)
    private String lowestUrl;

    @Column(name = "lowest_checked_at")
    private LocalDateTime lowestCheckedAt;

    /** 같은 최저가로 알림을 두 번 보내지 않으려고 */
    @Column(name = "notified_price")
    private Integer notifiedPrice;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    protected CartItem() {}

    public CartItem(Long userId, Ingredient ingredient, String name, Integer targetPrice) {
        this.userId = userId;
        this.ingredient = ingredient;
        this.name = name;
        this.targetPrice = targetPrice;
    }

    public void updateLowest(int price, String shop, String url, LocalDateTime at) {
        this.lowestPrice = price;
        this.lowestShop = shop;
        this.lowestUrl = url;
        this.lowestCheckedAt = at;
    }

    /** 목표가 이하로 내려왔고 아직 이 가격으로 알리지 않았으면 true */
    public boolean shouldNotify() {
        return alert && targetPrice != null && lowestPrice != null && lowestPrice <= targetPrice
                && (notifiedPrice == null || lowestPrice < notifiedPrice);
    }

    public void markNotified() { this.notifiedPrice = lowestPrice; }
    public void setTargetPrice(Integer targetPrice) { this.targetPrice = targetPrice; this.notifiedPrice = null; }
    public void setAlert(boolean alert) { this.alert = alert; }

    public Long getId() { return id; }
    public Long getUserId() { return userId; }
    public Ingredient getIngredient() { return ingredient; }
    public String getName() { return name; }
    public Integer getTargetPrice() { return targetPrice; }
    public boolean isAlert() { return alert; }
    public Integer getLowestPrice() { return lowestPrice; }
    public String getLowestShop() { return lowestShop; }
    public String getLowestUrl() { return lowestUrl; }
    public LocalDateTime getLowestCheckedAt() { return lowestCheckedAt; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
