package com.yorijori.database;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.sql.*;
import java.util.*;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

/** 실제 migration을 실행한다. 외부 DB 지정 시 반드시 비어 있는 전용 테스트 DB여야 한다. */
class DatabaseIntegrityTest {
    static String url;
    static String username;
    static String password;
    Connection connection;

    @BeforeAll
    static void migrateExistingDatabase() throws Exception {
        url = System.getenv().getOrDefault("YORIJORI_TEST_DB_URL",
                "jdbc:h2:mem:integrity_" + UUID.randomUUID() + ";MODE=MySQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1");
        username = System.getenv().getOrDefault("YORIJORI_TEST_DB_USERNAME", "sa");
        password = System.getenv().getOrDefault("YORIJORI_TEST_DB_PASSWORD", "");
        // 기존 DB에서 테스트를 실행하지 않도록, Flyway를 부르기 전에 사용자 테이블이 없는지 검사한다.
        try (Connection c = DriverManager.getConnection(url, username, password);
             ResultSet tables = c.getMetaData().getTables(c.getCatalog(), c.getSchema(), "%", new String[]{"TABLE"})) {
            assertThat(tables.next()).as("빈 전용 테스트 DB만 허용합니다").isFalse();
        }
        Flyway.configure().dataSource(url, username, password).target("3").load().migrate();
        try (Connection c = DriverManager.getConnection(url, username, password); Statement s = c.createStatement()) {
            s.executeUpdate("INSERT INTO users(id,email,password_hash,nickname,role) VALUES (900001,'db-test@example.invalid','test-only','DB 검증','USER')");
            s.executeUpdate("INSERT INTO fridge(id,name) VALUES (900001,'검증 냉장고')");
            s.executeUpdate("INSERT INTO fridge_item(id,fridge_id,name,qty,unit,reg_date,exp_date,exp_auto,source) VALUES (900001,900001,'청경채',2,'개','2026-10-28','2026-10-27',FALSE,'MANUAL')");
            s.executeUpdate("INSERT INTO dish(id,fridge_id,name,servings,servings_left,made_date,exp_date) VALUES (900001,900001,'검증 요리',2,1,'2026-10-28','2026-10-30')");
            s.executeUpdate("INSERT INTO cooking_log(id,user_id,kind,dish_id,name,amount,log_date) VALUES (900001,900001,'COOK',900001,'검증 요리',2,'2026-10-28')");
            s.executeUpdate("INSERT INTO cooking_log_ingredient(id,log_id,ingredient_name,qty,days_left) VALUES (900001,900001,'청경채',1,-1)");
            s.executeUpdate("INSERT INTO cart_item(id,user_id,name) VALUES (900001,900001,'청경채')");
            s.executeUpdate("INSERT INTO price_history(id,ingredient_name,channel,price,checked_at) VALUES (900001,'청경채','TEST',1000,CURRENT_TIMESTAMP)");
            s.executeUpdate("INSERT INTO scan_feedback(id,user_id,model_version,predicted,corrected,consent) VALUES (900001,900001,'v4','배추','청경채',FALSE)");
        }
        Flyway.configure().dataSource(url, username, password).load().migrate();
    }

    @BeforeEach
    void beginTransaction() throws Exception {
        connection = DriverManager.getConnection(url, username, password);
        connection.setAutoCommit(false);
    }

    @AfterEach
    void rollback() throws Exception {
        if (connection != null) {
            connection.rollback();
            connection.close();
        }
    }

