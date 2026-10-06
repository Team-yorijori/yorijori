package com.yorijori.fridge.dto;

import jakarta.validation.constraints.PositiveOrZero;

import java.time.LocalDate;

/**
 * 소비기한·수량 수정 (데모 v6 수정 창)
 * resetAuto = true 이면 expDate 를 무시하고 자동 안내 날짜(등록일 + 보관 일수)로 되돌린다.
 * qty = 0 이면 다 쓴 것으로 보고 지운다.
 */
public record UpdateItemRequest(@PositiveOrZero Double qty, LocalDate expDate, Boolean resetAuto) {}
