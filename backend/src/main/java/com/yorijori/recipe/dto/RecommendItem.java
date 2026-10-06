package com.yorijori.recipe.dto;

import java.util.List;

/**
 * 추천 목록 한 줄 (데모 match() 결과)
 * @param score   보유율×60 + 임박 가산점 − 최근 만듦 감점
 * @param urgent  이 레시피에 쓰이는 재료 중 가장 임박한 것 (없으면 null)
 * @param recent  최근에 만든 지 며칠 (안 만들었으면 null)
 * @param avoid   못 먹는 재료 (v9)
 */
public record RecommendItem(String code, String title, Integer cookTimeMin, String difficulty, String category,
                            double score, double ratio, List<String> have, List<String> missing, List<String> optional,
                            Urgent urgent, Long recent, List<String> avoid) {

    public record Urgent(String name, long dday) {}
}
