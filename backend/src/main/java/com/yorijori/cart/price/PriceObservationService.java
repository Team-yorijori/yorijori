package com.yorijori.cart.price;

import com.yorijori.cart.PriceHistory;
import com.yorijori.cart.PriceHistoryRepository;
import com.yorijori.cart.Product;
import com.yorijori.cart.ProductRepository;
import com.yorijori.ingredient.Ingredient;
import com.yorijori.ingredient.IngredientService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;

@Service
public class PriceObservationService {
    private final ProductRepository products;
    private final PriceHistoryRepository history;
    private final IngredientService ingredients;

    public PriceObservationService(ProductRepository products, PriceHistoryRepository history, IngredientService ingredients) {
        this.products = products;
        this.history = history;
        this.ingredients = ingredients;
    }

    @Transactional
    public PriceHistory observe(String name, ShopPrice price, LocalDateTime checkedAt) {
        Ingredient ingredient = ingredients.resolve(name).orElse(null);
        Product product = null;
        if (price.externalId() != null && !price.externalId().isBlank() && price.externalId().length() <= 100) {
            product = products.findByChannelAndExternalId(price.channel(), price.externalId())
                    .orElseGet(() -> products.save(new Product(price.channel(), price.externalId(), price.title(), price.url(), ingredient)));
            product.observe(price.title(), price.url(), ingredient);
        }
        PriceHistory snapshot = new PriceHistory(name, price.channel(), price.mallName(), price.price(), price.title(), price.url(), checkedAt);
        snapshot.link(ingredient, product);
        return history.save(snapshot);
    }
}
