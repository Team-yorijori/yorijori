package com.yorijori.ingredient;

import com.yorijori.common.util.Hangul;
import com.yorijori.ingredient.dto.IngredientResponse;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Comparator;
import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
public class IngredientService {

    /** 기준표에 없는 재료의 기본 보관일수 (데모와 같다) */
    public static final int UNKNOWN_DAYS = 7;

    private final IngredientRepository ingredients;
    private final IngredientAliasRepository aliases;

    public IngredientService(IngredientRepository ingredients, IngredientAliasRepository aliases) {
        this.ingredients = ingredients;
        this.aliases = aliases;
    }

    /**
     * 자동완성. q 가 비어 있으면 전체.
     * 초성 검색 지원 (ㅇㅍ → 양파). 앞에서 맞는 것 → 중간에서 맞는 것 순서.
     */
    public List<IngredientResponse> search(String q) {
        List<Ingredient> all = ingredients.findAll();
        if (q == null || q.isBlank()) return all.stream().map(IngredientResponse::of).toList();
        String k = q.trim();
        return all.stream()
                .filter(i -> Hangul.contains(i.getName(), k))
                .sorted(Comparator.comparingInt((Ingredient i) -> Hangul.indexOf(i.getName(), k))
                        .thenComparingInt(i -> i.getName().length()))
                .limit(20)
                .map(IngredientResponse::of).toList();
    }

    /** 이름 → 표준 재료. 기준표 이름이 먼저, 없으면 동의어. 둘 다 없으면 empty */
    public Optional<Ingredient> resolve(String name) {
        if (name == null || name.isBlank()) return Optional.empty();
        String n = name.trim();
        return ingredients.findByName(n).or(() -> aliases.findByAlias(n).map(IngredientAlias::getIngredient));
    }

    /** 표준 이름 (기준표에 없으면 입력 그대로) */
    public String canonicalName(String name) {
        return resolve(name).map(Ingredient::getName).orElse(name == null ? "" : name.trim());
    }
}
