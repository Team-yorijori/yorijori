package com.yorijori.recipe;

import com.yorijori.common.response.ApiResponse;
import com.yorijori.common.security.LoginUser;
import com.yorijori.recipe.dto.RecipeDetail;
import com.yorijori.recipe.dto.RecommendPage;
import org.springframework.http.MediaType;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

/**
 * GET /api/recipes/recommend?sort=urgent|ready&q=&page=0&size=12   추천 목록 (로그인)
 * GET /api/recipes/{code}                                          상세 (로그인하면 보유 상태 포함)
 * GET /api/recipes/data                                            전체 레시피 (데모 recipeData 형식)
 * 요리 완료는 dish 패키지: POST /api/recipes/{code}/cook
 */
@RestController
@RequestMapping("/api/recipes")
public class RecipeController {

    private final RecommendService recommendService;
    private final RecipeService recipeService;

    public RecipeController(RecommendService recommendService, RecipeService recipeService) {
        this.recommendService = recommendService;
        this.recipeService = recipeService;
    }

    @GetMapping("/recommend")
    public ApiResponse<RecommendPage> recommend(@AuthenticationPrincipal LoginUser me,
                                                @RequestParam(defaultValue = "urgent") String sort,
                                                @RequestParam(required = false) String q,
                                                @RequestParam(defaultValue = "0") int page,
                                                @RequestParam(defaultValue = "12") int size) {
        return ApiResponse.ok(recommendService.recommend(me.getId(), sort, q, Math.max(0, page), Math.min(Math.max(1, size), 60)));
    }

    @GetMapping(value = "/data", produces = MediaType.APPLICATION_JSON_VALUE)
    public String data() {
        return recipeService.recipeDataJson();
    }

    @GetMapping("/{code}")
    public ApiResponse<RecipeDetail> detail(@PathVariable String code, @AuthenticationPrincipal LoginUser me) {
        return ApiResponse.ok(recipeService.detail(code, me == null ? null : me.getId()));
    }
}
