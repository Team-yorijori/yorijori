package com.yorijori.flow;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * 데모 v9 의 주요 흐름을 API 로 한 번에:
 * 가입 → 재료 등록(스캔처럼 여러 개) → 추천 → 못 먹는 재료 → 요리 완료 → 먹기 → 이번 달 기록 → 장보기
 */
@SpringBootTest
@AutoConfigureMockMvc
class ApiFlowTest {

    @Autowired MockMvc mvc;
    @Autowired ObjectMapper om;

    @Test
    void mainFlow() throws Exception {
        MockHttpSession s = new MockHttpSession();

        // 로그인 전에는 401
        mvc.perform(get("/api/fridge/items")).andExpect(status().isUnauthorized());

        // 가입 (가입하면 바로 로그인)
        post(s, "/api/auth/signup", "{\"email\":\"test@yorijori.kr\",\"password\":\"password1\",\"nickname\":\"테스트\"}");

        // 재료 등록 — 동의어(달걀 → 계란), 기준표에 없는 재료(청경채 → 7일)
        JsonNode add = post(s, "/api/fridge/items", """
            {"items":[{"name":"두부","source":"SCAN"},{"name":"달걀","qty":10},{"name":"대파"},{"name":"김치","qty":500},{"name":"청경채"}]}""");
        assertThat(add.at("/data/items/1/item/name").asText()).isEqualTo("계란");
        assertThat(add.at("/data/items/4/message").asText()).contains("7일");

        // 두부 소비기한을 내일로 → 두부가 든 레시피가 위로
        long tofuId = add.at("/data/items/0/item/id").asLong();
        mvc.perform(patch("/api/fridge/items/" + tofuId).session(s).contentType(MediaType.APPLICATION_JSON)
                .content("{\"expDate\":\"" + java.time.LocalDate.now(java.time.ZoneId.of("Asia/Seoul")).plusDays(1) + "\"}"))
                .andExpect(status().isOk());

        JsonNode rec = get(s, "/api/recipes/recommend?sort=urgent&size=5");
        assertThat(rec.at("/data/items").size()).isGreaterThan(0);
        assertThat(rec.at("/data/items/0/urgent/name").asText()).isEqualTo("두부");
        String code = rec.at("/data/items/0/code").asText();

        // 못 먹는 재료: 대두 → 두부·간장이 든 레시피가 빠진다
        mvc.perform(put("/api/me/avoid").session(s).contentType(MediaType.APPLICATION_JSON)
                .content("{\"groups\":[\"대두\"],\"items\":[],\"show\":false}")).andExpect(status().isOk());
        JsonNode rec2 = get(s, "/api/recipes/recommend?size=60");
        rec2.at("/data/items").forEach(i -> assertThat(i.at("/avoid").size()).isZero());
        assertThat(rec2.at("/data/avoidHidden").asInt()).isGreaterThan(0);
        mvc.perform(put("/api/me/avoid").session(s).contentType(MediaType.APPLICATION_JSON)
                .content("{\"groups\":[],\"items\":[],\"show\":false}")).andExpect(status().isOk());

        // 요리 완료 → 두부 1모 차감, 만든 요리 2인분 보관, 임박 재료 살림
        JsonNode cook = post(s, "/api/recipes/" + code + "/cook", "{\"servings\":2,\"uses\":[{\"name\":\"두부\",\"qty\":1}]}");
        assertThat(cook.at("/data/deducted").asInt()).isEqualTo(1);
        assertThat(cook.at("/data/saved/0").asText()).isEqualTo("두부");
        long dishId = cook.at("/data/dish/id").asLong();

        // 방금 만든 요리는 추천에서 감점 (recent = 0)
        JsonNode detail = get(s, "/api/recipes/" + code);
        assertThat(detail.at("/data/title").asText()).isNotBlank();

        // 1인분 먹기
        JsonNode eat = post(s, "/api/dishes/" + dishId + "/eat", "{}");
        assertThat(eat.at("/data/left").asInt()).isEqualTo(1);

        JsonNode stats = get(s, "/api/stats/monthly");
        assertThat(stats.at("/data/cooked").asInt()).isEqualTo(1);
        assertThat(stats.at("/data/eaten").asInt()).isEqualTo(1);
        assertThat(stats.at("/data/saved").asInt()).isEqualTo(1);

        // 장보기: 담기 → 샀어요 → 냉장고로
        JsonNode cart = post(s, "/api/cart", "{\"names\":[\"양파\"],\"targetPrice\":3000}");
        long cartId = cart.at("/data/0/id").asLong();
        JsonNode bought = post(s, "/api/cart/" + cartId + "/bought", "{}");
        assertThat(bought.at("/data/item/name").asText()).isEqualTo("양파");
        assertThat(get(s, "/api/cart").at("/data").size()).isZero();

        // 화면
        mvc.perform(get("/")).andExpect(status().isOk());
        mvc.perform(get("/api/scan/classes")).andExpect(jsonPath("$.data.length()").value(33));
    }

    private JsonNode post(MockHttpSession s, String url, String body) throws Exception {
        MvcResult r = mvc.perform(org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post(url)
                        .session(s).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isOk()).andReturn();
        return om.readTree(r.getResponse().getContentAsString(java.nio.charset.StandardCharsets.UTF_8));
    }

    private JsonNode get(MockHttpSession s, String url) throws Exception {
        MvcResult r = mvc.perform(org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get(url).session(s))
                .andExpect(status().isOk()).andReturn();
        return om.readTree(r.getResponse().getContentAsString(java.nio.charset.StandardCharsets.UTF_8));
    }
}
