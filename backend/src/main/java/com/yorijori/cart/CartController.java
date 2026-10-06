package com.yorijori.cart;

import com.yorijori.cart.dto.CartAddRequest;
import com.yorijori.cart.dto.CartItemResponse;
import com.yorijori.cart.dto.CartUpdateRequest;
import com.yorijori.common.response.ApiResponse;
import com.yorijori.common.security.LoginUser;
import com.yorijori.fridge.dto.AddItemResult;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * GET    /api/cart              장보기 목록
 * POST   /api/cart              담기 (여러 개 가능)
 * PATCH  /api/cart/{id}         목표가·알림 설정
 * DELETE /api/cart/{id}         빼기
 * POST   /api/cart/{id}/bought  샀어요 → 냉장고로
 */
@RestController
@RequestMapping("/api/cart")
public class CartController {

    private final CartService cartService;

    public CartController(CartService cartService) {
        this.cartService = cartService;
    }

    @GetMapping
    public ApiResponse<List<CartItemResponse>> list(@AuthenticationPrincipal LoginUser me) {
        return ApiResponse.ok(cartService.list(me.getId()));
    }

    @PostMapping
    public ApiResponse<List<CartItemResponse>> add(@AuthenticationPrincipal LoginUser me, @Valid @RequestBody CartAddRequest req) {
        List<CartItemResponse> added = cartService.add(me.getId(), req);
        return ApiResponse.ok(added, added.isEmpty() ? "이미 담긴 재료입니다." : "장보기에 " + added.size() + "개 담았습니다.");
    }

    @PatchMapping("/{id}")
    public ApiResponse<CartItemResponse> update(@AuthenticationPrincipal LoginUser me, @PathVariable Long id,
                                                @Valid @RequestBody CartUpdateRequest req) {
        return ApiResponse.ok(cartService.update(me.getId(), id, req));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@AuthenticationPrincipal LoginUser me, @PathVariable Long id) {
        cartService.delete(me.getId(), id);
        return ApiResponse.ok(null);
    }

    @PostMapping("/{id}/bought")
    public ApiResponse<AddItemResult> bought(@AuthenticationPrincipal LoginUser me, @PathVariable Long id) {
        AddItemResult r = cartService.bought(me.getId(), id);
        return ApiResponse.ok(r, r.message());
    }
}
