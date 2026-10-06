package com.yorijori.fridge;

/**
 * 재료 이름별 보유 현황 — 추천 점수 계산용 (데모 stockQty / soonest)
 * @param qty      전체 수량
 * @param soonest  가장 가까운 소비기한까지 남은 일수
 */
public record Stock(String name, double qty, long soonest) {}