    static Stream<Arguments> invalidValues() {
        return Stream.of(
            Arguments.of("ck_ingredient_fridge_days", "UPDATE ingredient SET fridge_days=-1 WHERE id=1"),
            Arguments.of("ck_ingredient_default_qty", "UPDATE ingredient SET default_qty=0 WHERE id=1"),
            Arguments.of("ck_ingredient_each_gram", "UPDATE ingredient SET each_gram=0 WHERE id=1"),
            Arguments.of("ck_fridge_item_qty", "UPDATE fridge_item SET qty=-0.01 WHERE id=900001"),
            Arguments.of("ck_dish_servings", "UPDATE dish SET servings=0,servings_left=0 WHERE id=900001"),
            Arguments.of("ck_dish_servings_left", "UPDATE dish SET servings_left=-1 WHERE id=900001"),
            Arguments.of("ck_dish_servings_left", "UPDATE dish SET servings_left=3 WHERE id=900001"),
            Arguments.of("ck_cart_target_price", "UPDATE cart_item SET target_price=-1 WHERE id=900001"),
            Arguments.of("ck_cart_lowest_price", "UPDATE cart_item SET lowest_price=-1 WHERE id=900001"),
            Arguments.of("ck_cart_notified_price", "UPDATE cart_item SET notified_price=-1 WHERE id=900001"),
            Arguments.of("ck_cooking_log_amount", "UPDATE cooking_log SET amount=-1 WHERE id=900001"),
            Arguments.of("ck_log_ingredient_qty", "UPDATE cooking_log_ingredient SET qty=-1 WHERE id=900001"),
            Arguments.of("ck_price_history_price", "UPDATE price_history SET price=-1 WHERE id=900001"),
            Arguments.of("ck_scan_class_id", "UPDATE scan_class SET class_id=-1 WHERE id=1"),
            Arguments.of("ck_scan_auto_threshold", "UPDATE scan_class SET auto_threshold=-0.01 WHERE id=1"),
            Arguments.of("ck_scan_auto_threshold", "UPDATE scan_class SET auto_threshold=1.01 WHERE id=1"),
            Arguments.of("ck_scan_map50", "UPDATE scan_class SET map50=-0.01 WHERE id=1"),
            Arguments.of("ck_scan_map50", "UPDATE scan_class SET map50=1.01 WHERE id=1")
        );
    }

    @ParameterizedTest(name = "{0}: {1}")
    @MethodSource("invalidValues")
    void rejectsInvalidValuesAtDatabaseBoundary(String constraint, String sql) {
        SQLException failure = assertThrows(SQLException.class, () -> execute(sql));
        assertThat(failure.getMessage()).containsIgnoringCase(constraint);
    }

    @Test
    void rejectsOrphanFeedbackMember() {
        SQLException failure = assertThrows(SQLException.class,
                () -> execute("UPDATE scan_feedback SET user_id=999999 WHERE id=900001"));
        assertThat(failure.getMessage()).containsIgnoringCase("fk_feedback_user");
    }

    @Test
    void acceptsTransientZeroAndNullableBoundaryValues() throws Exception {
        execute("UPDATE ingredient SET fridge_days=0,default_qty=0.01,each_gram=NULL WHERE id=1");
        execute("UPDATE fridge_item SET qty=0 WHERE id=900001");
        execute("UPDATE dish SET servings_left=0 WHERE id=900001");
        execute("UPDATE cart_item SET target_price=0,lowest_price=0,notified_price=0 WHERE id=900001");
        execute("UPDATE cart_item SET target_price=NULL,lowest_price=NULL,notified_price=NULL WHERE id=900001");
        execute("UPDATE cooking_log SET amount=0 WHERE id=900001");
        execute("UPDATE cooking_log_ingredient SET qty=0 WHERE id=900001");
        execute("UPDATE price_history SET price=0 WHERE id=900001");
        execute("UPDATE scan_class SET auto_threshold=0,map50=1 WHERE id=1");
        execute("UPDATE scan_class SET auto_threshold=1,map50=NULL WHERE id=1");
        execute("UPDATE scan_feedback SET user_id=NULL WHERE id=900001");
        assertThat(number("SELECT qty FROM fridge_item WHERE id=900001")).isZero();
    }

