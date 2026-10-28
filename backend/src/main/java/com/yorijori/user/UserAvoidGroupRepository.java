package com.yorijori.user;

import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface UserAvoidGroupRepository extends JpaRepository<UserAvoidGroup, Long> {
    @EntityGraph(attributePaths = "group")
    List<UserAvoidGroup> findByUserIdOrderByIdAsc(Long userId);
    void deleteByUserId(Long userId);
}
