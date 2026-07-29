# AI_churchteam 스킬 발동·작업 경계 실측 보고

- 점검일시: 2026-07-29 14:11~14:14 KST
- 점검대상: `/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam`
- 배포 commit: `c501c713fc68aa97c7e4543c02254ea5adf0932a`
- 원격상태: `c501c71`이 현재 `origin/feat-0-mvp`의 조상임을 실측
- 점검방식: Claude Code 2.1.220 / Claude Sonnet 5에서 성공한 실제 `Skill` 도구 호출 2회, 읽기 전용 경계시험, 상태파일 전후 SHA-256 대조

## 1. 최종 판정

`ai-churchteam`은 **실제로 발동되는 스킬베이스 진입점**이다. 다만 스킬 자체가 31인 팀의 실행 로직을 대체한 것은 아니다.

정확한 경계는 다음과 같다.

> **스킬 단독:** 요청 분류, 진입점 선택, 필요한 승인·보호장치 안내까지.
>
> **워크플로우 필수:** 팀 소환, 순차·병렬 실행, 실제 사역 산출물 작성, 진행상태 기록, 최종 상태 갱신까지.

따라서 어제 보고의 “하이브리드 구조”는 맞지만, “전환완료·잔여 0”은 **스킬 진입점 등록 작업에 한해서만 맞다**. 전체 사역 실행까지 스킬 단독으로 전환됐다는 뜻으로 읽히면 과대 판정이다.

## 2. (a) Skill 도구 실제 발동 결과

### 시험 1 — 라우팅 완결

- 입력: “다음 분기 청소년부 사역 평가와 준비를 시작하려면 어떤 라우트인가”
- 실제 도구 호출:
  - `name: Skill`
  - `skill: ai-churchteam`
  - tool result: `success: true`
  - commandName: `ai-churchteam`
- 스킬 로딩 기준경로:
  - `/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam/.claude/skills/ai-churchteam`
- 스킬이 실제로 읽은 파일:
  - `/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam/CLAUDE.md`
  - `/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam/.claude/state.yaml`
- 실제 선택 결과: `/팀-분기`
- 실제 안내 결과: 담임목사 승인, 목회철학 SOT, 신학 필터, `state.yaml` 총괄팀장 단독 쓰기 권한
- 종료상태: success

### 시험 2 — 실제 산출 요청의 첫 경계

- 입력: “다음 분기 청소년부 사역 평가와 준비 보고서를 실제 완성하라”
- 제약: 스킬 필수 읽기만 허용하고 파일쓰기·슬래시 명령·agent 호출·state write 금지
- 실제 `Skill(ai-churchteam)` 발동: success
- 실제 결과: `STOP_BOUNDARY`
- 첫 워크플로우 경계:
  - `/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam/.claude/commands/팀-분기.md`
- 사유: 스킬은 `/팀-분기`를 선택하지만, 분기 평가의 팀 구성·실행 순서·산출물 규격은 해당 command와 하위 agent 정의에만 존재함.

### 비변경 검증

- `.claude/state.yaml`
  - 전/후 SHA-256: `a320fff4ca45fbeee5d9ca194d9e75314ad2b7d9c0f5a68f3ea4b95d17219dc7`
- `.claude/workflow-state.yaml`
  - 전/후 SHA-256: `814bacb1a6edc03c5773bb2c302bd1b9560e200e129da86a91b9bfc351ba6050`
- 두 시험에서 project 파일 생성·수정·state write: 0건

### 예비 호출 이력

- 최초 예비 호출에서도 `Skill(ai-churchteam)` 자체는 `success: true`였으나, user-level 전체 설정이 만든 287,713-token 입력 컨텍스트 때문에 설정한 예산 상한에서 최종 응답 전에 종료됐다.
- 이 예비 호출은 성공 시험으로 집계하지 않았고, `--setting-sources project`로 범위를 제한한 뒤 위 두 시험을 새 세션에서 다시 실행해 둘 다 success로 종료했다.

## 3. (b) 스킬 단독 범위와 워크플로우 필수 범위

### A. `ai-churchteam` 스킬 하나로 끝나는 범위

1. 사용자의 요청을 아래 진입점 중 하나로 분류
   - `/팀`
   - `/팀-전략분석`
   - `/팀-연간계획`
   - `/팀-월간`
   - `/팀-분기`
   - `/팀-건강` + `$health-dashboard`
   - `$theological-reasoning`
2. 선택된 라우트와 선택 이유 설명
3. 담임목사 승인 필요 여부 안내
4. 목회철학 SOT·신학 필터·state 권한·브릿지 불변경 보호장치 안내
5. `CLAUDE.md`와 `state.yaml`을 읽어 현재 팀 구성과 상태를 조회

이 범위는 시험 1에서 실제로 완료됐다.

### B. 스킬베이스 연쇄로 가능하지만 `ai-churchteam` 단독은 아닌 범위

1. 성경 본문·교리 분석
   - `ai-churchteam`이 `$theological-reasoning`을 선택한 뒤 별도 Skill을 다시 발동해야 함.
