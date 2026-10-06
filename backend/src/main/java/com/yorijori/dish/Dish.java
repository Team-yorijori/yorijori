package com.yorijori.dish;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;

/**
 * 만든 요리 (데모 v8) — { id, rid, name, serv, left, made, exp, colors[], saved[] }
 * 냉장고 단위로 보관한다 (가족이 같이 먹을 수 있게).
 */
@Entity
@Table(name = "dish")
public class Dish {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "fridge_id", nullable = false)
    private Long fridgeId;

    @Column(name = "recipe_id")
    private Long recipeId;

    @Column(name = "recipe_code", length = 40)
    private String recipeCode;

    @Column(nullable = false, length = 100)
    private String name;

    /** 만든 인분 */
    @Column(nullable = false)
    private int servings;

    /** 남은 인분 */
    @Column(name = "servings_left", nullable = false)
    private int servingsLeft;

    @Column(name = "made_date", nullable = false)
    private LocalDate madeDate;

    /** 보관 기한 (참고용) */
    @Column(name = "exp_date", nullable = false)
    private LocalDate expDate;

    /** 접시 그림 색 (쉼표 구분) */
    @Column(length = 100)
    private String colors;

    /** 이 요리로 살린 임박 재료 (쉼표 구분) */
    @Column(name = "saved_names", length = 500)
    private String savedNames;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    protected Dish() {}

    public Dish(Long fridgeId, Long recipeId, String recipeCode, String name, int servings,
                LocalDate madeDate, LocalDate expDate, List<String> colors, List<String> saved) {
        this.fridgeId = fridgeId;
        this.recipeId = recipeId;
        this.recipeCode = recipeCode;
        this.name = name;
        this.servings = servings;
        this.servingsLeft = servings;
        this.madeDate = madeDate;
        this.expDate = expDate;
        this.colors = String.join(",", colors);
        this.savedNames = String.join(",", saved);
    }

    /** 1인분 먹기. 남은 인분을 돌려준다 */
    public int eatOne() {
        servingsLeft = Math.max(0, servingsLeft - 1);
        return servingsLeft;
    }

    public long daysLeft(LocalDate today) { return ChronoUnit.DAYS.between(today, expDate); }

    public Long getId() { return id; }
    public Long getFridgeId() { return fridgeId; }
    public Long getRecipeId() { return recipeId; }
    public String getRecipeCode() { return recipeCode; }
    public String getName() { return name; }
    public int getServings() { return servings; }
    public int getServingsLeft() { return servingsLeft; }
    public LocalDate getMadeDate() { return madeDate; }
    public LocalDate getExpDate() { return expDate; }
    public List<String> getColors() { return split(colors); }
    public List<String> getSaved() { return split(savedNames); }

    private static List<String> split(String s) {
        return s == null || s.isBlank() ? List.of() : Arrays.asList(s.split(","));
    }
}
