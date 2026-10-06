package com.yorijori.fridge.dto;

import com.yorijori.fridge.FridgeItem;

import java.time.LocalDate;

public record FridgeItemResponse(Long id, String name, String category, double qty, String unit,
                                 LocalDate regDate, LocalDate expDate, boolean expAuto, long dday, String source) {

    public static FridgeItemResponse of(FridgeItem f, LocalDate today) {
        String cat = f.getIngredient() == null ? "기타" : f.getIngredient().getCategory();
        return new FridgeItemResponse(f.getId(), f.getName(), cat, f.getQty(), f.getUnit(),
                f.getRegDate(), f.getExpDate(), f.isExpAuto(), f.daysLeft(today), f.getSource());
    }
}
