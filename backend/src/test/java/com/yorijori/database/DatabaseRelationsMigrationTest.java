package com.yorijori.database;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import java.sql.*;
import java.util.UUID;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

class DatabaseRelationsMigrationTest {
    static String url, user, password;
    Connection c;
    @BeforeAll static void upgrade() throws Exception {
        url=System.getenv().getOrDefault("YORIJORI_RELATION_DB_URL","jdbc:h2:mem:relations_"+UUID.randomUUID()+";MODE=MySQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1");
        user=System.getenv().getOrDefault("YORIJORI_RELATION_DB_USERNAME","sa");
        password=System.getenv().getOrDefault("YORIJORI_RELATION_DB_PASSWORD","");
        try(Connection c=DriverManager.getConnection(url,user,password); ResultSet r=c.getMetaData().getTables(c.getCatalog(),c.getSchema(),"%",new String[]{"TABLE"})) {
            assertThat(r.next()).as("빈 전용 DB만 사용").isFalse();
        }
        Flyway.configure().dataSource(url,user,password).target("4").load().migrate();
        try(Connection c=DriverManager.getConnection(url,user,password); Statement s=c.createStatement()) {
            s.executeUpdate("INSERT INTO users(id,email,password_hash,nickname,role) VALUES(800001,'relations@example.invalid','test','검증','USER')");
            s.executeUpdate("INSERT INTO fridge(id,name) VALUES(800001,'관계 검증')");
            s.executeUpdate("INSERT INTO fridge_member(fridge_id,user_id,role) VALUES(800001,800001,'OWNER')");
            s.executeUpdate("INSERT INTO user_avoid(user_id,kind,avoid_value) VALUES(800001,'GROUP','대두'),(800001,'ITEM','오이')");
            s.executeUpdate("INSERT INTO fridge_item(id,fridge_id,ingredient_id,name,qty,unit,reg_date,exp_date,exp_auto,source) SELECT 800001,800001,id,'양파',3,'개','2026-10-28','2026-10-27',FALSE,'MANUAL' FROM ingredient WHERE name='양파'");
            s.executeUpdate("INSERT INTO dish(id,fridge_id,name,servings,servings_left,made_date,exp_date) VALUES(800001,800001,'검증 요리',2,1,'2026-10-28','2026-10-30')");
            s.executeUpdate("INSERT INTO cooking_log(id,user_id,kind,dish_id,name,amount,log_date) VALUES(800001,800001,'COOK',800001,'검증 요리',2,'2026-10-28'),(800002,800001,'TOSS_ING',NULL,'이전 재료',1,'2026-10-27')");
            s.executeUpdate("INSERT INTO cooking_log_ingredient(id,log_id,ingredient_name,qty) VALUES(800001,800001,'양파',1)");
            s.executeUpdate("INSERT INTO price_history(id,ingredient_name,channel,price,checked_at) VALUES(800001,'양파','TEST',1000,CURRENT_TIMESTAMP)");
            s.executeUpdate("INSERT INTO scan_feedback(id,user_id,model_version,predicted,corrected,consent) VALUES(800001,800001,'v4','양파','청경채',FALSE),(800002,800001,'old-test','미등록1','미등록2',FALSE)");
        }
        Flyway.configure().dataSource(url,user,password).load().migrate();
    }
    @BeforeEach void begin() throws Exception {c=DriverManager.getConnection(url,user,password);c.setAutoCommit(false);}
    @AfterEach void end() throws Exception {c.rollback();c.close();}
    @Test void movesGroupSelectionsWithoutLosingCustomItems() throws Exception {
        assertThat(n("SELECT COUNT(*) FROM user_avoid_group u JOIN avoid_group g ON u.group_id=g.id WHERE u.user_id=800001 AND g.name='대두'")).isEqualTo(1);
        assertThat(n("SELECT COUNT(*) FROM user_avoid WHERE user_id=800001 AND kind='ITEM' AND avoid_value='오이'")).isEqualTo(1);
        assertThat(n("SELECT COUNT(*) FROM user_avoid WHERE kind='GROUP'")).isZero();
        assertThrows(SQLException.class,()->sql("INSERT INTO user_avoid_group(user_id,group_id) SELECT user_id,group_id FROM user_avoid_group WHERE user_id=800001"));
    }
    @Test void backfillsOnlyKnownRelations() throws Exception {
        assertThat(n("SELECT fridge_id FROM cooking_log WHERE id=800001")).isEqualTo(800001);
        assertThat(n("SELECT COUNT(*) FROM cooking_log WHERE id=800002 AND fridge_id IS NULL")).isEqualTo(1);
        assertThat(n("SELECT COUNT(*) FROM cooking_log_ingredient l JOIN ingredient i ON l.ingredient_id=i.id WHERE l.id=800001 AND i.name='양파'")).isEqualTo(1);
        assertThat(n("SELECT COUNT(*) FROM price_history p JOIN ingredient i ON p.ingredient_id=i.id WHERE p.id=800001 AND i.name='양파' AND p.product_id IS NULL")).isEqualTo(1);
    }
    @Test void openingStockSurvivesItemDeletion() throws Exception {
        assertThat(n("SELECT COUNT(*) FROM inventory_movement WHERE fridge_id=800001 AND event_type='OPENING' AND qty_before=0 AND qty_after=3 AND qty_delta=3 AND actor_user_id IS NULL")).isEqualTo(1);
        sql("DELETE FROM fridge_item WHERE id=800001");
        assertThat(n("SELECT COUNT(*) FROM inventory_movement WHERE item_ref_id=800001 AND fridge_item_id IS NULL AND item_name='양파' AND unit='개'")).isEqualTo(1);
    }
    @Test void modelsPreserveUnknownHistoricalVersionsAndFeedbackText() throws Exception {
        assertThat(n("SELECT COUNT(*) FROM scan_model WHERE version='old-test'")).isEqualTo(1);
        assertThat(n("SELECT COUNT(*) FROM scan_feedback WHERE id=800001 AND predicted='양파' AND corrected='청경채' AND corrected_ingredient_id IS NULL AND predicted_class_id IS NOT NULL")).isEqualTo(1);
        assertThrows(SQLException.class,()->sql("UPDATE scan_feedback SET model_version='missing' WHERE id=800001"));
    }
    @Test void rejectsInventedRelationsAndInvalidMovementBalances() {
        assertThrows(SQLException.class,()->sql("UPDATE inventory_movement SET qty_delta=999 WHERE item_ref_id=800001"));
        assertThrows(SQLException.class,()->sql("UPDATE inventory_movement SET qty_after=-1 WHERE item_ref_id=800001"));
        assertThrows(SQLException.class,()->sql("UPDATE price_history SET ingredient_id=999999 WHERE id=800001"));
        assertThrows(SQLException.class,()->sql("INSERT INTO product(channel,external_id,title,package_qty) VALUES('TEST','one','양파',1)"));
    }
    @Test void migrationReachesVersion5AndKeepsSeedCatalog() throws Exception {
        assertThat(Flyway.configure().dataSource(url,user,password).load().info().current().getVersion().toString()).isEqualTo("5");
        assertThat(n("SELECT COUNT(*) FROM ingredient")).isEqualTo(70);
        assertThat(n("SELECT COUNT(*) FROM recipe")).isEqualTo(560);
    }
    void sql(String q) throws SQLException {try(Statement s=c.createStatement()){s.executeUpdate(q);}}
    long n(String q) throws SQLException {try(Statement s=c.createStatement();ResultSet r=s.executeQuery(q)){r.next();return r.getLong(1);}}

