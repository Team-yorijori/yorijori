package com.yorijori.dish;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * 요리 기록 (데모 v8 log) — { t: cook|eat|toss|tossIng, name, rid?, n?, saved?, d }
 * 이번 달 통계, "다시 만들기", 최근 만든 요리 감점, 재학습·분석에 쓴다.
 */
@Entity
@Table(name = "cooking_log")
public class CookingLog {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private LogKind kind;

    @Column(name = "recipe_code", length = 40)
    private String recipeCode;

    @Column(name = "dish_id")
    private Long dishId;

    @Column(nullable = false, length = 100)
    private String name;

    /** 인분(COOK·EAT·TOSS) 또는 재료 수량(TOSS_ING) */
    @Column(nullable = false)
    private double amount;

    /** COOK: 살린 임박 재료 (쉼표 구분) */
    @Column(name = "saved_names", length = 500)
    private String savedNames;

    @Column(name = "log_date", nullable = false)
    private LocalDate logDate;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "log", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<CookingLogIngredient> ingredients = new ArrayList<>();

    protected CookingLog() {}

    private CookingLog(Long userId, LogKind kind, String recipeCode, Long dishId, String name, double amount, String saved, LocalDate date) {
        this.userId = userId;
        this.kind = kind;
        this.recipeCode = recipeCode;
        this.dishId = dishId;
        this.name = name;
        this.amount = amount;
        this.savedNames = saved;
        this.logDate = date;
    }

    public static CookingLog cook(Long userId, String recipeCode, Long dishId, String name, int servings, List<String> saved, LocalDate date) {
        return new CookingLog(userId, LogKind.COOK, recipeCode, dishId, name, servings, String.join(",", saved), date);
    }
    public static CookingLog eat(Long userId, String recipeCode, Long dishId, String name, LocalDate date) {
        return new CookingLog(userId, LogKind.EAT, recipeCode, dishId, name, 1, null, date);
    }
    public static CookingLog toss(Long userId, String recipeCode, Long dishId, String name, int servingsLeft, LocalDate date) {
        return new CookingLog(userId, LogKind.TOSS, recipeCode, dishId, name, servingsLeft, null, date);
    }
    public static CookingLog tossIngredient(Long userId, String name, double qty, LocalDate date) {
        return new CookingLog(userId, LogKind.TOSS_ING, null, null, name, qty, null, date);
    }

    public void addIngredient(String name, double qty, Long daysLeft) {
        ingredients.add(new CookingLogIngredient(this, name, qty, daysLeft));
    }

    public Long getId() { return id; }
    public Long getUserId() { return userId; }
    public LogKind getKind() { return kind; }
    public String getRecipeCode() { return recipeCode; }
    public Long getDishId() { return dishId; }
    public String getName() { return name; }
    public double getAmount() { return amount; }
    public List<String> getSaved() {
        return savedNames == null || savedNames.isBlank() ? List.of() : Arrays.asList(savedNames.split(","));
    }
    public LocalDate getLogDate() { return logDate; }
    public List<CookingLogIngredient> getIngredients() { return ingredients; }
}
