package com.yorijori.recipe.dto;

import java.util.List;

/**
 * @param total       만들 수 있는(보유 재료가 하나라도 있는) 레시피 수
 * @param avoidHidden 못 먹는 재료 때문에 뺀(또는 표시한) 레시피 수
 */
public record RecommendPage(List<RecommendItem> items, int page, int size, int total, int recipeCount,
                            int avoidHidden, boolean avoidShow) {}