    @Test void unknownLegacyGroupIsReportedAndMigrationDoesNotDropIt() throws Exception {
        String legacy="jdbc:h2:mem:unknown_group_"+UUID.randomUUID()+";MODE=MySQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1";
        Flyway.configure().dataSource(legacy,"sa","").target("4").load().migrate();
        try(Connection x=DriverManager.getConnection(legacy,"sa","");Statement s=x.createStatement()) {
            s.executeUpdate("INSERT INTO users(id,email,password_hash,nickname,role) VALUES(800003,'legacy@example.invalid','test','검증','USER')");
            s.executeUpdate("INSERT INTO user_avoid(id,user_id,kind,avoid_value) VALUES(800003,800003,'GROUP','없는분류')");
            String preflight=java.nio.file.Files.readString(java.nio.file.Path.of("../docs/erd/preflight-v5.sql"));
            try(ResultSet r=s.executeQuery(preflight)) {
                assertThat(r.next()).isTrue();
                assertThat(r.getString("rule_name")).isEqualTo("unknown_avoid_group");
                assertThat(r.getLong("row_id")).isEqualTo(800003);
                assertThat(r.next()).isFalse();
            }
            assertThrows(org.flywaydb.core.api.FlywayException.class,
                    ()->Flyway.configure().dataSource(legacy,"sa","").load().migrate());
            try(ResultSet r=s.executeQuery("SELECT avoid_value FROM user_avoid WHERE id=800003")) {
                assertThat(r.next()).isTrue(); assertThat(r.getString(1)).isEqualTo("없는분류");
            }
        }
    }
}
