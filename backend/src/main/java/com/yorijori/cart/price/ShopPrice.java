package com.yorijori.cart.price;

/** 쇼핑몰 검색 결과 한 건 */
public record ShopPrice(String channel, String mallName, int price, String title, String url) {}
