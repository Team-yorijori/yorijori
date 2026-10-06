package com.yorijori.dish;

import com.yorijori.common.response.ApiResponse;
import com.yorijori.common.security.LoginUser;
import com.yorijori.dish.dto.CookRequest;
import com.yorijori.dish.dto.CookResult;
import com.yorijori.dish.dto.DishResponse;
import com.yorijori.dish.dto.MonthlyStats;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.time.YearMonth;
import java.util.List;

/**
 * POST   /api/recipes/{code}/cook   요리 완료: 재료 차감 + 만든 요리 생성
 * GET    /api/dishes                만든 요리 (보관 기한 가까운 순)
 * POST   /api/dishes/{id}/eat       1인분 먹기
 * DELETE /api/dishes/{id}           버리기
 * GET    /api/stats/monthly?month=2026-10   이번 달 기록
 */
@RestController
@RequestMapping("/api")
public class DishController {

    private final DishService dishService;
    private final CookingLogService cookingLogService;

    public DishController(DishService dishService, CookingLogService cookingLogService) {
        this.dishService = dishService;
        this.cookingLogService = cookingLogService;
    }

    @PostMapping("/recipes/{code}/cook")
    public ApiResponse<CookResult> cook(@AuthenticationPrincipal LoginUser me, @PathVariable String code,
                                        @Valid @RequestBody CookRequest req) {
        CookResult r = dishService.cook(me.getId(), code, req);
        return ApiResponse.ok(r, r.message());
    }

    @GetMapping("/dishes")
    public ApiResponse<List<DishResponse>> list(@AuthenticationPrincipal LoginUser me) {
        return ApiResponse.ok(dishService.list(me.getId()));
    }

    @PostMapping("/dishes/{id}/eat")
    public ApiResponse<DishResponse> eat(@AuthenticationPrincipal LoginUser me, @PathVariable Long id) {
        String name = dishService.list(me.getId()).stream().filter(d -> d.id().equals(id)).map(DishResponse::name).findFirst().orElse("");
        DishResponse after = dishService.eat(me.getId(), id);
        return ApiResponse.ok(after, dishService.eatMessage(name, after));
    }

    @DeleteMapping("/dishes/{id}")
    public ApiResponse<Void> toss(@AuthenticationPrincipal LoginUser me, @PathVariable Long id) {
        return ApiResponse.ok(null, dishService.toss(me.getId(), id));
    }

    @GetMapping("/stats/monthly")
    public ApiResponse<MonthlyStats> monthly(@AuthenticationPrincipal LoginUser me,
                                             @RequestParam(required = false) String month) {
        YearMonth ym = month == null ? YearMonth.now(java.time.ZoneId.of("Asia/Seoul")) : YearMonth.parse(month);
        return ApiResponse.ok(cookingLogService.monthly(me.getId(), ym));
    }
}
