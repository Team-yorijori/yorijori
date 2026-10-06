package com.yorijori.ingredient;

import com.yorijori.common.response.ApiResponse;
import com.yorijori.ingredient.dto.AvoidGroupResponse;
import com.yorijori.ingredient.dto.IngredientResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * GET /api/ingredients?q=ㅇㅍ        재료 기준표 · 자동완성 (초성 가능)
 * GET /api/ingredients/avoid-groups  v9 알레르기 묶음
 */
@RestController
@RequestMapping("/api/ingredients")
public class IngredientController {

    private final IngredientService ingredientService;
    private final AvoidGroupService avoidGroupService;

    public IngredientController(IngredientService ingredientService, AvoidGroupService avoidGroupService) {
        this.ingredientService = ingredientService;
        this.avoidGroupService = avoidGroupService;
    }

    @GetMapping
    public ApiResponse<List<IngredientResponse>> search(@RequestParam(required = false) String q) {
        return ApiResponse.ok(ingredientService.search(q));
    }

    @GetMapping("/avoid-groups")
    public ApiResponse<List<AvoidGroupResponse>> avoidGroups() {
        return ApiResponse.ok(avoidGroupService.list());
    }
}
