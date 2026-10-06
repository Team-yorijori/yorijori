package com.yorijori.cart.price;

import com.yorijori.cart.CartItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * 목표가 알림.
 * TODO(백) 알림 방식 결정: 웹 푸시(Service Worker + VAPID) 또는 메일(spring-boot-starter-mail).
 * 지금은 로그만 남긴다.
 */
@Component
public class PriceNotifier {

    private static final Logger log = LoggerFactory.getLogger(PriceNotifier.class);

    public void notifyTargetReached(CartItem c) {
        log.info("[최저가 알림] user={} {} {}원 (목표 {}원) {} {}", c.getUserId(), c.getName(), c.getLowestPrice(),
                c.getTargetPrice(), c.getLowestShop(), c.getLowestUrl());
    }
}
