package com.yorijori.ingredient;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 인식 결과를 사용자가 고친 기록 — 재학습용.
 * 예: 모델이 "귤 98%" 로 봤는데 사용자가 "감"으로 고쳐 등록.
 * consent=false 이면 통계(어떤 재료를 자주 헷갈리는지)에만 쓰고 재학습 데이터로는 쓰지 않는다.
 * 사진은 저장하지 않는다 (사진은 브라우저 밖으로 나가지 않는다).
 */
@Entity
@Table(name = "scan_feedback")
public class ScanFeedback {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "model_version", nullable = false, length = 10)
    private String modelVersion;

    @Column(nullable = false, length = 50)
    private String predicted;

    @Column(nullable = false, length = 50)
    private String corrected;

    private Double score;

    @Column(nullable = false)
    private boolean consent;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "predicted_class_id")
    private ScanClass predictedClass;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "corrected_ingredient_id")
    private Ingredient correctedIngredient;

    public void link(ScanClass predictedClass, Ingredient correctedIngredient) {
        this.predictedClass = predictedClass;
        this.correctedIngredient = correctedIngredient;
    }

    protected ScanFeedback() {}

    public ScanFeedback(Long userId, String modelVersion, String predicted, String corrected, Double score, boolean consent) {
        this.userId = userId;
        this.modelVersion = modelVersion;
        this.predicted = predicted;
        this.corrected = corrected;
        this.score = score;
        this.consent = consent;
    }

    public Long getId() { return id; }
    public String getPredicted() { return predicted; }
    public String getCorrected() { return corrected; }
}
