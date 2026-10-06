package com.yorijori.dish.dto;

import java.util.List;

/** 이번 달 요리 기록 (데모 v8 통계 카드 4개 + 최근 기록) */
public record MonthlyStats(String month, int cooked, int eaten, int saved, int tossed, List<LogResponse> recent) {}
