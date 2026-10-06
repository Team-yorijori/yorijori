package com.yorijori.ingredient;

import com.yorijori.common.config.AppProperties;
import com.yorijori.common.response.ApiResponse;
import com.yorijori.common.security.LoginUser;
import com.yorijori.ingredient.dto.ScanClassResponse;
import com.yorijori.ingredient.dto.ScanFeedbackRequest;
import jakarta.validation.Valid;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 재료 인식은 브라우저에서 한다 (static/js/ai/fridge-scan.js). 서버는 기준값과 수정 기록만 다룬다.
 * GET  /api/scan/classes    현재 모델의 클래스 + 재료별 인식 기준(v9) + 헷갈리는 재료
 * POST /api/scan/feedback   인식 결과를 고친 기록
 */
@RestController
@RequestMapping("/api/scan")
public class ScanController {

    private final ScanClassRepository classes;
    private final ScanFeedbackRepository feedbacks;
    private final AppProperties props;

    public ScanController(ScanClassRepository classes, ScanFeedbackRepository feedbacks, AppProperties props) {
        this.classes = classes;
        this.feedbacks = feedbacks;
        this.props = props;
    }

    @GetMapping("/classes")
    @Transactional(readOnly = true)
    public ApiResponse<List<ScanClassResponse>> classes(@RequestParam(required = false) String version) {
        String v = version == null ? props.scan().modelVersion() : version;
        return ApiResponse.ok(classes.findByModelVersionOrderByClassIdAsc(v).stream().map(ScanClassResponse::of).toList());
    }

    @PostMapping("/feedback")
    @Transactional
    public ApiResponse<Integer> feedback(@AuthenticationPrincipal LoginUser me, @Valid @RequestBody ScanFeedbackRequest req) {
        int n = 0;
        for (ScanFeedbackRequest.Row r : req.rows()) {
            if (r.predicted().equals(r.corrected())) continue;
            feedbacks.save(new ScanFeedback(me.getId(), req.modelVersion(), r.predicted(), r.corrected(), r.score(), req.consent()));
            n++;
        }
        return ApiResponse.ok(n);
    }
}
