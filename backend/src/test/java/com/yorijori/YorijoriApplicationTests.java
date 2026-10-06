package com.yorijori;

import com.yorijori.ingredient.IngredientRepository;
import com.yorijori.ingredient.ScanClassRepository;
import com.yorijori.recipe.RecipeCatalog;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.assertj.core.api.Assertions.assertThat;

/** local 프로필(H2)로 띄워서 Flyway 스키마·seed 가 다 들어가는지 확인 */
@SpringBootTest
class YorijoriApplicationTests {

    @Autowired IngredientRepository ingredients;
    @Autowired ScanClassRepository scanClasses;
    @Autowired RecipeCatalog catalog;

    @Test
    void seedLoaded() {
        assertThat(ingredients.count()).isEqualTo(70);
        assertThat(scanClasses.findByModelVersionOrderByClassIdAsc("v4")).hasSize(33);
        assertThat(catalog.all()).hasSize(560);
        assertThat(catalog.find("r1")).isPresent();
        assertThat(catalog.find("kimchi-rice")).isEmpty();          // 공공 레시피에 같은 이름이 있어서 데모 것은 빠졌다
        assertThat(catalog.find("r1").get().getSteps()).isNotEmpty();
    }
}
