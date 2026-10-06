package com.yorijori.recipe;

import org.springframework.stereotype.Component;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * 레시피는 기준 데이터라 바뀌지 않으므로 처음 한 번 불러와 메모리에 둔다 (560건, 수 MB).
 * 추천 점수는 요청마다 이 목록 전체로 계산한다 — 데모와 같은 방식.
 * seed SQL 이 바뀌거나 영상 ID 를 수집한 뒤에는 reload() 한다.
 * TODO(백) 레시피가 수만 건이 되면 후보를 SQL 로 먼저 줄이고(보유 재료가 들어간 레시피만) 점수를 계산한다.
 */
@Component
public class RecipeCatalog {

    private final RecipeRepository recipes;
    private final TransactionTemplate tx;
    private volatile List<Recipe> all;
    private volatile Map<String, Recipe> byCode;

    public RecipeCatalog(RecipeRepository recipes, PlatformTransactionManager tm) {
        this.recipes = recipes;
        this.tx = new TransactionTemplate(tm);
        this.tx.setReadOnly(true);
    }

    public synchronized void reload() {
        List<Recipe> list = tx.execute(s -> {
            List<Recipe> l = recipes.findAllWithIngredients();
            l.forEach(r -> r.getSteps().size());     // 조리 순서도 미리 불러 둔다 (트랜잭션 밖에서 쓰므로)
            return l;
        });
        all = List.copyOf(list);
        byCode = all.stream().collect(Collectors.toUnmodifiableMap(Recipe::getCode, Function.identity()));
    }

    public List<Recipe> all() {
        if (all == null) reload();
        return all;
    }

    public Optional<Recipe> find(String code) {
        if (byCode == null) reload();
        return Optional.ofNullable(byCode.get(code));
    }
}
