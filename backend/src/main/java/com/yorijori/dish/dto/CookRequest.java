package com.yorijori.dish.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.PositiveOrZero;

import java.util.List;

/**
 * 요리 완료 (데모 openDeduct 창)
 * @param servings 만든 양 (인분) — 만든 요리에 보관
 * @param uses     실제로 쓴 재료와 양. 0 이면 차감하지 않는다. 비어 있으면 차감 없이 보관만
 */
public record CookRequest(@Min(1) @Max(20) int servings, List<@Valid Use> uses) {
    public record Use(@NotBlank String name, @PositiveOrZero double qty) {}
}
