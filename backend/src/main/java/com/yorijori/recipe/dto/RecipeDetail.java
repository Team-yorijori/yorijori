package com.yorijori.recipe.dto;

import java.util.List;

/** 레시피 상세 — 재료마다 보유 상태(HAVE · LOW · MISSING · OPTIONAL) */
public record RecipeDetail(String code, String title, String description, Integer cookTimeMin, String difficulty,
                           Integer servings, String category, String cuisine, String kcal, String source,
                           String videoId, int storageDays, List<Ing> ingredients, List<String> seasonings,
                           List<String> steps, List<String> avoid) {

    public record Ing(String name, String amountText, Double amount, String unit, boolean optional,
                      String status, double have) {}
}
