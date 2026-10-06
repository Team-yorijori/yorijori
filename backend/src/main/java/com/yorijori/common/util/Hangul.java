package com.yorijori.common.util;

/**
 * 초성 검색 — 데모 v6 의 choOf / koHas 를 서버로 옮긴 것.
 * "ㅇㅍ" → 양파, "김ㅊ" → 김치찌개 (글자와 초성을 섞어 써도 된다)
 */
public final class Hangul {

    private static final char[] CHO = {
            'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'};

    private Hangul() {}

    /** 한 글자의 초성. 완성형 한글이 아니면 그대로 돌려준다 */
    public static char choOf(char c) {
        if (c >= 0xAC00 && c <= 0xD7A3) return CHO[(c - 0xAC00) / 588];
        return c;
    }

    public static boolean isCho(char c) {
        for (char x : CHO) if (x == c) return true;
        return false;
    }

    /** text 안에 q가 들어 있는가. q의 초성 글자는 text 글자의 초성과 비교한다. 공백은 무시한다 */
    public static boolean contains(String text, String q) {
        return indexOf(text, q) >= 0;
    }

    /** text 안에서 q가 시작하는 위치(공백 제거 기준). 없으면 -1 */
    public static int indexOf(String text, String q) {
        if (text == null || q == null) return -1;
        String t = text.replace(" ", ""), k = q.replace(" ", "");
        if (k.isEmpty()) return 0;
        outer:
        for (int i = 0; i + k.length() <= t.length(); i++) {
            for (int j = 0; j < k.length(); j++) {
                char a = t.charAt(i + j), b = k.charAt(j);
                if (isCho(b) ? choOf(a) != b : a != b) continue outer;
            }
            return i;
        }
        return -1;
    }

    /** 조사 이/가, 을/를 — 마지막 글자 받침 여부 */
    public static String josa(String word, String withBatchim, String without) {
        if (word == null || word.isEmpty()) return "";
        char c = word.charAt(word.length() - 1);
        boolean batchim = c >= 0xAC00 && c <= 0xD7A3 && (c - 0xAC00) % 28 != 0;
        return word + (batchim ? withBatchim : without);
    }
}
