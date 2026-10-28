package com.yorijori.ingredient.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.List;

/** 스캔 결과 등록 시, 이름을 고친 줄만 모아서 보낸다 */
public record ScanFeedbackRequest(@NotBlank @Size(max = 10) String modelVersion, boolean consent,
                                  @NotNull List<@NotNull @Valid Row> rows) {
    public record Row(@NotBlank @Size(max = 50) String predicted,
                      @NotBlank @Size(max = 50) String corrected,
                      @DecimalMin("0.0") @DecimalMax("1.0") Double score) {}
}
