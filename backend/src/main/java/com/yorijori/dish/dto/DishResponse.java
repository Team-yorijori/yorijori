package com.yorijori.dish.dto;

import com.yorijori.dish.Dish;

import java.time.LocalDate;
import java.util.List;

public record DishResponse(Long id, String recipeCode, String name, int servings, int left,
                           LocalDate made, LocalDate exp, long dday, List<String> colors, List<String> saved) {
    public static DishResponse of(Dish d, LocalDate today) {
        return new DishResponse(d.getId(), d.getRecipeCode(), d.getName(), d.getServings(), d.getServingsLeft(),
                d.getMadeDate(), d.getExpDate(), d.daysLeft(today), d.getColors(), d.getSaved());
    }
}
