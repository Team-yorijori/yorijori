package com.yorijori.fridge;

import com.yorijori.user.UserService;
import com.yorijori.user.dto.SignupRequest;
import com.yorijori.fridge.dto.*;
import com.yorijori.dish.DishService;
import com.yorijori.dish.dto.CookRequest;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;
import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Transactional
class InventoryMovementFlowTest {
    @Autowired UserService users;
    @Autowired FridgeService fridge;
    @Autowired DishService dishes;
    @Autowired JdbcTemplate jdbc;
    @Autowired jakarta.persistence.EntityManager em;
    @Autowired org.springframework.transaction.PlatformTransactionManager transactionManager;
    long userId, fridgeId;
    @BeforeEach void setup() {
        userId=users.signup(new SignupRequest("stock-"+UUID.randomUUID()+"@example.invalid","password1","재고 검증")).getId();
        fridgeId=fridge.fridgeIdOf(userId);
    }
    @Test void recordsActualStockChangesAndKeepsHistoryAfterDelete() {
        long itemId=fridge.add(userId,new AddItemRequest(List.of(new AddItemRequest.Item("양파",5.0,null,"MANUAL")))).get(0).item().id();
        fridge.update(userId,itemId,new UpdateItemRequest(4.0,null,null));
        dishes.cook(userId,"r1",new CookRequest(2,List.of(new CookRequest.Use("양파",2))));
        fridge.toss(userId,itemId);
        em.flush(); em.clear();
        assertThat(jdbc.queryForList("SELECT event_type FROM inventory_movement WHERE fridge_id=? ORDER BY id",String.class,fridgeId)).containsExactly("ADD","ADJUST","COOK","TOSS");
        assertThat(jdbc.queryForList("SELECT qty_delta FROM inventory_movement WHERE fridge_id=? ORDER BY id",Double.class,fridgeId)).containsExactly(5.0,-1.0,-2.0,-2.0);
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM inventory_movement WHERE fridge_id=? AND actor_user_id=? AND item_ref_id=? AND fridge_item_id IS NULL",Long.class,fridgeId,userId,itemId)).isEqualTo(4);
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM cooking_log WHERE user_id=? AND fridge_id=?",Long.class,userId,fridgeId)).isEqualTo(2);
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM cooking_log_ingredient l JOIN ingredient i ON l.ingredient_id=i.id JOIN cooking_log c ON l.log_id=c.id WHERE c.user_id=? AND i.name='양파'",Long.class,userId)).isEqualTo(1);
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM inventory_movement WHERE fridge_id=? AND event_type IN ('COOK','TOSS') AND cooking_log_id IS NOT NULL",Long.class,fridgeId)).isEqualTo(2);
    }
    @Test void quantityZeroKeepsAdjustmentSnapshotAndExpiryOnlyEditDoesNotInventMovement() {
        long id=fridge.add(userId,new AddItemRequest(List.of(new AddItemRequest.Item("청경채",1.0,null,"SCAN")))).get(0).item().id();
        fridge.update(userId,id,new UpdateItemRequest(null,fridge.today().minusDays(2),null));
        fridge.update(userId,id,new UpdateItemRequest(0.0,null,null));
        em.flush(); em.clear();
        assertThat(jdbc.queryForList("SELECT event_type FROM inventory_movement WHERE fridge_id=? ORDER BY id",String.class,fridgeId)).containsExactly("ADD","ADJUST");
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM inventory_movement WHERE fridge_id=? AND ingredient_id IS NULL AND item_name='청경채' AND qty_after=0",Long.class,fridgeId)).isEqualTo(1);
    }

    @Test
    void tinyCookingAmountDoesNotInventConsumptionWhenRoundedStockStaysSame() {
        fridge.add(userId,new AddItemRequest(List.of(new AddItemRequest.Item("양파",1.0,null,"MANUAL"))));
        var result=dishes.cook(userId,"r1",new CookRequest(1,List.of(new CookRequest.Use("양파",0.001))));
        em.flush(); em.clear();
        assertThat(result.deducted()).isZero();
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM cooking_log_ingredient i JOIN cooking_log l ON i.log_id=l.id WHERE l.user_id=?",Long.class,userId)).isZero();
    }

