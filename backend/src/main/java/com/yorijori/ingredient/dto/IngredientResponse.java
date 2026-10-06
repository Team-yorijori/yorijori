package com.yorijori.ingredient.dto;

import com.yorijori.ingredient.Ingredient;

public record IngredientResponse(Long id, String name, String category, int fridgeDays, String unit,
                                 double defaultQty, String color) {
    public static IngredientResponse of(Ingredient i) {
        return new IngredientResponse(i.getId(), i.getName(), i.getCategory(), i.getFridgeDays(), i.getUnit(),
                i.getDefaultQty(), i.getColor());
    }
}
