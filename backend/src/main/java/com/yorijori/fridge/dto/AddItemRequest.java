package com.yorijori.fridge.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;

import java.time.LocalDate;
import java.util.List;

/**
 * 재료 등록 — 직접 입력은 1개, 스캔·영수증은 여러 개를 한 번에 보낸다.
 * qty 가 없으면 기준표의 기본 수량, expDate 가 없으면 보관 일수로 자동 안내.
 */
public record AddItemRequest(@NotEmpty(message = "등록할 재료가 없습니다.") @Size(max = 100) List<@Valid Item> items) {

    public record Item(
            @NotBlank(message = "재료 이름을 입력하세요.") @Size(max = 50) String name,
            @PositiveOrZero Double qty,
            LocalDate expDate,
            /** MANUAL · SCAN · RECEIPT · CART (없으면 MANUAL) */
            String source) {}
}
