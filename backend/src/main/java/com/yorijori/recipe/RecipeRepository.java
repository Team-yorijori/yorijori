package com.yorijori.recipe;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface RecipeRepository extends JpaRepository<Recipe, Long> {

    Optional<Recipe> findByCode(String code);

    /** 재료까지 한 번에 (추천 계산용 전체 로드). 조리 순서는 batch fetch 로 따로 불러온다 */
    @Query("select distinct r from Recipe r left join fetch r.ingredients i left join fetch i.ingredient order by r.id")
    List<Recipe> findAllWithIngredients();

    /** 대표 영상이 아직 없는 레시피 (YouTube 수집) */
    @Query("select r from Recipe r where r.videoId is null order by r.id")
    List<Recipe> findWithoutVideo(Pageable pageable);
}
