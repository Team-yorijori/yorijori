import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 농림축산식품 공공데이터 포털 레시피 API 3종을 전부 받아 recipe_data 폴더에 저장한다.
 *
 * 실행 (JDK 11 이상, 컴파일 필요 없음):
 *   java RecipeFetch.java 인증키
 *
 * 결과: recipe_data/basic_0001.json, ingredient_0001.json, process_0001.json ...
 *       (1,000건씩 나눠 받은 원본 JSON 그대로)
 */
public class RecipeFetch {

    static final String BASE = "http://211.237.50.150:7080/openapi";
    static final int PAGE = 1000;

    // 이름 → 서비스 ID (포털 상세 화면의 API_URL 값)
    static final Map<String, String> SERVICES = new LinkedHashMap<>();
    static {
        SERVICES.put("basic", "Grid_20150827000000000226_1");      // 레시피 기본정보
        SERVICES.put("ingredient", "Grid_20150827000000000227_1"); // 레시피 재료정보
        SERVICES.put("process", "Grid_20150827000000000228_1");    // 레시피 과정정보
    }

    static final HttpClient HTTP = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(15)).build();

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.out.println("사용법: java RecipeFetch.java 인증키");
            return;
        }
        String key = args[0].trim();
        Path out = Path.of("recipe_data");
        Files.createDirectories(out);

        for (Map.Entry<String, String> svc : SERVICES.entrySet()) {
            String name = svc.getKey(), grid = svc.getValue();
            System.out.println("\n== " + name + " (" + grid + ") ==");

            String first = get(key, grid, 1, 1);
            String code = find(first, "\"code\"\\s*:\\s*\"([^\"]*)\"");
            String msg = find(first, "\"message\"\\s*:\\s*\"([^\"]*)\"");
            String total = find(first, "\"totalCnt\"\\s*:\\s*\"?(\\d+)");
            if (total == null) {
                System.out.println("  실패: " + code + " " + msg);
                System.out.println("  응답 앞부분: " + first.substring(0, Math.min(300, first.length())));
                continue;
            }
            int totalCnt = Integer.parseInt(total);
            System.out.println("  전체 " + totalCnt + "건");

            int saved = 0;
            for (int start = 1; start <= totalCnt; start += PAGE) {
                int end = Math.min(start + PAGE - 1, totalCnt);
                String body = get(key, grid, start, end);
                Path file = out.resolve(String.format("%s_%04d.json", name, (start - 1) / PAGE + 1));
                Files.writeString(file, body, StandardCharsets.UTF_8);
                saved += end - start + 1;
                System.out.printf("  %d ~ %d 저장 → %s%n", start, end, file.getFileName());
                Thread.sleep(300); // 서버 부담 줄이기
            }
            System.out.println("  완료: " + saved + "건");
        }
        System.out.println("\n끝. recipe_data 폴더를 압축해서 보내주면 된다.");
    }

    static String get(String key, String grid, int start, int end) throws Exception {
        String url = String.format("%s/%s/json/%s/%d/%d", BASE, key, grid, start, end);
        HttpRequest req = HttpRequest.newBuilder(URI.create(url)).timeout(Duration.ofSeconds(60)).GET().build();
        for (int attempt = 1; ; attempt++) {
            try {
                HttpResponse<String> res = HTTP.send(req, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
                return res.body();
            } catch (Exception e) {
                if (attempt >= 3) throw e;
                System.out.println("  재시도(" + attempt + "): " + e.getMessage());
                Thread.sleep(2000L * attempt);
            }
        }
    }

    static String find(String s, String regex) {
        Matcher m = Pattern.compile(regex).matcher(s);
        return m.find() ? m.group(1) : null;
    }
}
