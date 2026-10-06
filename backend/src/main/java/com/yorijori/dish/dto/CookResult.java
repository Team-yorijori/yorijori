package com.yorijori.dish.dto;

import java.util.List;

/** @param deducted 차감한 재료 종류 수 · @param saved 살린 임박 재료(D-3 이내) */
public record CookResult(DishResponse dish, int deducted, List<String> saved, String message) {}
