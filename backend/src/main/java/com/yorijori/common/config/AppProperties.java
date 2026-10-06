package com.yorijori.common.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * application.yml 의 yorijori.* 설정.
 * 키 값은 application-secret.yml(깃에 올리지 않음) 또는 환경 변수로 넣는다.
 */
@ConfigurationProperties(prefix = "yorijori")
public record AppProperties(Naver naver, Youtube youtube, Scan scan) {

    /** 네이버 쇼핑 검색 API — 최저가 확인 스케줄러 */
    public record Naver(boolean enabled, String clientId, String clientSecret, String priceCron) {}

    /** YouTube Data API — 레시피 대표 영상 ID 수집 (하루 검색 100회 한도) */
    public record Youtube(boolean enabled, String apiKey, int dailyLimit, String collectCron) {}

    /** 브라우저 재료 인식 모델 */
    public record Scan(String modelVersion, String modelUrl, String classesUrl) {}
}
