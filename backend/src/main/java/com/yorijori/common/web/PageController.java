package com.yorijori.common.web;

import com.yorijori.common.config.AppProperties;
import com.yorijori.recipe.RecipeService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/**
 * 화면. 데모 v9처럼 한 페이지 안에서 화면을 바꾸므로 템플릿은 index.html 하나이고,
 * 주소마다 처음 열 화면(page)만 다르게 넘긴다.
 * 화면별 HTML은 templates/pages/*.html 조각으로 나뉘어 있다.
 */
@Controller
public class PageController {

    private final RecipeService recipeService;
    private final AppProperties props;

    public PageController(RecipeService recipeService, AppProperties props) {
        this.recipeService = recipeService;
        this.props = props;
    }

    @GetMapping("/")            public String home(Model m)    { return app(m, "home"); }
    @GetMapping("/fridge")      public String fridge(Model m)  { return app(m, "fridge"); }
    @GetMapping("/recipes")     public String recipes(Model m) { return app(m, "recipes"); }
    @GetMapping("/dishes")      public String dishes(Model m)  { return app(m, "dishes"); }
    @GetMapping("/cart")        public String cart(Model m)    { return app(m, "cart"); }
    @GetMapping("/items")       public String items(Model m)   { return app(m, "items"); }

    @GetMapping("/recipes/{code}")
    public String detail(@PathVariable String code, Model m) {
        m.addAttribute("recipeCode", code);
        return app(m, "detail");
    }

    @GetMapping("/login")  public String login()  { return "auth/login"; }
    @GetMapping("/signup") public String signup() { return "auth/signup"; }

    private String app(Model m, String page) {
        m.addAttribute("page", page);
        // 데모 v9의 <script id="recipeData"> 와 같은 형식의 JSON (레시피 DB → 화면)
        m.addAttribute("recipeJson", recipeService.recipeDataJson());
        m.addAttribute("modelUrl", props.scan().modelUrl());
        m.addAttribute("classesUrl", props.scan().classesUrl());
        return "index";
    }
}
