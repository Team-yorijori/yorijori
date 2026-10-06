package com.yorijori.cart;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.time.LocalDateTime;
import java.util.List;

public interface PriceHistoryRepository extends JpaRepository<PriceHistory, Long> {

    List<PriceHistory> findByIngredientNameAndCheckedAtAfterOrderByCheckedAtAsc(String ingredientName, LocalDateTime after);

    @Query("select min(p.price) from PriceHistory p where p.ingredientName = :name and p.checkedAt >= :after")
    Integer minPriceSince(String name, LocalDateTime after);
}
