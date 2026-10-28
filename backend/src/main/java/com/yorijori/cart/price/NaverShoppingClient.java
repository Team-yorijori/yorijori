package com.yorijori.cart.price;

import com.fasterxml.jackson.databind.JsonNode;
import com.yorijori.common.config.AppProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.Comparator;
import java.util.Optional;
import java.util.stream.StreamSupport;

/**
 * 네이버 쇼핑 검색 API — https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md
 * 키는 서버에만 둔다 (브라우저에서 부르면 키가 노출된다). 하루 호출 한도가 있으므로 스케줄러에서만 부른다.
 */
@Component
public class NaverShoppingClient {

    private static final Logger log = LoggerFactory.getLogger(NaverShoppingClient.class);

    private final RestClient http;
    private final AppProperties.Naver cfg;

    public NaverShoppingClient(RestClient.Builder builder, AppProperties props) {
        this.cfg = props.naver();
        this.http = builder.baseUrl("https://openapi.naver.com").build();
    }

    public boolean enabled() {
        return cfg != null && cfg.enabled() && notBlank(cfg.clientId()) && notBlank(cfg.clientSecret());
    }

    /**
     * 재료 이름으로 검색해 식품 분류 중 가장 싼 상품.
     * TODO(백) "양파" 검색에 양파링·양파즙이 섞인다 → 영수증 규칙(ai/receipt)의 가공품 제외 단어를 같이 쓴다.
     */
    public Optional<ShopPrice> lowest(String keyword) {
        if (!enabled()) return Optional.empty();
        try {
            JsonNode res = http.get()
                    .uri(u -> u.path("/v1/search/shop.json")
                               .queryParam("query", keyword)
                               .queryParam("display", 30)
                               .queryParam("sort", "sim")
                               .build())
                    .header("X-Naver-Client-Id", cfg.clientId())
                    .header("X-Naver-Client-Secret", cfg.clientSecret())
                    .retrieve()
                    .body(JsonNode.class);
            if (res == null || !res.has("items")) return Optional.empty();
            return StreamSupport.stream(res.get("items").spliterator(), false)
                    .filter(i -> "식품".equals(i.path("category1").asText()))
                    .filter(i -> i.path("lprice").asInt(0) > 0)
                    .min(Comparator.comparingInt(i -> i.path("lprice").asInt()))
                    .map(i -> new ShopPrice("NAVER", i.path("mallName").asText(null), i.path("lprice").asInt(),
                            i.path("title").asText("").replaceAll("<[^>]+>", ""), i.path("link").asText(null), i.path("productId").asText(null)));
        } catch (RestClientException e) {
            log.warn("네이버 쇼핑 검색 실패: {} — {}", keyword, e.getMessage());
            return Optional.empty();
        }
    }

    private static boolean notBlank(String s) { return s != null && !s.isBlank(); }
}
