package com.yorijori.ingredient.dto;

import com.yorijori.ingredient.ScanClass;

import java.util.Arrays;
import java.util.List;

/** 화면의 SCAN_CLASSES + SCAN_AUTO + SCAN_CONFUSE 를 한 번에 */
public record ScanClassResponse(int id, String en, String ko, double auto, List<String> confuse) {
    public static ScanClassResponse of(ScanClass c) {
        List<String> confuse = c.getConfuseWith() == null || c.getConfuseWith().isBlank() ? List.of()
                : Arrays.stream(c.getConfuseWith().split(",")).map(String::trim).toList();
        return new ScanClassResponse(c.getClassId(), c.getEnName(), c.getIngredient().getName(), c.getAutoThreshold(), confuse);
    }
}
