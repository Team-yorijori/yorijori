package com.yorijori.common.response;

/**
 * 모든 REST 응답의 공통 형식.
 * 성공: { "ok": true,  "data": {...}, "message": null }
 * 실패: { "ok": false, "data": null,  "message": "재료 이름을 입력하세요.", "code": "INVALID_INPUT" }
 */
public record ApiResponse<T>(boolean ok, T data, String message, String code) {

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(true, data, null, null);
    }

    public static <T> ApiResponse<T> ok(T data, String message) {
        return new ApiResponse<>(true, data, message, null);
    }

    public static ApiResponse<Void> fail(String code, String message) {
        return new ApiResponse<>(false, null, message, code);
    }
}
