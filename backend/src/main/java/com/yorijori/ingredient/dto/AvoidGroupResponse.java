package com.yorijori.ingredient.dto;

import com.yorijori.ingredient.AvoidGroup;

import java.util.List;

public record AvoidGroupResponse(String name, List<String> terms, String warning) {
    public static AvoidGroupResponse of(AvoidGroup g) {
        return new AvoidGroupResponse(g.getName(), List.copyOf(g.getTerms()), g.getWarning());
    }
}
