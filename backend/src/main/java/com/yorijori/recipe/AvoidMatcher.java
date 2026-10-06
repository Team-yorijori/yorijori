package com.yorijori.recipe;

import java.util.List;

/**
 * v9 못 먹는 재료 — 레시피 재료 이름·원래 표기·기본 양념까지 글자 포함으로 확인한다 (데모 avoidHits)
 * 예: 대두 묶음 → "간장"이 기본 양념에 있으면 걸린다.
 */
public final class AvoidMatcher {

    private AvoidMatcher() {}

    public static List<String> hits(Recipe r, List<String> terms) {
        if (terms == null || terms.isEmpty()) return List.of();
        StringBuilder sb = new StringBuilder();
        for (RecipeIngredient i : r.getIngredients()) {
            sb.append(i.getIngredientName()).append(' ');
            if (i.getAmountText() != null) sb.append(i.getAmountText());
            sb.append(" | ");
        }
        String text = sb.toString();
        return terms.stream().filter(text::contains).toList();
    }
}
