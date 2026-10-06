package com.yorijori.ingredient;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ScanClassRepository extends JpaRepository<ScanClass, Long> {
    List<ScanClass> findByModelVersionOrderByClassIdAsc(String modelVersion);
}
