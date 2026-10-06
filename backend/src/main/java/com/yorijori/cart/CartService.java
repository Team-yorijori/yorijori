package com.yorijori.cart;

import com.yorijori.cart.dto.CartAddRequest;
import com.yorijori.cart.dto.CartItemResponse;
import com.yorijori.cart.dto.CartUpdateRequest;
import com.yorijori.common.exception.ApiException;
import com.yorijori.common.exception.ErrorCode;
import com.yorijori.fridge.FridgeService;
import com.yorijori.fridge.dto.AddItemRequest;
import com.yorijori.fridge.dto.AddItemResult;
import com.yorijori.ingredient.Ingredient;
import com.yorijori.ingredient.IngredientService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
public class CartService {

    private final CartItemRepository carts;
    private final IngredientService ingredientService;
    private final FridgeService fridgeService;

    public CartService(CartItemRepository carts, IngredientService ingredientService, FridgeService fridgeService) {
        this.carts = carts;
        this.ingredientService = ingredientService;
        this.fridgeService = fridgeService;
    }

    public List<CartItemResponse> list(Long userId) {
        return carts.findByUserIdOrderByIdDesc(userId).stream().map(CartItemResponse::of).toList();
    }

    /** 이미 담긴 재료는 다시 담지 않는다. 새로 담긴 것만 돌려준다 */
    @Transactional
    public List<CartItemResponse> add(Long userId, CartAddRequest req) {
        List<CartItemResponse> out = new ArrayList<>();
        for (String raw : req.names()) {
            if (raw == null || raw.isBlank()) continue;
            Optional<Ingredient> ing = ingredientService.resolve(raw);
            String name = ing.map(Ingredient::getName).orElse(raw.trim());
            if (carts.findByUserIdAndName(userId, name).isPresent()) continue;
            Integer target = req.names().size() == 1 && req.targetPrice() != null && req.targetPrice() > 0 ? req.targetPrice() : null;
            out.add(CartItemResponse.of(carts.save(new CartItem(userId, ing.orElse(null), name, target))));
        }
        return out;
    }

    @Transactional
    public CartItemResponse update(Long userId, Long id, CartUpdateRequest req) {
        CartItem c = find(userId, id);
        if (req.targetPrice() != null) c.setTargetPrice(req.targetPrice() > 0 ? req.targetPrice() : null);
        if (req.alert() != null) c.setAlert(req.alert());
        return CartItemResponse.of(c);
    }

    @Transactional
    public void delete(Long userId, Long id) {
        carts.delete(find(userId, id));
    }

    /** "샀어요" — 냉장고로 옮기고 목록에서 뺀다 */
    @Transactional
    public AddItemResult bought(Long userId, Long id) {
        CartItem c = find(userId, id);
        List<AddItemResult> r = fridgeService.add(userId,
                new AddItemRequest(List.of(new AddItemRequest.Item(c.getName(), null, null, "CART"))));
        carts.delete(c);
        return r.get(0);
    }

    /** 스캔·영수증으로 냉장고에 넣은 재료를 목록에서 뺀다. 뺀 이름을 돌려준다 */
    @Transactional
    public List<String> removeByNames(Long userId, List<String> names) {
        if (names.isEmpty()) return List.of();
        List<CartItem> hit = carts.findByUserIdAndNameIn(userId, names);
        carts.deleteAll(hit);
        return hit.stream().map(CartItem::getName).toList();
    }

    private CartItem find(Long userId, Long id) {
        return carts.findByIdAndUserId(id, userId).orElseThrow(() -> new ApiException(ErrorCode.CART_ITEM_NOT_FOUND));
    }
}