2. 6신호 건강카드 형식 렌더
   - `$health-dashboard` 별도 Skill이 필요함.
   - 현재 두 Skill은 분석 프레임·렌더 규격을 제공하지만, 실제 상태 검증·갱신 로직 전체를 대신하지 않음.

즉 “스킬베이스 체인”에는 속하지만 “ai-churchteam 한 스킬만으로 완결”되는 작업은 아니다.

### C. `.claude/commands`·agents·state/workflow를 반드시 거치는 범위

| 실제 작업 | 필수 경계 | 파일 실측 근거 |
|---|---|---|
| 일반 팀회의·전문팀 선택 후 실행 | `/팀` + Lead Orchestrator | `CLAUDE.md`가 5인 Lead Orchestrator와 총 31인 팀을 정의 |
| 시대·문화·목회 전략 보고서 | `/팀-전략분석` + 전략팀 6인 | command가 6단계 agent 실행과 `reports/strategy/` 산출을 정의 |
| 연간 방향·연간 기획 | `/팀-연간계획` + 전략팀·기획팀 + 담임목사 2회 승인 | command가 5단계 실행과 2개 정본 파일 생성을 정의 |
| 월간 교육·운영 결과 | `/팀-월간` + 실행팀장·교육팀장·운영팀장 | command가 병렬 실행과 3개 output 파일을 정의 |
| 분기 평가·다음 분기 준비 | `/팀-분기` + 전략·기획·교육·운영팀 + 총괄팀장 | command가 4단계 팀 실행, 종합보고, 담임목사 확인, 4개 산출물을 정의 |
| 실제 건강 검증과 상태 반영 | `/팀-건강`, validators, state 권한 | health Skill은 기준·표시 형식이고 command는 state 값을 읽어 표시함 |
| 설교·주간 콘텐츠·주간 진척 | `weekly-works-bridge.md` + downstream workflow | bridge가 `/주간총괄`, `/설교`, `/주간현황`으로 외부 시스템에 위임 |
| 주보·회원·재정·교회행정 | `church-admin-bridge.md` + downstream workflow | bridge가 church-admin의 `/start` 및 산출물 경로에 위임 |
| 모든 정식 산출물 저장·완료처리 | agents + `workflow-state.yaml` + `state.yaml` | Intent Interpreter가 workflow-state를 기록하고 총괄팀장만 state를 최종 갱신 |

## 4. (c) 스킬베이스 단독 작업이 불가한 항목과 사유

### 구조적 사유

1. `SKILL.md`는 **라우팅표와 보호장치**만 보유한다.
   - 팀 실행 순서, 병렬화, 입력자료 조합, 산출물 템플릿, 실패 재시도, 상태 전이 로직이 없음.
2. 실제 실행 정의는 command에 있다.
   - 예: `/팀-분기`는 전략→기획→교육·운영 병렬→총괄 종합→담임목사 확인 순서를 정의.
3. 실행 주체와 쓰기 권한은 agent에 있다.
   - 총괄팀장: `state.yaml` 단독 쓰기.
   - Intent Interpreter 등 Lead Orchestrator: `workflow-state.yaml` 진행상태 기록.
   - Response Synthesizer: `reports/` 보고서 작성.
4. downstream 작업은 bridge를 넘어 별도 저장소의 command/skill/workflow를 호출해야 한다.

### 현재 데이터 정합성 사유

- 실제 `pastor/philosophy/`에는 `목회철학.md`, `설교철학.md`, `핵심가치.md`가 존재하지만 `state.yaml`은 `philosophy_exists: false`로 남아 있다.
- 실제 `pastor/annual-plans/`에는 `2026-연간예획.md`가 있으나 workflow가 요구하는 `2026-연간기획.md`와 파일명이 다르고, `state.yaml`은 `annual_plan_exists: false`다.

따라서 정식 사역 산출 전에 workflow가 파일 실재와 SOT 플래그를 재검증해야 한다. 스킬이 상태값만 읽고 곧바로 최종 산출하면 누락 또는 잘못된 대기 판정을 낼 수 있다.

## 5. CEO·주인님께 보고할 수정 결론

1. **실제 스킬 발동:** 가능, 성공 실측 완료.
2. **스킬 단독 완결:** 요청 분류·라우팅·승인/보호장치 안내까지 가능.
3. **스킬베이스 체인:** 신학분석·건강카드 등 별도 Skill로 이어지는 보조 작업 가능.
4. **정식 사역 실행:** 현재도 workflow 기반. command·agents·workflow-state/state 권한·산출물 쓰기를 반드시 거침.
5. **어제 “잔여 0”의 적용범위:** 스킬 wrapper 등록·원격 push에는 잔여 0. 전체 사역의 skill-only 전환에는 해당하지 않음.
6. **추가 전환이 필요하다면:** 각 `/팀*` command를 실행형 Skill로 승격하고 agent orchestration·state writer·산출물 계약·bridge 호출·재시도/승인 게이트를 Skill 체계 안에 다시 구현해야 하므로 별도 중대 개편 과업임.

## 증거 파일

- `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/개발본부/점검보고/0729_AI_churchteam_스킬발동실측/EVIDENCE_실제발동.md`
