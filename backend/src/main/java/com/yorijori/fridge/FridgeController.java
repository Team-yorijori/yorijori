package com.yorijori.fridge;

import com.yorijori.cart.CartService;
import com.yorijori.common.response.ApiResponse;
import com.yorijori.common.security.LoginUser;
import com.yorijori.fridge.dto.AddItemRequest;
import com.yorijori.fridge.dto.AddItemResult;
import com.yorijori.fridge.dto.FridgeItemResponse;
import com.yorijori.fridge.dto.UpdateItemRequest;
import com.yorijori.user.UserService;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * GET    /api/fridge/items        내 냉장고 (소비기한 가까운 순)
 * POST   /api/fridge/items        등록 (여러 개 가능: 스캔·영수증)
 * PATCH  /api/fridge/items/{id}   수량·소비기한 수정
 * DELETE /api/fridge/items/{id}   버리기 (기록 남김)
 */
@RestController
@RequestMapping("/api/fridge/items")
public class FridgeController {

    private final FridgeService fridgeService;
    private final CartService cartService;
    private final UserService userService;

    public FridgeController(FridgeService fridgeService, CartService cartService, UserService userService) {
        this.fridgeService = fridgeService;
        this.cartService = cartService;
        this.userService = userService;
    }

    @GetMapping
    public ApiResponse<List<FridgeItemResponse>> list(@AuthenticationPrincipal LoginUser me) {
        return ApiResponse.ok(fridgeService.list(me.getId()));
    }

    /**
     * 등록 후
     * - 장보기 목록에 있던 재료는 목록에서 뺀다 (데모 v6 cartBought)
     * - 못 먹는 재료면 안내를 붙인다 (데모 v9)
     */
    @PostMapping
    public ApiResponse<Map<String, Object>> add(@AuthenticationPrincipal LoginUser me, @Valid @RequestBody AddItemRequest req) {
        List<AddItemResult> added = fridgeService.add(me.getId(), req);
        List<String> names = added.stream().map(a -> a.item().name()).toList();
        List<String> removedFromCart = cartService.removeByNames(me.getId(), names);
        List<String> terms = userService.avoidTerms(me.getId());
        List<AddItemResult> out = new ArrayList<>();
        for (AddItemResult a : added) {
            boolean avoid = terms.stream().anyMatch(t -> a.item().name().contains(t));
            out.add(avoid ? new AddItemResult(a.item(), a.message() + " · 못 먹는 재료로 설정된 재료입니다") : a);
        }
        return ApiResponse.ok(Map.of("items", out, "removedFromCart", removedFromCart));
    }

    @PatchMapping("/{id}")
    public ApiResponse<FridgeItemResponse> update(@AuthenticationPrincipal LoginUser me, @PathVariable Long id,
                                                  @Valid @RequestBody UpdateItemRequest req) {
        FridgeItemResponse r = fridgeService.update(me.getId(), id, req);
        return ApiResponse.ok(r, r == null ? "다 쓴 재료를 목록에서 뺐습니다." : null);
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> toss(@AuthenticationPrincipal LoginUser me, @PathVariable Long id) {
        fridgeService.toss(me.getId(), id);
        return ApiResponse.ok(null);
    }
}
