package com.yorijori.fridge;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/** 재고 변경 원장. 재고가 삭제되어도 이름·단위·원래 행 ID와 변경량을 보존한다. */
@Entity
@Table(name="inventory_movement")
public class InventoryMovement {
    public enum EventType { OPENING, ADD, ADJUST, COOK, TOSS }
    @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
    @Column(name="fridge_id",nullable=false) private Long fridgeId;
    @Column(name="fridge_item_id") private Long fridgeItemId;
    @Column(name="item_ref_id",nullable=false) private Long itemRefId;
    @Column(name="ingredient_id") private Long ingredientId;
    @Column(name="actor_user_id") private Long actorUserId;
    @Column(name="cooking_log_id") private Long cookingLogId;
    @Column(name="item_name",nullable=false,length=50) private String itemName;
    @Column(nullable=false,length=10) private String unit;
    @Enumerated(EnumType.STRING) @Column(name="event_type",nullable=false,length=16) private EventType eventType;
    @Column(name="qty_before",nullable=false) private double qtyBefore;
    @Column(name="qty_after",nullable=false) private double qtyAfter;
    @Column(name="qty_delta",nullable=false) private double qtyDelta;
    @Column(length=10) private String source;
    @Column(name="occurred_at",nullable=false) private LocalDateTime occurredAt;
    protected InventoryMovement() {}
    public InventoryMovement(FridgeItem item, Long actor, Long logId, EventType type,
                             double before, double after, LocalDateTime at) {
        fridgeId=item.getFridgeId(); fridgeItemId=item.getId(); itemRefId=item.getId();
        ingredientId=item.getIngredient()==null?null:item.getIngredient().getId();
        actorUserId=actor; cookingLogId=logId; itemName=item.getName(); unit=item.getUnit();
        eventType=type; qtyBefore=before; qtyAfter=after; qtyDelta=after-before;
        source=item.getSource(); occurredAt=at;
    }
}
