package com.yorijori.fridge;

import com.yorijori.ingredient.Ingredient;
import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

/**
 * 냉장고 속 재료 한 묶음 — 데모의 { id, name, qty, unit, reg, exp, auto }
 * 같은 재료를 여러 번 사면 행이 여러 개다 (소비기한이 다르므로). 차감은 소비기한이 가까운 행부터.
 */
@Entity
@Table(name = "fridge_item")
public class FridgeItem {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "fridge_id", nullable = false)
    private Long fridgeId;

    /** 기준표에 없는 재료면 null */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ingredient_id")
    private Ingredient ingredient;

    /** 표준 이름 (기준표에 없으면 사용자가 쓴 이름) */
    @Column(nullable = false, length = 50)
    private String name;

    @Column(nullable = false)
    private double qty;

    @Column(nullable = false, length = 10)
    private String unit;

    @Column(name = "reg_date", nullable = false)
    private LocalDate regDate;

    @Column(name = "exp_date", nullable = false)
    private LocalDate expDate;

    /** true: 보관 일수로 계산한 참고용 날짜 / false: 사용자가 직접 넣은 날짜 */
    @Column(name = "exp_auto", nullable = false)
    private boolean expAuto;

    /** 등록 경로: MANUAL · SCAN · RECEIPT · CART */
    @Column(nullable = false, length = 10)
    private String source;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    protected FridgeItem() {}

    public FridgeItem(Long fridgeId, Ingredient ingredient, String name, double qty, String unit,
                      LocalDate regDate, LocalDate expDate, boolean expAuto, String source) {
        this.fridgeId = fridgeId;
        this.ingredient = ingredient;
        this.name = name;
        this.qty = qty;
        this.unit = unit;
        this.regDate = regDate;
        this.expDate = expDate;
        this.expAuto = expAuto;
        this.source = source;
    }

    /** 오늘 기준 남은 일수 (지났으면 음수) */
    public long daysLeft(LocalDate today) {
        return ChronoUnit.DAYS.between(today, expDate);
    }

    /** need 만큼 빼고, 실제로 뺀 양을 돌려준다 */
    public double take(double need) {
        double before = qty;
        double t = Math.min(qty, Math.max(0, need));
        qty = Math.max(0, Math.round((qty - t) * 100) / 100.0);
        return Math.max(0, before - qty);
    }

    public void changeQty(double qty) { this.qty = Math.max(0, Math.round(qty * 100) / 100.0); }
    public void changeExp(LocalDate expDate, boolean auto) { this.expDate = expDate; this.expAuto = auto; }

    public Long getId() { return id; }
    public Long getFridgeId() { return fridgeId; }
    public Ingredient getIngredient() { return ingredient; }
    public String getName() { return name; }
    public double getQty() { return qty; }
    public String getUnit() { return unit; }
    public LocalDate getRegDate() { return regDate; }
    public LocalDate getExpDate() { return expDate; }
    public boolean isExpAuto() { return expAuto; }
    public String getSource() { return source; }
}
