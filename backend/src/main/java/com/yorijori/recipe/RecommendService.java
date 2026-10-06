package com.yorijori.recipe;

import com.yorijori.common.util.Hangul;
import com.yorijori.dish.CookingLogService;
import com.yorijori.fridge.FridgeService;
import com.yorijori.fridge.Stock;
import com.yorijori.recipe.dto.RecommendItem;
import com.yorijori.recipe.dto.RecommendPage;
import com.yorijori.user.User;
import com.yorijori.user.UserService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

/**
 * 레시피 추천 — 외부 생성형 AI 없이 레시피 DB + 점수 규칙 (데모 match / ranked 와 같은 계산)
 *
 *   점수 = 보유율 × 60 + 임박 가산점 − 최근 만듦 감점
 *   보유율        = 가진 필수 재료 수 / 필수 재료 수      (필수 재료가 없으면 전체 재료 기준)
 *   임박 가산점   = 쓰이는 재료 중 가장 임박한 것이 D-1 이하 +40 · D-3 이하 +25 · D-5 이하 +10
 *   최근 만듦 감점 = 2일 안에 만든 레시피 −15
 *   기본 양념(SEASONING)은 있는 것으로 본다.
 */
@Service
@Transactional(readOnly = true)
public class RecommendService {

    public static final String SORT_URGENT = "urgent";
    public static final String SORT_READY = "ready";

    private final RecipeCatalog catalog;
    private final FridgeService fridgeService;
    private final CookingLogService cookingLogService;
    private final UserService userService;

    public RecommendService(RecipeCatalog catalog, FridgeService fridgeService,
                            CookingLogService cookingLogService, UserService userService) {
        this.catalog = catalog;
        this.fridgeService = fridgeService;
        this.cookingLogService = cookingLogService;
        this.userService = userService;
    }

    public RecommendPage recommend(Long userId, String sort, String q, int page, int size) {
        Map<String, Stock> stock = fridgeService.stockMap(fridgeService.fridgeIdOf(userId));
        Map<String, Long> recent = cookingLogService.recentCookDays(userId);
        List<String> terms = userService.avoidTerms(userId);
        User user = userService.get(userId);

        List<RecommendItem> list = new ArrayList<>();
        for (Recipe r : catalog.all()) {
            RecommendItem m = match(r, stock, recent.get(r.getCode()), AvoidMatcher.hits(r, terms));
            if (m.ratio() <= 0) continue;
            if (q != null && !q.isBlank() && !matchesQuery(r, q.trim())) continue;
            list.add(m);
        }
        int total = list.size();
        int avoidCount = (int) list.stream().filter(m -> !m.avoid().isEmpty()).count();

        Comparator<RecommendItem> byScore = Comparator.comparingDouble(RecommendItem::score).reversed();
        Comparator<RecommendItem> byMissing = Comparator.comparingInt(m -> m.missing().size());
        list.sort(SORT_READY.equals(sort) ? byMissing.thenComparing(byScore) : byScore.thenComparing(byMissing));

        // 못 먹는 재료: 기본은 빼고, show 면 뒤로 보낸다
        List<RecommendItem> ok = list.stream().filter(m -> m.avoid().isEmpty()).toList();
        List<RecommendItem> bad = list.stream().filter(m -> !m.avoid().isEmpty()).toList();
        List<RecommendItem> ordered = new ArrayList<>(ok);
        if (user.isAvoidShow()) ordered.addAll(bad);

        int from = Math.min(page * size, ordered.size()), to = Math.min(from + size, ordered.size());
        return new RecommendPage(ordered.subList(from, to), page, size, user.isAvoidShow() ? total : total - avoidCount,
                catalog.all().size(), avoidCount, user.isAvoidShow());
    }

    /** 데모 match(r) */
    static RecommendItem match(Recipe r, Map<String, Stock> stock, Long recentDays, List<String> avoid) {
        List<RecipeIngredient> ings = r.getIngredients().stream().filter(i -> i.getType() != IngredientType.SEASONING).toList();
        List<RecipeIngredient> req0 = ings.stream().filter(i -> !i.isOptional()).toList();
        List<RecipeIngredient> req = req0.isEmpty() ? ings : req0;
        List<RecipeIngredient> opt = req0.isEmpty() ? List.of() : ings.stream().filter(RecipeIngredient::isOptional).toList();

        List<String> have = new ArrayList<>(), missing = new ArrayList<>();
        for (RecipeIngredient i : req) (has(stock, i) ? have : missing).add(i.getIngredientName());

        RecommendItem.Urgent urgent = null;
        for (RecipeIngredient i : ings) {
            Stock s = stock.get(i.getIngredientName());
            if (s == null || s.qty() <= 0) continue;
            if (urgent == null || s.soonest() < urgent.dday()) urgent = new RecommendItem.Urgent(s.name(), s.soonest());
        }
        double ratio = req.isEmpty() ? 0 : (double) have.size() / req.size();
        int bonus = urgent == null ? 0 : urgent.dday() <= 1 ? 40 : urgent.dday() <= 3 ? 25 : urgent.dday() <= 5 ? 10 : 0;
        int penalty = recentDays != null && recentDays <= 2 ? 15 : 0;
        double score = ratio * 60 + bonus - penalty;

        return new RecommendItem(r.getCode(), r.getTitle(), r.getCookTimeMin(), r.getDifficulty(), r.getCategory(),
                score, ratio, have, missing, opt.stream().map(RecipeIngredient::getIngredientName).toList(),
                urgent, recentDays, avoid);
    }

    private static boolean has(Map<String, Stock> stock, RecipeIngredient i) {
        Stock s = stock.get(i.getIngredientName());
        return s != null && s.qty() > 0;
    }

    /** 요리 이름 또는 재료 이름 (초성 가능) */
    private static boolean matchesQuery(Recipe r, String q) {
        if (Hangul.contains(r.getTitle(), q)) return true;
        return r.getIngredients().stream().anyMatch(i -> Hangul.contains(i.getIngredientName(), q));
    }
}
