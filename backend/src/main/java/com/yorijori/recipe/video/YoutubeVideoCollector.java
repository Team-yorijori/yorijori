package com.yorijori.recipe.video;

import com.yorijori.recipe.Recipe;
import com.yorijori.recipe.RecipeRepository;
import com.yorijori.recipe.RecipeService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 레시피 대표 영상 ID 수집 — 하루 한 번, 영상이 없는 레시피를 dailyLimit 개씩 (560건이면 약 7일)
 * yorijori.youtube.enabled=false 이면 동작하지 않는다.
 * TODO(AI) 첫 결과가 엉뚱한 영상일 수 있다 → 제목에 요리 이름이 들어 있는지 확인, 관리자 화면에서 검수
 */
@Component
public class YoutubeVideoCollector {

    private static final Logger log = LoggerFactory.getLogger(YoutubeVideoCollector.class);

    private final YoutubeClient youtube;
    private final RecipeRepository recipes;
    private final RecipeService recipeService;

    public YoutubeVideoCollector(YoutubeClient youtube, RecipeRepository recipes, RecipeService recipeService) {
        this.youtube = youtube;
        this.recipes = recipes;
        this.recipeService = recipeService;
    }

    @Scheduled(cron = "${yorijori.youtube.collect-cron:0 30 4 * * *}", zone = "Asia/Seoul")
    @Transactional
    public void collect() {
        if (!youtube.enabled()) return;
        List<Recipe> todo = recipes.findWithoutVideo(PageRequest.of(0, youtube.dailyLimit()));
        int found = 0;
        for (Recipe r : todo) {
            var id = youtube.findRecipeVideo(r.getTitle());
            if (id.isPresent()) { r.setVideoId(id.get()); found++; }
        }
        log.info("레시피 영상 수집: {}건 검색, {}건 저장", todo.size(), found);
        if (found > 0) recipeService.evict();
    }
}