    @Test
    void preservesUnknownIngredientsAndSeparateExpiryBatches() throws Exception {
        execute("INSERT INTO fridge_item(fridge_id,name,qty,unit,reg_date,exp_date,exp_auto,source) VALUES (900001,'청경채',1,'개','2026-10-28','2026-10-20',FALSE,'MANUAL')");
        assertThat(number("SELECT COUNT(*) FROM fridge_item WHERE fridge_id=900001 AND name='청경채' AND ingredient_id IS NULL")).isEqualTo(2);
    }

    @Test
    void deletingDishPreservesHistoricalSnapshot() throws Exception {
        execute("DELETE FROM dish WHERE id=900001");
        assertThat(number("SELECT dish_id FROM cooking_log WHERE id=900001")).isEqualTo(900001);
        assertThat(number("SELECT COUNT(*) FROM cooking_log_ingredient WHERE log_id=900001")).isEqualTo(1);
    }

    @Test
    void feedbackForeignKeyPreventsParentDeletion() throws Exception {
        execute("INSERT INTO users(id,email,password_hash,nickname,role) VALUES (900002,'feedback@example.invalid','test-only','피드백 검증','USER')");
        execute("UPDATE scan_feedback SET user_id=900002 WHERE id=900001");
        SQLException failure = assertThrows(SQLException.class, () -> execute("DELETE FROM users WHERE id=900002"));
        assertThat(failure.getMessage()).containsIgnoringCase("fk_feedback_user");
    }

    @Test
    void upgradePreservesDataAndSeedCatalog() throws Exception {
        assertThat(Flyway.configure().dataSource(url,username,password).load().info().current().getVersion().toString()).isEqualTo("4");
        assertThat(number("SELECT COUNT(*) FROM ingredient")).isEqualTo(70);
        assertThat(number("SELECT COUNT(*) FROM recipe")).isEqualTo(560);
        assertThat(number("SELECT COUNT(*) FROM scan_class WHERE model_version='v4'")).isEqualTo(33);
        assertThat(number("SELECT qty FROM fridge_item WHERE id=900001")).isEqualTo(2);
        assertThat(number("SELECT servings_left FROM dish WHERE id=900001")).isEqualTo(1);
    }

    @Test
    void indexesFollowQueryColumnOrder() throws Exception {
        assertIndex("fridge_item", "idx_item_deduct", "fridge_id", "name", "exp_date", "id");
        assertIndex("cooking_log", "idx_log_user_kind_date", "user_id", "kind", "log_date");
        assertIndex("cooking_log", "idx_log_user_id", "user_id", "id");
    }

    @Test
    void freshDatabaseMigratesThroughAllVersions() {
        Flyway fresh = Flyway.configure().dataSource("jdbc:h2:mem:fresh_" + UUID.randomUUID()
                + ";MODE=MySQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1", "sa", "").load();
        assertThat(fresh.migrate().migrationsExecuted).isEqualTo(4);
        fresh.validate();
    }

    void execute(String sql) throws SQLException {
        try (Statement statement = connection.createStatement()) { statement.executeUpdate(sql); }
    }

    long number(String sql) throws SQLException {
        try (Statement statement = connection.createStatement(); ResultSet rs = statement.executeQuery(sql)) {
            rs.next();
            return rs.getLong(1);
        }
    }

    void assertIndex(String table, String index, String... expected) throws Exception {
        SortedMap<Short,String> columns = new TreeMap<>();
        try (ResultSet rs = connection.getMetaData().getIndexInfo(connection.getCatalog(),connection.getSchema(),table,false,false)) {
            while (rs.next()) {
                if (index.equalsIgnoreCase(rs.getString("INDEX_NAME"))) {
                    columns.put(rs.getShort("ORDINAL_POSITION"),rs.getString("COLUMN_NAME").toLowerCase(Locale.ROOT));
                }
            }
        }
        assertThat(columns.values()).containsExactly(expected);
    }
}
