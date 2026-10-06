package com.yorijori.user.dto;

import java.util.List;

/**
 * v9 못 먹는 재료 설정 — 데모의 localStorage "yorijori-demo-avoid-v1" { groups, items, show } 와 같은 모양
 * @param groups 알레르기 묶음 이름 (예: ["계란", "대두"])
 * @param items  직접 넣은 재료 (예: ["오이"])
 * @param show   true면 빼지 않고 빨갛게 표시만
 */
public record AvoidSettings(List<String> groups, List<String> items, boolean show) {}
