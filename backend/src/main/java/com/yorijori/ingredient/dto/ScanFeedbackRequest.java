package com.yorijori.ingredient.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.util.List;

/** 스캔 결과 등록 시, 이름을 고친 줄만 모아서 보낸다 */
public record ScanFeedbackRequest(@NotBlank String modelVersion, boolean consent, @NotNull List<Row> rows) {
    public record Row(@NotBlank String predicted, @NotBlank String corrected, Double score) {}
}