    @Test
    @Transactional(propagation=org.springframework.transaction.annotation.Propagation.NOT_SUPPORTED)
    void failedTransactionRollsBackStockAndMovementTogether() {
        var tx=new org.springframework.transaction.support.TransactionTemplate(transactionManager);
        org.junit.jupiter.api.Assertions.assertThrows(IllegalStateException.class,()->tx.executeWithoutResult(status->{
            fridge.add(userId,new AddItemRequest(List.of(new AddItemRequest.Item("양파",3.0,null,"MANUAL"))));
            throw new IllegalStateException("rollback probe");
        }));
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM fridge_item WHERE fridge_id=?",Long.class,fridgeId)).isZero();
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM inventory_movement WHERE fridge_id=?",Long.class,fridgeId)).isZero();
    }

    @Test
    @Transactional(propagation=org.springframework.transaction.annotation.Propagation.NOT_SUPPORTED)
    void simultaneousAdjustmentsKeepAContinuousMovementChain() throws Exception {
        long id=fridge.add(userId,new AddItemRequest(List.of(new AddItemRequest.Item("양파",100.0,null,"MANUAL")))).get(0).item().id();
        int workers=12;
        var start=new java.util.concurrent.CountDownLatch(1);
        var pool=java.util.concurrent.Executors.newFixedThreadPool(workers);
        List<java.util.concurrent.Future<?>> futures=new ArrayList<>();
        try {
            for(int i=1;i<=workers;i++) {
                double quantity=i;
                futures.add(pool.submit(()->{
                    try { start.await(); } catch(InterruptedException e) { Thread.currentThread().interrupt(); throw new RuntimeException(e); }
                    fridge.update(userId,id,new UpdateItemRequest(quantity,null,null));
                }));
            }
            start.countDown();
            for(var future:futures) future.get(20,java.util.concurrent.TimeUnit.SECONDS);
        } finally { pool.shutdownNow(); }
        var rows=jdbc.queryForList("SELECT qty_before,qty_after FROM inventory_movement WHERE fridge_id=? ORDER BY id",fridgeId);
        assertThat(rows).hasSize(workers+1);
        double previous=0;
        for(var row:rows) {
            assertThat(((Number)row.get("qty_before")).doubleValue()).isEqualTo(previous);
            previous=((Number)row.get("qty_after")).doubleValue();
        }
        assertThat(jdbc.queryForObject("SELECT qty FROM fridge_item WHERE id=?",Double.class,id)).isEqualTo(previous);
    }

    @Test
    void consumingFractionalStockNeverIncreasesIt() {
        long id=fridge.add(userId,new AddItemRequest(List.of(new AddItemRequest.Item("양파",0.006,null,"MANUAL")))).get(0).item().id();
        var cooked=dishes.cook(userId,"r1",new CookRequest(1,List.of(new CookRequest.Use("양파",0.001))));
        em.flush(); em.clear();
        assertThat(cooked.deducted()).isZero();
        assertThat(jdbc.queryForObject("SELECT qty FROM fridge_item WHERE id=?",Double.class,id)).isEqualTo(0.006);
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM inventory_movement WHERE fridge_id=?",Long.class,fridgeId)).isEqualTo(1);
    }

    @Test
    @Transactional(propagation=org.springframework.transaction.annotation.Propagation.NOT_SUPPORTED)
    void cookingRefreshesPreloadedStockAfterConcurrentAdjustment() throws Exception {
        long id=fridge.add(userId,new AddItemRequest(List.of(new AddItemRequest.Item("양파",10.0,null,"MANUAL")))).get(0).item().id();
        var tx=new org.springframework.transaction.support.TransactionTemplate(transactionManager);
        var pool=java.util.concurrent.Executors.newSingleThreadExecutor();
        try {
            tx.executeWithoutResult(status->{
                // 요리 트랜잭션의 1차 캐시에 10개를 먼저 로드한다.
                fridge.stockMap(fridgeId);
                try {
                    pool.submit(()->fridge.update(userId,id,new UpdateItemRequest(7.0,null,null)))
                            .get(15,java.util.concurrent.TimeUnit.SECONDS);
                } catch(Exception e) { throw new RuntimeException(e); }
                dishes.cook(userId,"r1",new CookRequest(1,List.of(new CookRequest.Use("양파",2.0))));
            });
        } finally { pool.shutdownNow(); }
        assertThat(jdbc.queryForObject("SELECT qty FROM fridge_item WHERE id=?",Double.class,id)).isEqualTo(5.0);
        assertThat(jdbc.queryForList("SELECT qty_before FROM inventory_movement WHERE fridge_id=? ORDER BY id",Double.class,fridgeId)).containsExactly(0.0,10.0,7.0);
        assertThat(jdbc.queryForList("SELECT qty_after FROM inventory_movement WHERE fridge_id=? ORDER BY id",Double.class,fridgeId)).containsExactly(10.0,7.0,5.0);
    }
}
