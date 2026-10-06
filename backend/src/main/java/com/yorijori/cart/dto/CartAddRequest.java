package com.yorijori.cart.dto;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.PositiveOrZero;

import java.util.List;

/**
 * 담기 — 직접 담기는 names 1개, 레시피 "부족한 재료 담기"는 여러 개.
 * targetPrice 는 1개 담을 때만 쓴다.
 */
public record CartAddRequest(@NotEmpty(message = "담을 재료를 입력하세요.") List<String> names,
                             @PositiveOrZero Integer targetPrice) {}
