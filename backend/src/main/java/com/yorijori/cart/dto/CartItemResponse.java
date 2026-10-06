package com.yorijori.cart.dto;

import com.yorijori.cart.CartItem;

import java.time.LocalDateTime;

public record CartItemResponse(Long id, String name, Integer targetPrice, boolean alert,
                               Integer lowestPrice, String lowestShop, String lowestUrl, LocalDateTime lowestCheckedAt) {
    public static CartItemResponse of(CartItem c) {
        return new CartItemResponse(c.getId(), c.getName(), c.getTargetPrice(), c.isAlert(),
                c.getLowestPrice(), c.getLowestShop(), c.getLowestUrl(), c.getLowestCheckedAt());
    }
}
