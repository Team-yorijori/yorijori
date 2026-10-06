package com.yorijori.fridge;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface FridgeMemberRepository extends JpaRepository<FridgeMember, Long> {
    List<FridgeMember> findByUserIdOrderByIdAsc(Long userId);
}
