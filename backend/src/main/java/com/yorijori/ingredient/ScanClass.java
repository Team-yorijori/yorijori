package com.yorijori.ingredient;

import jakarta.persistence.*;

/**
 * 인식 모델 클래스 ↔ 재료. 모델 버전마다 행이 따로 있다 (v3 25종, v4 33종).
 * v9 재료별 인식 기준: auto_threshold 이상이면 자동 체크, confuse_with 는 "혹시 ○○?" 버튼.
 */
@Entity
@Table(name = "scan_class",
       uniqueConstraints = @UniqueConstraint(columnNames = {"model_version", "class_id"}))
public class ScanClass {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "model_version", nullable = false, length = 10)
    private String modelVersion;

    /** 모델 출력의 classId (0부터) */
    @Column(name = "class_id", nullable = false)
    private int classId;

    @Column(name = "en_name", nullable = false, length = 40)
    private String enName;

    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    @JoinColumn(name = "ingredient_id")
    private Ingredient ingredient;

    @Column(name = "auto_threshold", nullable = false)
    private double autoThreshold;

    /** 쉼표로 구분 (예: "귤,레몬,감") */
    @Column(name = "confuse_with", length = 100)
    private String confuseWith;

    /** 검증 mAP50 (참고) */
    @Column(name = "map50")
    private Double map50;

    protected ScanClass() {}

    public Long getId() { return id; }
    public String getModelVersion() { return modelVersion; }
    public int getClassId() { return classId; }
    public String getEnName() { return enName; }
    public Ingredient getIngredient() { return ingredient; }
    public double getAutoThreshold() { return autoThreshold; }
    public String getConfuseWith() { return confuseWith; }
    public Double getMap50() { return map50; }
}
