package com.yorijori.cart;

import com.yorijori.cart.price.PriceCheckScheduler;
import com.yorijori.cart.price.NaverShoppingClient;
import com.yorijori.cart.price.ShopPrice;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.transaction.annotation.Transactional;
import java.util.Optional;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

@SpringBootTest
@Transactional
class ProductRelationTest {
    @Autowired PriceCheckScheduler scheduler;
    @Autowired JdbcTemplate jdbc;
    @Autowired jakarta.persistence.EntityManager em;
    @MockitoBean NaverShoppingClient naver;

    private void cart(String name) {
        jdbc.update("INSERT INTO users(email,password_hash,nickname,role) VALUES('product@test.local','hash','상품검증','USER')");
        Long user = jdbc.queryForObject("SELECT id FROM users WHERE email='product@test.local'", Long.class);
        jdbc.update("INSERT INTO cart_item(user_id,name) VALUES(?,?)", user, name);
        when(naver.enabled()).thenReturn(true);
    }

    @Test
    void observationWithoutExternalIdKeepsSnapshotAndIngredientButNoProduct() {
        cart("달걀");
        when(naver.lowest("달걀")).thenReturn(Optional.of(new ShopPrice("NAVER","상점",3000,"계란 10개","https://shop.test/item")));
        scheduler.checkPrices();
        var row=jdbc.queryForMap("SELECT ingredient_name,ingredient_id,product_id,product_title,price FROM price_history ORDER BY id DESC LIMIT 1");
        assertThat(row.get("ingredient_name")).isEqualTo("달걀");
        assertThat(row.get("ingredient_id")).isEqualTo(jdbc.queryForObject("SELECT id FROM ingredient WHERE name='계란'",Long.class));
        assertThat(row.get("product_id")).isNull();
        assertThat(row.get("product_title")).isEqualTo("계란 10개");
        assertThat(row.get("price")).isEqualTo(3000);
    }

    private ShopPrice product(String title, int price) throws Exception {
        return new ShopPrice("NAVER","상점",price,title,"https://shop.test/item","external-42");
    }

    @Test
    void invalidExternalIdsPreserveObservationsWithoutCreatingProductIdentity() {
        cart("달걀");
        for (String externalId : new String[]{"   ", "x".repeat(101)}) {
            when(naver.lowest("달걀")).thenReturn(Optional.of(new ShopPrice("NAVER","상점",3000,"계란","https://shop.test/item",externalId)));
            scheduler.checkPrices();
        }
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM product", Long.class)).isZero();
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM price_history WHERE ingredient_name='달걀' AND product_id IS NULL", Long.class)).isEqualTo(2L);
    }

    @Test
    void existingProductIngredientSurvivesAliasRemapping() throws Exception {
        cart("달걀");
        when(naver.lowest("달걀")).thenReturn(Optional.of(product("같은 상품",3000)));
        scheduler.checkPrices();
        em.flush();
        em.clear();
        jdbc.update("UPDATE ingredient_alias SET ingredient_id=(SELECT id FROM ingredient WHERE name='두부') WHERE alias='달걀'");
        scheduler.checkPrices();
        assertThat(jdbc.queryForObject("SELECT ingredient_id FROM product WHERE channel='NAVER' AND external_id='external-42'", Long.class))
                .isEqualTo(jdbc.queryForObject("SELECT id FROM ingredient WHERE name='계란'", Long.class));
        assertThat(jdbc.queryForObject("SELECT ingredient_id FROM price_history ORDER BY id DESC LIMIT 1", Long.class))
                .isEqualTo(jdbc.queryForObject("SELECT id FROM ingredient WHERE name='두부'", Long.class));
    }

    @Test
    void repeatedExternalProductReusesIdentityAndPreservesEarlierSnapshot() throws Exception {
        cart("달걀");
        when(naver.lowest("달걀")).thenReturn(Optional.of(product("첫 제목 10개",3000)));
        scheduler.checkPrices();
        when(naver.lowest("달걀")).thenReturn(Optional.of(product("새 제목 12개",2500)));
        scheduler.checkPrices();
        var rows=jdbc.queryForList("SELECT product_id,product_title,price FROM price_history WHERE ingredient_name='달걀' ORDER BY id");
        assertThat(rows).hasSize(2);
        assertThat(rows.get(0).get("product_id")).isNotNull().isEqualTo(rows.get(1).get("product_id"));
        assertThat(rows.get(0).get("product_title")).isEqualTo("첫 제목 10개");
        assertThat(rows.get(0).get("price")).isEqualTo(3000);
        var product=jdbc.queryForMap("SELECT ingredient_id,package_qty,package_unit FROM product WHERE channel='NAVER' AND external_id='external-42'");
        assertThat(product.get("ingredient_id")).isEqualTo(jdbc.queryForObject("SELECT id FROM ingredient WHERE name='계란'",Long.class));
        assertThat(product.get("package_qty")).isNull();
        assertThat(product.get("package_unit")).isNull();
    }
}
