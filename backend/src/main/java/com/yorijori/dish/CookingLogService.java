package com.yorijori.dish;

import com.yorijori.dish.dto.LogResponse;
import com.yorijori.dish.dto.MonthlyStats;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Clock;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Transactional(readOnly = true)
public class CookingLogService {

    private final CookingLogRepository logs;
    private final Clock clock;

    public CookingLogService(CookingLogRepository logs, Clock clock) {
        this.logs = logs;
        this.clock = clock;
    }

    /** 레시피 code → 마지막으로 만든 지 며칠 (최근 30일). 추천 감점용 (데모 recentCookDays) */
    public Map<String, Long> recentCookDays(Long userId) {
        LocalDate today = LocalDate.now(clock);
        Map<String, Long> out = new HashMap<>();
        for (CookingLog l : logs.findByUserIdAndKindAndLogDateGreaterThanEqual(userId, LogKind.COOK, today.minusDays(30))) {
            if (l.getRecipeCode() == null) continue;
            long d = ChronoUnit.DAYS.between(l.getLogDate(), today);
            out.merge(l.getRecipeCode(), d, Math::min);
        }
        return out;
    }

    public MonthlyStats monthly(Long userId, YearMonth ym) {
        List<CookingLog> mon = logs.findByUserIdAndLogDateBetween(userId, ym.atDay(1), ym.atEndOfMonth());
        int cooked = 0, eaten = 0, saved = 0, tossed = 0;
        for (CookingLog l : mon) {
            switch (l.getKind()) {
                case COOK -> { cooked++; saved += l.getSaved().size(); }
                case EAT -> eaten += (int) Math.max(1, l.getAmount());
                case TOSS, TOSS_ING -> tossed++;
            }
        }
        List<LogResponse> recent = logs.findByUserIdOrderByIdDesc(userId, PageRequest.of(0, 8)).stream()
                .map(LogResponse::of).toList();
        return new MonthlyStats(ym.toString(), cooked, eaten, saved, tossed, recent);
    }
}
