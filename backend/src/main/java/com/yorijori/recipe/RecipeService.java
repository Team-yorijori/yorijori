package com.yorijori.recipe;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.yorijori.common.exception.ApiException;
import com.yorijori.common.exception.ErrorCode;
import com.yorijori.fridge.FridgeService;
import com.yorijori.fridge.Stock;
import com.yorijori.recipe.dto.RecipeDetail;
import com.yorijori.user.UserService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
@Transactional(readOnly = true)
public class RecipeService {

    private final RecipeCatalog catalog;
    private final FridgeService fridgeService;
    private final UserService userService;
    private final ObjectMapper om;
    private volatile String dataJson;

    public RecipeService(RecipeCatalog catalog, FridgeService fridgeService, UserService userService, ObjectMapper om) {
        this.catalog = catalog;
        this.fridgeService = fridgeService;
        this.userService = userService;
        this.om = om;
    }

    public Recipe get(String code) {
        return catalog.find(code).orElseThrow(() -> new ApiException(ErrorCode.RECIPE_NOT_FOUND));
    }

    /** 상세. userId 가 null(로그인 전)이면 보유 상태 없이 */
    public RecipeDetail detail(String code, Long userId) {
        Recipe r = get(code);
        Map<String, Stock> stock = userId == null ? Map.of() : fridgeService.stockMap(fridgeService.fridgeIdOf(userId));
        List<String> avoid = userId == null ? List.of() : AvoidMatcher.hits(r, userService.avoidTerms(userId));

        List<RecipeDetail.Ing> ings = new ArrayList<>();
        List<String> seasonings = new ArrayList<>();
        for (RecipeIngredient i : r.getIngredients()) {
            if (i.getType() == IngredientType.SEASONING) {
                seasonings.add(i.getAmountText() != null ? i.getAmountText() : i.getIngredientName());
                continue;
            }
            Stock s = stock.get(i.getIngredientName());
            double have = s == null ? 0 : s.qty();
            String status = i.isOptional() ? "OPTIONAL"
                    : have <= 0 ? "MISSING"
                    : i.getAmount() != null && have < i.getAmount() ? "LOW" : "HAVE";
            String unit = i.getIngredient() == null ? null : i.getIngredient().getUnit();
            ings.add(new RecipeDetail.Ing(i.getIngredientName(), i.getAmountText(), i.getAmount(), unit, i.isOptional(), status, have));
        }
        return new RecipeDetail(r.getCode(), r.getTitle(), r.getDescription(), r.getCookTimeMin(), r.getDifficulty(),
                r.getServings(), r.getCategory(), r.getCuisine(), r.getKcal(), r.getSource(), r.getVideoId(),
                r.storageDaysOrGuess(), ings, seasonings,
                r.getSteps().stream().map(RecipeStep::getContent).toList(), avoid);
    }

    /**
     * 데모 v9 의 recipeData 형식 JSON — 화면 JS(static/js/data.js)가 그대로 읽는다.
     * { id, name, time, diff, serv, ings: [[이름, 수량, 선택(1/0), 원래 표기]], steps, summary, type, nation, kcal, pantry, src, video }
     * TODO(프론트·백) 화면을 API 방식으로 다 옮기면 이 통째 JSON 대신 /api/recipes/recommend 를 쓴다.
     */
    public String recipeDataJson() {
        if (dataJson == null) {
            List<Map<String, Object>> out = new ArrayList<>();
            for (Recipe r : catalog.all()) {
                Map<String, Object> m = new LinkedHashMap<>();
                m.put("id", r.getCode());
                m.put("name", r.getTitle());
                m.put("time", r.getCookTimeMin());
                m.put("diff", r.getDifficulty());
                m.put("serv", r.getServings());
                List<List<Object>> ings = new ArrayList<>();
                List<String> pantry = new ArrayList<>();
                for (RecipeIngredient i : r.getIngredients()) {
                    if (i.getType() == IngredientType.SEASONING) {
                        pantry.add(i.getAmountText() != null ? i.getAmountText() : i.getIngredientName());
                        continue;
                    }
                    List<Object> row = new ArrayList<>(List.of(i.getIngredientName(),
                            i.getAmount() == null ? 1 : i.getAmount(), i.isOptional() ? 1 : 0));
                    if (i.getAmountText() != null) row.add(i.getAmountText());
                    ings.add(row);
                }
                m.put("ings", ings);
                m.put("steps", r.getSteps().stream().map(RecipeStep::getContent).toList());
                if (r.getDescription() != null) m.put("summary", r.getDescription());
                if (r.getCategory() != null) m.put("type", r.getCategory());
                if (r.getCuisine() != null) m.put("nation", r.getCuisine());
                if (r.getKcal() != null) m.put("kcal", r.getKcal());
                if (!pantry.isEmpty()) m.put("pantry", pantry);
                if (r.getSource() != null) m.put("src", r.getSource());
                if (r.getVideoId() != null) m.put("video", r.getVideoId());
                if (r.getStorageDays() != null) m.put("keep", r.getStorageDays());
                out.add(m);
            }
            try {
                // </script> 가 들어가지 않도록 < 를 이스케이프한다 (th:utext 로 그대로 넣으므로)
                dataJson = om.writeValueAsString(out).replace("<", "\\u003c");
            } catch (JsonProcessingException e) {
                throw new IllegalStateException(e);
            }
        }
        return dataJson;
    }

    /** 영상 ID 를 모은 뒤 등 기준 데이터가 바뀌면 */
    public void evict() {
        catalog.reload();
        dataJson = null;
    }
}
