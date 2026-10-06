package com.yorijori.dish;

import com.yorijori.common.exception.ApiException;
import com.yorijori.common.exception.ErrorCode;
import com.yorijori.common.util.Hangul;
import com.yorijori.dish.dto.CookRequest;
import com.yorijori.dish.dto.CookResult;
import com.yorijori.dish.dto.DishResponse;
import com.yorijori.fridge.FridgeService;
import com.yorijori.fridge.Stock;
import com.yorijori.recipe.Recipe;
import com.yorijori.recipe.RecipeIngredient;
import com.yorijori.recipe.RecipeService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.*;

@Service
@Transactional(readOnly = true)
public class DishService {

    /** 임박 재료 기준 (D-3 이내를 쓰면 "살렸다") */
    private static final int SAVED_DAYS = 3;
    private static final List<String> FALLBACK_COLORS = List.of("#F3A46C", "#9CCB6B", "#F7C948");

    private final DishRepository dishes;
    private final CookingLogRepository logs;
    private final FridgeService fridgeService;
    private final RecipeService recipeService;

    public DishService(DishRepository dishes, CookingLogRepository logs, FridgeService fridgeService, RecipeService recipeService) {
        this.dishes = dishes;
        this.logs = logs;
        this.fridgeService = fridgeService;
        this.recipeService = recipeService;
    }

    public List<DishResponse> list(Long userId) {
        LocalDate today = fridgeService.today();
        return dishes.findByFridgeIdOrderByExpDateAscIdAsc(fridgeService.fridgeIdOf(userId)).stream()
                .map(d -> DishResponse.of(d, today)).toList();
    }

    /** 요리 완료: 재료 차감(임박한 것부터) → 만든 요리 보관 → 기록 */
    @Transactional
    public CookResult cook(Long userId, String recipeCode, CookRequest req) {
        Recipe r = recipeService.get(recipeCode);
        Long fridgeId = fridgeService.fridgeIdOf(userId);
        LocalDate today = fridgeService.today();
        Map<String, Stock> before = fridgeService.stockMap(fridgeId);

        // 1) 차감 — 그 재료의 당시 남은 일수를 같이 기록한다
        record Used(String name, double qty, long daysLeft) {}
        List<Used> used = new ArrayList<>();
        List<String> saved = new ArrayList<>();
        for (CookRequest.Use u : Optional.ofNullable(req.uses()).orElse(List.of())) {
            if (u.qty() <= 0) continue;
            Stock s = before.get(u.name());
            if (s == null) continue;
            double taken = fridgeService.deduct(fridgeId, u.name(), u.qty());
            if (taken <= 0) continue;
            used.add(new Used(u.name(), taken, s.soonest()));
            if (s.soonest() <= SAVED_DAYS) saved.add(u.name());
        }
        int deducted = used.size();

        // 2) 만든 요리 보관
        Dish dish = dishes.save(new Dish(fridgeId, r.getId(), r.getCode(), r.getTitle(), req.servings(),
                today, today.plusDays(r.storageDaysOrGuess()), colorsOf(r), saved));

        // 3) 기록
        CookingLog log = CookingLog.cook(userId, r.getCode(), dish.getId(), r.getTitle(), req.servings(), saved, today);
        used.forEach(u -> log.addIngredient(u.name(), u.qty(), u.daysLeft()));
        logs.save(log);

        String msg = r.getTitle() + " " + req.servings() + "인분을 만든 요리에 보관했습니다"
                + (deducted > 0 ? " · 재료 " + deducted + "종 차감" : "")
                + (saved.isEmpty() ? "" : " · 임박 재료 " + saved.size() + "개 살림");
        return new CookResult(DishResponse.of(dish, today), deducted, saved, msg);
    }

    @Transactional
    public DishResponse eat(Long userId, Long dishId) {
        Dish d = find(userId, dishId);
        int left = d.eatOne();
        logs.save(CookingLog.eat(userId, d.getRecipeCode(), d.getId(), d.getName(), fridgeService.today()));
        if (left <= 0) { dishes.delete(d); return null; }
        return DishResponse.of(d, fridgeService.today());
    }

    @Transactional
    public String toss(Long userId, Long dishId) {
        Dish d = find(userId, dishId);
        logs.save(CookingLog.toss(userId, d.getRecipeCode(), d.getId(), d.getName(), d.getServingsLeft(), fridgeService.today()));
        dishes.delete(d);
        return d.getName() + " " + d.getServingsLeft() + "인분을 버렸습니다.";
    }

    public String eatMessage(String name, DishResponse after) {
        return after == null ? Hangul.josa(name, "을", "를") + " 다 먹었습니다"
                : name + " 1인분을 먹었습니다 · " + after.left() + "인분 남음";
    }

    private Dish find(Long userId, Long dishId) {
        return dishes.findByIdAndFridgeId(dishId, fridgeService.fridgeIdOf(userId))
                .orElseThrow(() -> new ApiException(ErrorCode.DISH_NOT_FOUND));
    }

    /** 접시 색: 재료 기준표 색 최대 5개 (데모 dishColors) */
    private static List<String> colorsOf(Recipe r) {
        LinkedHashSet<String> c = new LinkedHashSet<>();
        for (RecipeIngredient i : r.getIngredients()) {
            if (i.getIngredient() != null && i.getIngredient().getColor() != null) c.add(i.getIngredient().getColor());
            if (c.size() == 5) break;
        }
        List<String> out = new ArrayList<>(c);
        while (out.size() < 3) out.add(FALLBACK_COLORS.get(out.size()));
        return out;
    }
}
