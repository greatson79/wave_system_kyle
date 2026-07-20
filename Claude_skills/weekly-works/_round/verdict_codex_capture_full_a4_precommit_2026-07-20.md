# reviewer-codex 코드리뷰 — capture-full-a4 pre-commit

```yaml
verdict: REVISE
justification: >-
  신규 스크립트는 인자 누락과 캡처 대상 부재를 종료 코드 1로 막고, browser를 finally에서 닫으며,
  fonts.ready를 기다리는 점은 적절하다. 그러나 month/week 인자를 검증하지 않은 채 path.join에
  전달하므로 ../를 포함한 입력이 workspaceRoot 밖의 로컬 HTML 경로를 가리킬 수 있다. 공유 표준
  스크립트의 경로 조작 방어 요구를 충족하지 못하므로 커밋 전 allowlist 검증 및 경계 검증이 필요하다.
evidence:
  - claim: "인자 누락과 캡처 대상 부재는 명시적 오류 후 종료 코드 1로 처리한다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:30-33,40-43,48-52"
    verified: true
  - claim: "Puppeteer browser는 launch 뒤 try/finally로 감싸져 성공·실패 시 close된다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:54-73"
    verified: true
  - claim: "페이지 이동 후 document.fonts.ready를 await하고 fullPage 캡처를 사용한다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:63-69"
    verified: true
  - claim: "capture-a4.js의 git diff는 헤더 주석 범위뿐이며 실행 로직은 변경되지 않았다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-a4.js:1-14; git -C /Users/kylechoi/Desktop/Ai_works diff -- Claude_skills/weekly-works/src/scripts/capture-a4.js (실측)"
    verified: true
  - claim: "두 파일은 Node v24.14.0에서 node --check를 통과하고 설치된 Puppeteer는 24.37.2다."
    ref: "node --check /Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js 및 capture-a4.js (실측); /Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/package.json:14"
    verified: true
issues:
  - severity: major
    where: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:28,35-38"
    what: "month와 week에 ../ 또는 플랫폼 경로 구분자가 허용된다. 예컨대 path.join(workspaceRoot, 'output', '..', '..', '매일묵상', 'html-with-images')는 /Users/kylechoi/Desktop/Ai_works/Claude_skills/매일묵상/html-with-images로 해소되어 workspaceRoot 밖을 가리킨다."
    fix: "인자를 정규식 allowlist(예: 월=^[0-9]{1,2}월$, 주차=^[0-9]{1,2}주차$)로 먼저 검증하고, path.resolve한 srcDir/outDir가 workspaceRoot/output/ 하위인지 확인한다. 실패 시 browser launch 전에 종료 코드 1로 중단한다."
missing:
  - "경로 이탈 입력에 대한 fail-closed 검증"
```
