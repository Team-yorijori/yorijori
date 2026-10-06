package com.yorijori.dish;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface DishRepository extends JpaRepository<Dish, Long> {
    List<Dish> findByFridgeIdOrderByExpDateAscIdAsc(Long fridgeId);
    Optional<Dish> findByIdAndFridgeId(Long id, Long fridgeId);
}
