package com.yorijori.common.util;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class HangulTest {

    @Test
    void choseongSearch() {
        assertThat(Hangul.contains("양파", "ㅇㅍ")).isTrue();
        assertThat(Hangul.contains("김치찌개", "ㄱㅊㅉㄱ")).isTrue();
        assertThat(Hangul.contains("김치찌개", "김ㅊ")).isTrue();       // 글자 + 초성 섞어 쓰기
        assertThat(Hangul.contains("양배추", "ㅇㅍ")).isFalse();
        assertThat(Hangul.indexOf("돼지 김치찌개", "ㄱㅊ")).isEqualTo(2); // 공백은 무시
    }

    @Test
    void josa() {
        assertThat(Hangul.josa("된장국", "을", "를")).isEqualTo("된장국을");
        assertThat(Hangul.josa("김치찌개", "을", "를")).isEqualTo("김치찌개를");
        assertThat(Hangul.josa("계란, 오이", "이", "가")).isEqualTo("계란, 오이가");
    }
}
