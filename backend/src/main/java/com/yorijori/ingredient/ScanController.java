package com.yorijori.ingredient;

import com.yorijori.common.config.AppProperties;
import com.yorijori.common.exception.ApiException;
import com.yorijori.common.exception.ErrorCode;
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
    private final ScanModelRepository models;
    private final IngredientService ingredients;

    public ScanController(ScanClassRepository classes, ScanFeedbackRepository feedbacks, AppProperties props, ScanModelRepository models, IngredientService ingredients) {
        this.classes = classes;
        this.feedbacks = feedbacks;
        this.props = props;
        this.models = models;
        this.ingredients = ingredients;
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
        if (!models.existsById(req.modelVersion())) {
            throw new ApiException(ErrorCode.INVALID_INPUT, "등록되지 않은 인식 모델 버전입니다.");
        }
        int n = 0;
        for (ScanFeedbackRequest.Row r : req.rows()) {
            if (r.predicted().equals(r.corrected())) continue;
            ScanClass predictedClass = ingredients.resolve(r.predicted())
                    .map(i -> classes.findByModelVersionAndIngredientId(req.modelVersion(), i.getId()))
                    .filter(matches -> matches.size() == 1)
                    .map(matches -> matches.get(0)).orElse(null);
            ScanFeedback feedback = new ScanFeedback(me.getId(), req.modelVersion(), r.predicted(), r.corrected(), r.score(), req.consent());
            feedback.link(predictedClass, ingredients.resolve(r.corrected()).orElse(null));
            feedbacks.save(feedback);
            n++;
        }
        return ApiResponse.ok(n);
    }
}
