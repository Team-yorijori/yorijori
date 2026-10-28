package com.yorijori.fridge;

import com.yorijori.common.exception.ApiException;
import com.yorijori.common.exception.ErrorCode;
import com.yorijori.dish.CookingLog;
import com.yorijori.dish.CookingLogRepository;
import com.yorijori.fridge.dto.AddItemRequest;
import com.yorijori.fridge.dto.AddItemResult;
import com.yorijori.fridge.dto.FridgeItemResponse;
import com.yorijori.fridge.dto.UpdateItemRequest;
import com.yorijori.ingredient.Ingredient;
import com.yorijori.ingredient.IngredientService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Clock;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Service
@Transactional(readOnly = true)
public class FridgeService {

    private static final DateTimeFormatter MD = DateTimeFormatter.ofPattern("M/d");

    private final FridgeRepository fridges;
    private final FridgeMemberRepository members;
    private final FridgeItemRepository items;
    private final IngredientService ingredientService;
    private final CookingLogRepository logs;
    private final Clock clock;
    private final InventoryMovementRepository movements;

    public FridgeService(FridgeRepository fridges, FridgeMemberRepository members, FridgeItemRepository items,
                         IngredientService ingredientService, CookingLogRepository logs, Clock clock, InventoryMovementRepository movements) {
        this.fridges = fridges;
        this.members = members;
        this.items = items;
        this.ingredientService = ingredientService;
        this.logs = logs;
        this.clock = clock;
        this.movements = movements;
    }

    public LocalDate today() { return LocalDate.now(clock); }

    @Transactional
    public Fridge createDefaultFridge(Long userId, String name) {
        Fridge f = fridges.save(new Fridge(name.length() > 50 ? name.substring(0, 50) : name));
        members.save(new FridgeMember(f.getId(), userId, FridgeMember.Role.OWNER));
        return f;
    }

    /** 회원의 냉장고. 지금은 첫 번째 냉장고. TODO(백) 가족 공유 시 화면에서 고른 냉장고 */
    public Long fridgeIdOf(Long userId) {
        return members.findByUserIdOrderByIdAsc(userId).stream().findFirst()
                .map(FridgeMember::getFridgeId)
                .orElseThrow(() -> new ApiException(ErrorCode.FRIDGE_NOT_FOUND));
    }

    public List<FridgeItemResponse> list(Long userId) {
        LocalDate today = today();
        return items.findByFridgeIdOrderByExpDateAscIdAsc(fridgeIdOf(userId)).stream()
                .filter(f -> f.getQty() > 0)
                .map(f -> FridgeItemResponse.of(f, today)).toList();
    }

    /** 재료 등록 (데모 addItem). 소비기한: 직접 입력 > 기준표 보관 일수 > 7일 */
    @Transactional
    public List<AddItemResult> add(Long userId, AddItemRequest req) {
        Long fridgeId = fridgeIdOf(userId);
        LocalDate today = today();
        List<AddItemResult> out = new ArrayList<>();
        for (AddItemRequest.Item it : req.items()) {
            Optional<Ingredient> ing = ingredientService.resolve(it.name());
            String name = ing.map(Ingredient::getName).orElse(it.name().trim());
            LocalDate exp;
            boolean auto;
            String msg;
            if (it.expDate() != null) {
                exp = it.expDate(); auto = false;
                msg = name + " 추가 · 소비기한 " + exp.format(MD) + " (직접 입력)";
            } else if (ing.isPresent()) {
                exp = today.plusDays(ing.get().getFridgeDays()); auto = true;
                msg = name + " 추가 · 소비기한 " + exp.format(MD) + " 자동 안내 (냉장 " + ing.get().getFridgeDays() + "일 기준)";
            } else {
                exp = today.plusDays(IngredientService.UNKNOWN_DAYS); auto = true;
                msg = name + "은(는) 보관 기간 정보가 없어 " + IngredientService.UNKNOWN_DAYS + "일로 잡았습니다. 내 식재료에서 고칠 수 있습니다.";
            }
            double qty = it.qty() != null && it.qty() > 0 ? it.qty() : ing.map(Ingredient::getDefaultQty).orElse(1.0);
            String unit = ing.map(Ingredient::getUnit).orElse("개");
            String source = it.source() == null ? "MANUAL" : it.source();
            FridgeItem saved = items.save(new FridgeItem(fridgeId, ing.orElse(null), name, qty, unit, today, exp, auto, source));
            recordMovement(saved, userId, null, InventoryMovement.EventType.ADD, 0, saved.getQty());
            out.add(new AddItemResult(FridgeItemResponse.of(saved, today), msg));
        }
        return out;
    }

