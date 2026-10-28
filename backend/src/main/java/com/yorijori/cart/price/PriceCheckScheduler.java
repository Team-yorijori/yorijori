package com.yorijori.cart.price;

import com.yorijori.cart.CartItem;
import com.yorijori.cart.CartItemRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.Optional;

/**
 * 최저가 확인 — 장보기 목록에 있는 재료만, 하루 몇 번 (yorijori.naver.price-cron)
 * yorijori.naver.enabled=false 이거나 키가 없으면 아무 것도 하지 않는다.
 */
@Component
public class PriceCheckScheduler {

    private static final Logger log = LoggerFactory.getLogger(PriceCheckScheduler.class);

    private final NaverShoppingClient naver;
    private final CartItemRepository carts;
    private final PriceObservationService observations;
    private final PriceNotifier notifier;

    public PriceCheckScheduler(NaverShoppingClient naver, CartItemRepository carts,
                               PriceObservationService observations, PriceNotifier notifier) {
        this.naver = naver;
        this.carts = carts;
        this.observations = observations;
        this.notifier = notifier;
    }

    @Scheduled(cron = "${yorijori.naver.price-cron:0 0 9,13,19 * * *}", zone = "Asia/Seoul")
    @Transactional
    public void checkPrices() {
        if (!naver.enabled()) return;
        List<String> names = carts.findDistinctNames();
        LocalDateTime now = LocalDateTime.now(ZoneId.of("Asia/Seoul"));
        int found = 0;
        for (String name : names) {
            Optional<ShopPrice> p = naver.lowest(name);
            if (p.isEmpty()) continue;
            found++;
            ShopPrice sp = p.get();
            observations.observe(name, sp, now);
            for (CartItem c : carts.findByName(name)) {
                c.updateLowest(sp.price(), sp.mallName(), sp.url(), now);
                if (c.shouldNotify()) {
                    notifier.notifyTargetReached(c);
                    c.markNotified();
                }
            }
        }
        log.info("최저가 확인: 재료 {}개 중 {}개 가격 갱신", names.size(), found);
    }
}
