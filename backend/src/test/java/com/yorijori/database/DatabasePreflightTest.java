package com.yorijori.database;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.nio.file.*;
import java.sql.*;
import java.util.*;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;

/** V3 데이터에 대해 운영자가 실행할 실제 점검 SQL의 탐지 결과를 검증한다. */
class DatabasePreflightTest {
    static final String URL = "jdbc:h2:mem:preflight_" + UUID.randomUUID()
            + ";MODE=MySQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1";
    Connection connection;

    @BeforeAll
    static void prepareV3Data() throws Exception {
        Flyway.configure().dataSource(URL, "sa", "").target("3").load().migrate();
        try (Connection c = DriverManager.getConnection(URL,"sa",""); Statement s = c.createStatement()) {
            s.executeUpdate("INSERT INTO users(id,email,password_hash,nickname,role) VALUES (900001,'preflight@example.invalid','test-only','사전 점검','USER')");
            s.executeUpdate("INSERT INTO fridge(id,name) VALUES (900001,'점검 냉장고')");
            s.executeUpdate("INSERT INTO fridge_item(id,fridge_id,name,qty,unit,reg_date,exp_date,exp_auto,source) VALUES (900001,900001,'미등록 재료',0,'개','2026-10-28','2026-10-27',FALSE,'MANUAL')");
            s.executeUpdate("INSERT INTO dish(id,fridge_id,name,servings,servings_left,made_date,exp_date) VALUES (900001,900001,'점검 요리',2,0,'2026-10-28','2026-10-30')");
            s.executeUpdate("INSERT INTO cooking_log(id,user_id,kind,name,amount,log_date) VALUES (900001,900001,'COOK','점검 요리',0,'2026-10-28')");
            s.executeUpdate("INSERT INTO cooking_log_ingredient(id,log_id,ingredient_name,qty) VALUES (900001,900001,'미등록 재료',0)");
            s.executeUpdate("INSERT INTO cart_item(id,user_id,name) VALUES (900001,900001,'미등록 재료')");
            s.executeUpdate("INSERT INTO price_history(id,ingredient_name,channel,price,checked_at) VALUES (900001,'미등록 재료','TEST',0,CURRENT_TIMESTAMP)");
            s.executeUpdate("INSERT INTO scan_feedback(id,model_version,predicted,corrected,consent) VALUES (900001,'v4','배추','미등록 재료',FALSE)");
        }
    }

    @BeforeEach
    void begin() throws Exception {
        connection = DriverManager.getConnection(URL,"sa","");
        connection.setAutoCommit(false);
    }

    @AfterEach
    void rollback() throws Exception { connection.rollback(); connection.close(); }

    @Test
    void healthyDataAndAllowedZeroAndNullValuesProduceNoViolations() throws Exception {
        assertThat(violations()).isEmpty();
    }

    static Stream<Arguments> invalidData() {
        // 각 조건을 빼면 해당 사례를 놓친다. 기대 ID는 fixture/seed에서 독립적으로 정한다.
        return Stream.concat(DatabaseIntegrityTest.invalidValues().map(a -> {
            Object[] v = a.get();
            String sql = (String) v[1];
            return Arguments.of(v[0], sql, sql.endsWith("id=1") ? 1L : 900001L);
        }), Stream.of(Arguments.of("fk_feedback_user",
                "UPDATE scan_feedback SET user_id=999999 WHERE id=900001", 900001L)));
    }

    @ParameterizedTest(name = "{0}: {1}")
    @MethodSource("invalidData")
    void findsEachInvalidRowBeforeMigration(String rule, String sql, long id) throws Exception {
        try (Statement statement = connection.createStatement()) { statement.executeUpdate(sql); }
        assertThat(violations()).containsExactly(rule + ":" + id);
    }

    Set<String> violations() throws Exception {
        String sql = Files.readString(Path.of("../docs/erd/preflight.sql"));
        Set<String> out = new LinkedHashSet<>();
        try (Statement statement = connection.createStatement(); ResultSet rs = statement.executeQuery(sql)) {
            while (rs.next()) out.add(rs.getString("rule_name") + ":" + rs.getLong("row_id"));
        }
        return out;
    }
}
