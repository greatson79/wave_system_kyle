# reviewer-codex 재검수 — capture-full-a4 R2

```yaml
verdict: REVISE
justification: >-
  정규식 allowlist와 path.resolve 상대경계 검사는 ../, 경로구분자, 전각 숫자·문자 우회를
  browser launch 전에 종료 코드 1로 차단한다. 그러나 경계 검사는 문자열 경로만 평가하고
  fs.realpath 또는 lstat 심링크 검증을 하지 않는다. output 하위의 html-with-images 또는 captured가
  외부를 가리키는 심링크이면 경계 검사를 통과한 뒤 외부 HTML을 읽거나 외부 경로에 PNG를 쓸 수 있다.
  의뢰 범위가 명시한 심링크 우회 검증을 충족하지 못했으므로 커밋 전 보완이 필요하다.
evidence:
  - claim: "MONTH_PATTERN/WEEK_PATTERN은 ASCII 숫자 N월·N주차만 수용하고 경로 구성 전에 종료한다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:27-40"
    verified: true
  - claim: "../, 구분자 추가, 전각 월/주차 입력은 모두 exit 1로 browser launch 전에 차단됐다."
    ref: "node capture-full-a4.js '7월' '..' / '../4주차' / '4주차/' / '７월 4주차' / '7월 ４주차' (실측: 각 exit 1, 형식 오류)"
    verified: true
  - claim: "resolve 기반 상대경계 검사는 srcDir/outDir의 문자열 경로를 outputRoot와 비교한다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:42-56"
    verified: true
  - claim: "node --check는 통과했다."
    ref: "node --check /Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js (실측: exit 0)"
    verified: true
issues:
  - severity: major
    where: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:48-66,85-86"
    what: "isWithinOutputRoot는 path.resolve 결과만 검사한다. srcDir 또는 outDir 경로 구성요소가 외부를 가리키는 심링크여도 검사값은 outputRoot 하위여서 통과하며, readdirSync/page.goto 또는 screenshot이 심링크 대상 외부에 도달한다."
    fix: "입력 디렉터리에는 fs.realpathSync(srcDir) 후 real path가 real output root 하위인지 검증한다. 출력 경로는 구성요소별 lstat로 심링크를 거부하거나, realpath한 부모가 output root 하위인지 검증한 뒤 mkdir·screenshot을 수행한다. 검증 실패는 현재처럼 browser launch 전에 exit 1로 중단한다."
missing:
  - "srcDir/outDir 심링크 외부지향 케이스의 fail-closed 회귀 검증"
```
