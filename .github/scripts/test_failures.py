"""CI 백엔드 테스트가 실패했을 때 원인을 PR 화면에 주석(annotation)으로 띄운다.

- gradle.log 에서 'What went wrong' 블록과 컴파일 에러를 뽑는다.
- build/test-results/test/*.xml 에서 실패한 테스트 이름·메시지·스택 앞부분을 뽑는다.
로그인하지 않아도 PR의 Files changed / Checks 탭에서 원인을 볼 수 있다.
"""
import glob
import re
import sys
import xml.etree.ElementTree as ET

LOG = sys.argv[1] if len(sys.argv) > 1 else "gradle.log"


def esc(s: str) -> str:
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def emit(title: str, body: str) -> None:
    print(f"::error title={esc(title)}::{esc(body[:6000])}")


lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines() if glob.glob(LOG) else []

# 1) 컴파일 에러 (javac)
compile_errs = [l for l in lines if re.search(r"\.java:\d+: error:", l)]
if compile_errs:
    emit("컴파일 에러", "\n".join(compile_errs[:30]))

# 2) 실패한 테스트
count = 0
for path in sorted(glob.glob("build/test-results/test/*.xml")):
    for case in ET.parse(path).getroot().iter("testcase"):
        for tag in ("failure", "error"):
            node = case.find(tag)
            if node is None:
                continue
            count += 1
            trace = (node.text or "").strip().splitlines()
            # Caused by 줄은 끝까지 따라가서 근본 원인을 보여 준다
            causes = [l for l in trace[12:] if l.lstrip().startswith("Caused by")]
            body = "\n".join(trace[:12] + (["..."] if len(trace) > 12 else []) + causes[-4:])
            emit(f"테스트 실패: {case.get('classname', '').split('.')[-1]}.{case.get('name')}",
                 f"{node.get('message', '')}\n\n{body}")
            if count >= 8:
                sys.exit(0)

# 3) 위 둘이 없으면 Gradle 의 What went wrong 블록
if not compile_errs and count == 0:
    out, take = [], 0
    for l in lines:
        if "What went wrong" in l:
            take = 30
        if take:
            out.append(l)
            take -= 1
    emit("Gradle 실패", "\n".join(out) or "\n".join(lines[-40:]) or "gradle.log 가 없다")
