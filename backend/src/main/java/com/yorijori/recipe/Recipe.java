package com.yorijori.recipe;

import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.List;

/**
 * 레시피 — 공공 레시피 537건(id 1~537, code r1~r537) + 데모 레시피(id 1001~, code kimchi-rice 등)
 * 화면과 주고받을 때는 code 를 쓴다 (데모 r.id 와 같은 값).
 */
@Entity
@Table(name = "recipe")
public class Recipe {

    @Id
    private Long id;

    @Column(nullable = false, unique = true, length = 40)
    private String code;

    @Column(nullable = false, length = 100)
    private String title;

    @Column(length = 500)
    private String description;

    @Column(name = "cook_time_min")
    private Integer cookTimeMin;

    @Column(length = 20)
    private String difficulty;

    private Integer servings;

    /** 밥 · 국 · 찌개/전골/스튜 · 볶음 … (공공데이터 분류) */
    @Column(length = 50)
    private String category;

    @Column(length = 30)
    private String cuisine;

    @Column(length = 20)
    private String kcal;

    @Column(length = 100)
    private String source;

    /** 대표 영상 (YouTube video id) — YoutubeVideoCollector 가 채운다 */
    @Column(name = "video_id", length = 20)
    private String videoId;

    /** 만든 요리 냉장 보관 일수(참고용) — 데모 v8 DISH_DAYS */
    @Column(name = "storage_days")
    private Integer storageDays;

    @Column(name = "image_url", length = 500)
    private String imageUrl;

    @OneToMany(mappedBy = "recipe", fetch = FetchType.LAZY)
    @OrderBy("sortNo ASC")
    private List<RecipeIngredient> ingredients = new ArrayList<>();

    @OneToMany(mappedBy = "recipe", fetch = FetchType.LAZY)
    @OrderBy("stepNo ASC")
    private List<RecipeStep> steps = new ArrayList<>();

    protected Recipe() {}

    public Long getId() { return id; }
    public String getCode() { return code; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public Integer getCookTimeMin() { return cookTimeMin; }
    public String getDifficulty() { return difficulty; }
    public Integer getServings() { return servings; }
    public String getCategory() { return category; }
    public String getCuisine() { return cuisine; }
    public String getKcal() { return kcal; }
    public String getSource() { return source; }
    public String getVideoId() { return videoId; }
    public Integer getStorageDays() { return storageDays; }
    public String getImageUrl() { return imageUrl; }
    public List<RecipeIngredient> getIngredients() { return ingredients; }
    public List<RecipeStep> getSteps() { return steps; }

    public void setVideoId(String videoId) { this.videoId = videoId; }

    /** 보관 일수 — 값이 없으면 이름으로 추정 (데모 dishDays) */
    public int storageDaysOrGuess() {
        if (storageDays != null) return storageDays;
        String n = title == null ? "" : title;
        if (n.matches(".*(찌개|국|탕|전골).*")) return 3;
        if (n.matches(".*(볶음밥|덮밥|스무디|샐러드).*")) return 1;
        if (n.matches(".*(조림|장아찌).*")) return 4;
        return 2;
    }
}
