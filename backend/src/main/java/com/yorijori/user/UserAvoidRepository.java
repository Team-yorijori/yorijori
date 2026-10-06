package com.yorijori.user;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UserAvoidRepository extends JpaRepository<UserAvoid, Long> {
    List<UserAvoid> findByUserId(Long userId);
    void deleteByUserId(Long userId);
}
