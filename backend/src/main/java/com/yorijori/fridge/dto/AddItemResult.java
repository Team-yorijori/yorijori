package com.yorijori.fridge.dto;

/** 등록 결과 한 줄과 안내 문구 (데모 addItem 의 msg) */
public record AddItemResult(FridgeItemResponse item, String message) {}
