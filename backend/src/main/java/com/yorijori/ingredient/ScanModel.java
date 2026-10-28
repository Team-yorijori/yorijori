package com.yorijori.ingredient;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

/** 배포 및 피드백에서 참조하는 인식 모델 버전 레지스트리. */
@Entity
@Table(name = "scan_model")
public class ScanModel {
    @Id @Column(length = 10)
    private String version;
    @Column(name = "display_name", nullable = false, length = 100)
    private String displayName;
    @Column(name = "artifact_path", length = 500)
    private String artifactPath;
    @Column(name = "released_at")
    private LocalDateTime releasedAt;
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    protected ScanModel() {}
    public String getVersion() { return version; }
}
