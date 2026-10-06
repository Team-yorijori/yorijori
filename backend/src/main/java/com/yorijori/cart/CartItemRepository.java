package com.yorijori.cart;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface CartItemRepository extends JpaRepository<CartItem, Long> {
    List<CartItem> findByUserIdOrderByIdDesc(Long userId);
    Optional<CartItem> findByIdAndUserId(Long id, Long userId);
    Optional<CartItem> findByUserIdAndName(Long userId, String name);
    List<CartItem> findByUserIdAndNameIn(Long userId, List<String> names);

    /** 가격을 확인할 재료 이름 (모든 회원의 장보기 목록에서 중복 없이) */
    @Query("select distinct c.name from CartItem c")
    List<String> findDistinctNames();

    List<CartItem> findByName(String name);
}
