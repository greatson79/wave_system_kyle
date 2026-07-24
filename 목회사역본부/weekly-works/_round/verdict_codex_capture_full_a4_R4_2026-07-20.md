# reviewer-codex 재검수 — capture-full-a4 R4

```yaml
verdict: ACCEPT
justification: >-
  R3의 outputRoot 심링크 우회는 workspaceRoot/outputRoot lstat 거부와 realpath 정확 일치
  검증으로 해소됐다. 입력 실경로와 출력 구성요소 심링크는 최초 검증 및 각 page.goto/screenshot
  직전에 재검증된다. 마지막 순간의 경로 교체와 hardlink 공격은 단일 소유자 수동실행 환경에서는
  동일 권한의 스크립트 변조가 가능한 공격자라는 명시된 위협모델 밖이며, 다중사용자/CI 전환 시
  FD 고정·전용 권한 디렉터리 재평가 의무가 헤더에 기록돼 있다. 현 계약 범위에서 fail-closed
  경계와 회귀 요건을 충족한다.
evidence:
  - claim: "workspaceRoot와 outputRoot는 lstat로 심링크 거부되고, outputRoot 실경로는 realWorkspaceRoot/output와 정확히 일치해야 한다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:78-91"
    verified: true
  - claim: "입력은 realpath 경계로, 출력은 전체 구성요소 lstat로 검증되며 오류는 browser launch 전에 exit 1로 종료된다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:93-113"
    verified: true
  - claim: "각 page.goto와 screenshot 직전에 assertCapturePaths를 재실행하고 실패 시 exitCode 1을 설정한 뒤 finally에서 browser를 닫는다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:124-157"
    verified: true
  - claim: "../·구분자·전각 문자/숫자 입력은 모두 exit 1이며 node --check는 성공했다."
    ref: "node capture-full-a4.js '7월' '..' / '../4주차' / '4주차/' / '７월 4주차' / '7월 ４주차'; node --check /Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js (실측)"
    verified: true
  - claim: "실제 outputRoot는 심링크가 아니며 output/99월 테스트 픽스처는 남아 있지 않다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/output (lstat 실측: symlink=false); /Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/output/99월 (실측: 부재)"
    verified: true
  - claim: "TOCTOU·hardlink의 잔여 한계와 다중사용자/CI 이관 시 재평가 방침은 헤더에 명시되어 있다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:19-23"
    verified: true
issues: []
missing: []
```
