package com.yorijori.ingredient;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface ScanFeedbackRepository extends JpaRepository<ScanFeedback, Long> {

    /** 자주 헷갈리는 쌍 (예: 귤 → 감 37번) — 다음 학습 데이터 우선순위 정할 때 */
    @Query("select f.predicted, f.corrected, count(f) from ScanFeedback f " +
           "where f.predicted <> f.corrected group by f.predicted, f.corrected order by count(f) desc")
    List<Object[]> confusionCounts();
}
