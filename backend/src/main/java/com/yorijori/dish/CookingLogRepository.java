package com.yorijori.dish;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.List;

public interface CookingLogRepository extends JpaRepository<CookingLog, Long> {

    List<CookingLog> findByUserIdAndLogDateBetween(Long userId, LocalDate from, LocalDate to);

    List<CookingLog> findByUserIdOrderByIdDesc(Long userId, Pageable pageable);

    List<CookingLog> findByUserIdAndKindAndLogDateGreaterThanEqual(Long userId, LogKind kind, LocalDate from);
}
