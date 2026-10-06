package com.yorijori.recipe;

import jakarta.persistence.*;

@Entity
@Table(name = "recipe_step")
public class RecipeStep {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "recipe_id")
    private Recipe recipe;

    @Column(name = "step_no", nullable = false)
    private int stepNo;

    @Column(nullable = false, length = 2000)
    private String content;

    protected RecipeStep() {}

    public int getStepNo() { return stepNo; }
    public String getContent() { return content; }
}
