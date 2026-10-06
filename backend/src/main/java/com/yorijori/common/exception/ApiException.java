package com.yorijori.common.exception;

/** 서비스 계층에서 던지는 예외. GlobalExceptionHandler가 ApiResponse로 바꾼다. */
public class ApiException extends RuntimeException {

    private final ErrorCode code;

    public ApiException(ErrorCode code) {
        super(code.message());
        this.code = code;
    }

    public ApiException(ErrorCode code, String message) {
        super(message);
        this.code = code;
    }

    public ErrorCode getCode() { return code; }
}
