package com.yorijori.ingredient;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class ScanModelRelationTest {
    @Autowired MockMvc mvc;
    @Autowired JdbcTemplate jdbc;

    private MockHttpSession signup() throws Exception {
        MockHttpSession session = new MockHttpSession();
        mvc.perform(post("/api/auth/signup").session(session).contentType(MediaType.APPLICATION_JSON)
                .content("{\"email\":\"" + UUID.randomUUID() + "@scan.test\",\"password\":\"password1\",\"nickname\":\"인식검증\"}"))
                .andExpect(status().isOk());
        return session;
    }

    @Test
    void unknownModelIsRejectedEvenWithNoRows() throws Exception {
        mvc.perform(post("/api/scan/feedback").session(signup()).contentType(MediaType.APPLICATION_JSON)
                .content("{\"modelVersion\":\"missing\",\"rows\":[]}"))
                .andExpect(status().isBadRequest()).andExpect(jsonPath("$.code").value("INVALID_INPUT"));
    }

    @Test
    void nestedInvalidRowsAndOutOfRangeScoresAreRejected() throws Exception {
        MockHttpSession session = signup();
        for (String row : new String[]{"null", "{\"predicted\":\"\",\"corrected\":\"두부\"}",
                "{\"predicted\":\"달걀\",\"corrected\":\"두부\",\"score\":1.1}",
                "{\"predicted\":\"달걀\",\"corrected\":\"두부\",\"score\":-0.1}"}) {
            mvc.perform(post("/api/scan/feedback").session(session).contentType(MediaType.APPLICATION_JSON)
                    .content("{\"modelVersion\":\"v4\",\"rows\":[" + row + "]}"))
                    .andExpect(status().isBadRequest()).andExpect(jsonPath("$.code").value("INVALID_INPUT"));
        }
    }

    @Test
    void aliasesResolveRelationsWhileOriginalTextAndUnknownCorrectionsSurvive() throws Exception {
        mvc.perform(post("/api/scan/feedback").session(signup()).contentType(MediaType.APPLICATION_JSON)
                .content("{\"modelVersion\":\"v4\",\"consent\":true,\"rows\":[{\"predicted\":\"달걀\",\"corrected\":\"두부\",\"score\":0.9},{\"predicted\":\"달걀\",\"corrected\":\"이름없는재료\"}]}"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.data").value(2));
        var rows = jdbc.queryForList("SELECT f.predicted, f.corrected, f.predicted_class_id, f.corrected_ingredient_id FROM scan_feedback f ORDER BY f.id DESC LIMIT 2");
        assertThat(rows).hasSize(2);
        assertThat(rows.get(0).get("predicted")).isEqualTo("달걀");
        assertThat(rows.get(0).get("corrected_ingredient_id")).isNull();
        assertThat(rows.get(1).get("corrected_ingredient_id")).isEqualTo(jdbc.queryForObject("SELECT id FROM ingredient WHERE name='두부'", Long.class));
        Long expected = jdbc.queryForObject("SELECT s.id FROM scan_class s JOIN ingredient i ON i.id=s.ingredient_id WHERE s.model_version='v4' AND i.name='계란'", Long.class);
        assertThat(rows.get(0).get("predicted_class_id")).isEqualTo(expected);
    }

    @Test
    void multipleClassesForOneIngredientLeavePredictionUnlinked() throws Exception {
        jdbc.update("INSERT INTO scan_class(model_version,class_id,en_name,ingredient_id,auto_threshold) SELECT 'v4',999,'egg_extra',id,0.8 FROM ingredient WHERE name='계란'");
        mvc.perform(post("/api/scan/feedback").session(signup()).contentType(MediaType.APPLICATION_JSON)
                .content("{\"modelVersion\":\"v4\",\"rows\":[{\"predicted\":\"달걀\",\"corrected\":\"두부\"}]}"))
                .andExpect(status().isOk());
        assertThat(jdbc.queryForObject("SELECT predicted_class_id FROM scan_feedback ORDER BY id DESC LIMIT 1", Long.class)).isNull();
    }
}
