# reviewer-codex 재검수 — capture-full-a4 R3

```yaml
verdict: REVISE
justification: >-
  R2의 srcDir/outDir 하위 심링크 우회는 realpath 입력검증과 출력 구성요소 lstat 거부로 상당 부분
  해소됐다. 그러나 outputRoot 자체는 findSymbolicLinkComponent의 root로만 쓰여 검사되지 않는다.
  outputRoot가 외부를 가리키는 심링크이면 realOutputRoot와 realSrcDir은 모두 외부 안에서 정합해
  통과하고, output 쓰기도 외부에서 이뤄진다. 또한 검증 뒤 readdir/page.goto/screenshot 전에
  디렉터리를 바꾸는 TOCTOU 경합을 막는 파일 디스크립터 기반 고정이 없다.
evidence:
  - claim: "allowlist는 ../, 경로구분자, 전각 문자·숫자 입력을 모두 exit 1로 browser launch 전에 차단한다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:27-40; R3 입력 실측(각 exit 1)"
    verified: true
  - claim: "입력은 realpath 후 real output root 하위인지 확인하고, 출력은 구성요소 심링크를 lstat로 거부한다."
    ref: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:63-76,78-96"
    verified: true
  - claim: "node --check는 통과했다."
    ref: "node --check /Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js (실측: exit 0)"
    verified: true
issues:
  - severity: major
    where: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:42-50,63-76,78-96"
    what: "outputRoot 자체는 심링크 검사에서 제외된다. outputRoot가 외부 심링크이면 realOutputRoot가 외부 경로가 되고, realSrcDir도 그 하위라서 73행 검사를 통과한다. 79행 relative도 outputRoot 문자열 아래의 구성요소만 순회하므로 root 심링크를 탐지하지 못한다."
    fix: "outputRoot와 workspaceRoot를 lstat로 심링크 거부하고, realOutputRoot가 realWorkspaceRoot/output와 정확히 일치하는지 검증한다."
  - severity: major
    where: "/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/src/scripts/capture-full-a4.js:63-96,99-121"
    what: "경로 검증 완료 뒤 readdirSync·page.goto·screenshot까지 경로를 재검증하지 않으므로 로컬 공격자가 그 사이 srcDir/outDir 또는 중간 구성요소를 심링크로 교체하는 TOCTOU 경합이 남는다."
    fix: "검증과 사용을 가능한 한 인접시키고, 각 캡처 직전 입력 realpath/출력 lstat 경계를 재확인한다. 고위험 다중사용자 환경이면 디렉터리 FD 기반 처리 또는 전용 권한 디렉터리로 공격자 쓰기권한을 제거한다."
missing:
  - "outputRoot 자체 외부 심링크 차단 회귀 검증"
  - "검증 후 심링크 교체 TOCTOU 회귀 검증 또는 위협모델상 배제 근거"
```
