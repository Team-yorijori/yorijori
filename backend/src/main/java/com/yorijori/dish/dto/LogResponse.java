package com.yorijori.dish.dto;

import com.yorijori.dish.CookingLog;

import java.time.LocalDate;
import java.util.List;

/** 데모 log 와 같은 모양: t = cook · eat · toss · tossIng */
public record LogResponse(String t, String name, String rid, double n, List<String> saved, LocalDate d) {
    public static LogResponse of(CookingLog l) {
        String t = switch (l.getKind()) {
            case COOK -> "cook";
            case EAT -> "eat";
            case TOSS -> "toss";
            case TOSS_ING -> "tossIng";
        };
        return new LogResponse(t, l.getName(), l.getRecipeCode(), l.getAmount(), l.getSaved(), l.getLogDate());
    }
}
