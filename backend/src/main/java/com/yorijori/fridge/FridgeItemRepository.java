package com.yorijori.fridge;

import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.jpa.repository.Lock;
import jakarta.persistence.LockModeType;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

public interface FridgeItemRepository extends JpaRepository<FridgeItem, Long> {

    @EntityGraph(attributePaths = "ingredient")
    List<FridgeItem> findByFridgeIdOrderByExpDateAscIdAsc(Long fridgeId);

    /** 같은 재료 중 소비기한이 가까운 순 (차감용) */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    List<FridgeItem> findByFridgeIdAndNameAndQtyGreaterThanOrderByExpDateAscIdAsc(Long fridgeId, String name, double qty);

    Optional<FridgeItem> findByIdAndFridgeId(Long id, Long fridgeId);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select f from FridgeItem f where f.id = :id and f.fridgeId = :fridgeId")
    Optional<FridgeItem> findForUpdateByIdAndFridgeId(Long id, Long fridgeId);

    /** 다 쓴 재료 정리 */
    @Query("delete from FridgeItem f where f.fridgeId = :fridgeId and f.qty <= 0")
    @org.springframework.data.jpa.repository.Modifying
    int deleteEmpty(Long fridgeId);

    /** 임박 알림 대상 (TODO(백) 알림 기능) */
    List<FridgeItem> findByExpDateBetween(LocalDate from, LocalDate to);
}
