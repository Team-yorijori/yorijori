package com.yorijori.cart.dto;

import jakarta.validation.constraints.PositiveOrZero;

/** 목표가·알림 설정. targetPrice = 0 이면 목표가 해제, alert = 목표가 알림 받기 */
public record CartUpdateRequest(@PositiveOrZero Integer targetPrice, Boolean alert) {}