    @Transactional
    public FridgeItemResponse update(Long userId, Long itemId, UpdateItemRequest req) {
        FridgeItem f = items.findForUpdateByIdAndFridgeId(itemId, fridgeIdOf(userId))
                .orElseThrow(() -> new ApiException(ErrorCode.ITEM_NOT_FOUND));
        double before = f.getQty();
        if (req.qty() != null) f.changeQty(req.qty());
        if (Double.compare(before, f.getQty()) != 0) {
            recordMovement(f, userId, null, InventoryMovement.EventType.ADJUST, before, f.getQty());
        }
        if (Boolean.TRUE.equals(req.resetAuto())) {
            int days = f.getIngredient() == null ? IngredientService.UNKNOWN_DAYS : f.getIngredient().getFridgeDays();
            f.changeExp(f.getRegDate().plusDays(days), true);
        } else if (req.expDate() != null) {
            f.changeExp(req.expDate(), false);
        }
        if (f.getQty() <= 0) { items.delete(f); return null; }
        return FridgeItemResponse.of(f, today());
    }

    /** 재료 버리기 — 기록을 남긴다 (이번 달 "버린 것" 통계) */
    @Transactional
    public void toss(Long userId, Long itemId) {
        FridgeItem f = items.findForUpdateByIdAndFridgeId(itemId, fridgeIdOf(userId))
                .orElseThrow(() -> new ApiException(ErrorCode.ITEM_NOT_FOUND));
        CookingLog log = CookingLog.tossIngredient(userId, f.getName(), f.getQty(), today()).inFridge(f.getFridgeId());
        logs.save(log);
        recordMovement(f, userId, log.getId(), InventoryMovement.EventType.TOSS, f.getQty(), 0);
        items.delete(f);
    }

    /* ---------- 다른 서비스에서 쓰는 것 ---------- */

    /** 이름별 보유 현황 (수량 > 0 만) */
    public Map<String, Stock> stockMap(Long fridgeId) {
        LocalDate today = today();
        Map<String, Stock> map = new HashMap<>();
        for (FridgeItem f : items.findByFridgeIdOrderByExpDateAscIdAsc(fridgeId)) {
            if (f.getQty() <= 0) continue;
            long d = f.daysLeft(today);
            map.merge(f.getName(), new Stock(f.getName(), f.getQty(), d),
                    (a, b) -> new Stock(a.name(), a.qty() + b.qty(), Math.min(a.soonest(), b.soonest())));
        }
        return map;
    }

    /**
     * 요리 완료 차감 — 소비기한이 가까운 것부터 뺀다 (데모 openDeduct)
     * @return 실제로 뺀 양
     */
    @Transactional
    public double deduct(Long userId, Long fridgeId, String name, double need, Long cookingLogId) {
        double left = need, taken = 0;
        for (FridgeItem f : items.findByFridgeIdAndNameAndQtyGreaterThanOrderByExpDateAscIdAsc(fridgeId, name, 0)) {
            if (left <= 0) break;
            double before = f.getQty();
            double t = f.take(left);
            if (Double.compare(before, f.getQty()) != 0) {
                recordMovement(f, userId, cookingLogId, InventoryMovement.EventType.COOK, before, f.getQty());
            }
            left -= t; taken += t;
        }
        items.deleteEmpty(fridgeId);
        return taken;
    }

    private void recordMovement(FridgeItem item, Long actor, Long logId, InventoryMovement.EventType type,
                                double before, double after) {
        movements.save(new InventoryMovement(item, actor, logId, type, before, after, LocalDateTime.now(clock)));
    }
}
