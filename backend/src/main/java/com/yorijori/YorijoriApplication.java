package com.yorijori;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 요리조리 (냉장고를 부탁해)
 * 냉장고 재료를 사진 한 장으로 등록하고, 소비기한이 임박한 재료부터 쓰는 레시피를 추천한다.
 */
@SpringBootApplication
@EnableScheduling
@ConfigurationPropertiesScan
public class YorijoriApplication {
    public static void main(String[] args) {
        SpringApplication.run(YorijoriApplication.class, args);
    }
}
