package com.yorijori.ingredient;

import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface IngredientAliasRepository extends JpaRepository<IngredientAlias, Long> {
    @EntityGraph(attributePaths = "ingredient")
    Optional<IngredientAlias> findByAlias(String alias);

    @EntityGraph(attributePaths = "ingredient")
    List<IngredientAlias> findBySource(String source);
}
