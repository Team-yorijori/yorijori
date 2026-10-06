package com.yorijori.recipe.video;

import com.fasterxml.jackson.databind.JsonNode;
import com.yorijori.common.config.AppProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.Optional;

/**
 * YouTube Data API v3 search.list — 1회 100 유닛, 기본 할당량 하루 10,000 유닛 = 검색 100회.
 * 그래서 레시피마다 한 번만 찾아 recipe.video_id 에 저장한다.
 */
@Component
public class YoutubeClient {

    private static final Logger log = LoggerFactory.getLogger(YoutubeClient.class);

    private final RestClient http;
    private final AppProperties.Youtube cfg;

    public YoutubeClient(RestClient.Builder builder, AppProperties props) {
        this.cfg = props.youtube();
        this.http = builder.baseUrl("https://www.googleapis.com/youtube/v3").build();
    }

    public boolean enabled() {
        return cfg != null && cfg.enabled() && cfg.apiKey() != null && !cfg.apiKey().isBlank();
    }

    /** "김치찌개 레시피" 로 검색해 첫 번째 동영상 ID */
    public Optional<String> findRecipeVideo(String recipeTitle) {
        if (!enabled()) return Optional.empty();
        try {
            JsonNode res = http.get()
                    .uri(u -> u.path("/search")
                               .queryParam("part", "snippet")
                               .queryParam("type", "video")
                               .queryParam("maxResults", 1)
                               .queryParam("regionCode", "KR")
                               .queryParam("relevanceLanguage", "ko")
                               .queryParam("videoEmbeddable", "true")
                               .queryParam("q", recipeTitle + " 레시피")
                               .queryParam("key", cfg.apiKey())
                               .build())
                    .retrieve()
                    .body(JsonNode.class);
            if (res == null) return Optional.empty();
            JsonNode first = res.path("items").path(0).path("id").path("videoId");
            return first.isMissingNode() || first.asText().isBlank() ? Optional.empty() : Optional.of(first.asText());
        } catch (RestClientException e) {
            log.warn("YouTube 검색 실패: {} — {}", recipeTitle, e.getMessage());
            return Optional.empty();
        }
    }

    public int dailyLimit() {
        return cfg == null || cfg.dailyLimit() <= 0 ? 90 : cfg.dailyLimit();
    }
}
