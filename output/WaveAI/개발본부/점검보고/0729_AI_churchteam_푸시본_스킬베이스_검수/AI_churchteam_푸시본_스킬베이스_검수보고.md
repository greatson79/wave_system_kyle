# AI_churchteam 푸시본 스킬베이스 검수보고

## 1. 검수 대상

- 대상 저장소: `/Users/kylechoi/Desktop/Ai_works`
- 대상 경로: `목회사역본부/AI_churchteam`
- 대상 커밋: `c501c713fc68aa97c7e4543c02254ea5adf0932a`
- 커밋 제목: `feat(skill): add AI Church Team wrapper`
- 검수 기준: 현재 로컬 수정분이 아니라 **어제 실제 푸시된 위 커밋**
- 원격 확인: `origin/feat-0-mvp`가 `c501c71`을 조상으로 포함하며, 점검 시 원격 HEAD는 `647fbba63dd1c60d3731137fa4d511cad23605f8`

## 2. 최종 판정

> **ACCEPT — 스킬베이스 진입이 실제로 작동하는 하이브리드 구조**

`c501c71`에 푸시된 변경은 단순 문서가 아니라 실제 발동 가능한 `ai-churchteam` Skill wrapper다. 사용자는 `Skill(ai-churchteam)`으로 진입할 수 있고, 스킬이 요청을 적절한 팀 command 또는 보조 Skill로 라우팅한다.

다만 31인 팀의 실행 절차 전체가 Skill 하나로 옮겨진 것은 아니다. 정식 사역 실행은 기존 command·agents·state/workflow 체계를 거친다.

따라서 아래 두 표현은 모두 부정확하다.

- “결국 워크플로우로만 작업해야 한다” → **아님**. Skill 진입과 라우팅이 실제 작동한다.
- “모든 작업을 Skill 하나로 완결한다” → **아님**. 실제 실행은 workflow가 담당한다.

정확한 표현은 다음과 같다.

> **스킬로 시작하고, 워크플로우가 정식 실행을 완결한다.**

## 3. 푸시 커밋 실측

`c501c71`에는 다음 4개 변경만 포함됐다.

| 파일 | 변경 | 기능 |
|---|---:|---|
| `.claude/build_skill_registry.sh` | 1행 추가 | `ai-churchteam`을 조직 공용 Skill 레지스트리에 등록 |
| `.claude/skills/ai-churchteam` | 신규 심볼릭 링크 | 프로젝트 Skill을 조직 공용 진입점에 연결 |
| `목회사역본부/AI_churchteam/.claude/skills/ai-churchteam/SKILL.md` | 신규 | Skill 프론트매터·라우팅표·보호장치 정의 |
| `목회사역본부/AI_churchteam/.claude/skills/ai-churchteam/agents/openai.yaml` | 신규 | 표시명·설명·기본 호출 프롬프트 등록 |

공용 진입점은 일반 파일 복사가 아니라 mode `120000`의 심볼릭 링크이며, 실제 대상은 다음 경로다.

`/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam/.claude/skills/ai-churchteam`

### SKILL.md 프론트매터

- `name: ai-churchteam` 존재
- `description:` 존재
- 일반 팀 요청, 전략분석, 연간·월간·분기, 건강점검, 신학분석, 주간사역 및 교회행정 협업의 발동 조건 명시

### 등록 형태

레지스트리 빌더에 아래 매핑이 존재한다.

`ai-churchteam|목회사역본부/AI_churchteam/.claude/skills/ai-churchteam`

OpenAI metadata의 기본 호출 프롬프트도 `$ai-churchteam`을 명시한다.

## 4. 실제 Skill 발동 결과

Claude Code 2.1.220·Claude Sonnet 5 환경에서 쓰기 권한을 차단한 읽기 전용 시험으로 실제 `Skill` 도구를 2회 호출했다.

### 시험 A — 라우팅 작업

- 요청: 다음 분기 청소년부 사역 평가·준비 라우트 확인
- 호출: `Skill(ai-churchteam)`
- 도구 결과: `success: true`
- commandName: `ai-churchteam`
- 실제 선택: `/팀-분기`
- 안내: 담임목사 승인, 목회철학 SOT, 신학 필터, `state.yaml` 쓰기권한 보호

판정: **Skill 단독 라우팅 완결**

### 시험 B — 실제 산출물 완성 요청

- 요청: 다음 분기 청소년부 사역 평가·준비 보고서 실제 완성
- 호출: `Skill(ai-churchteam)`
- 도구 결과: `success: true`
- 중단 지점: `STOP_BOUNDARY`
- 첫 필수 경계: `.claude/commands/팀-분기.md`

판정: Skill은 실행 경로를 정확히 선택했지만, 보고서 작성에는 팀 구성·실행 순서·agent 호출·상태 기록이 필요하므로 workflow로 넘어갔다.

### 비변경 확인

- `.claude/state.yaml` 전후 SHA-256 동일
  `a320fff4ca45fbeee5d9ca194d9e75314ad2b7d9c0f5a68f3ea4b95d17219dc7`
- `.claude/workflow-state.yaml` 전후 SHA-256 동일
  `814bacb1a6edc03c5773bb2c302bd1b9560e200e129da86a91b9bfc351ba6050`
- 시험 중 project 파일 생성·수정·state write: 0건

## 5. 작업 가능 경계

### A. `ai-churchteam` Skill 하나로 끝나는 작업

1. 요청 유형 분류
2. `/팀`, `/팀-전략분석`, `/팀-연간계획`, `/팀-월간`, `/팀-분기`, `/팀-건강` 중 진입점 선택
3. `$health-dashboard`, `$theological-reasoning` 등 보조 Skill 필요 여부 선택
4. 선택 근거 설명
5. 담임목사 승인 필요 여부 안내
6. 목회철학 SOT·신학 필터·state 쓰기권한·bridge 보호장치 안내
7. `CLAUDE.md`와 `state.yaml`을 통한 현재 구조·상태 조회

### B. 스킬베이스 연쇄로 처리하지만 별도 Skill이 필요한 작업

| 작업 | 후속 Skill |
|---|---|
| 성경 본문·교리·신학 위험 분석 | `$theological-reasoning` |
| 6신호 건강카드 렌더 | `$health-dashboard` |

이 작업들은 스킬베이스에 속하지만 `ai-churchteam` 하나만으로 완결되지는 않는다.

### C. 반드시 workflow를 거치는 작업

| 실제 작업 | 필수 실행 경계 |
|---|---|
| 일반 팀회의·전문팀 실행 | `/팀` + Lead Orchestrator |
| 전략 보고서 | `/팀-전략분석` + 전략팀 agents |
| 연간 방향·기획 | `/팀-연간계획` + 전략·기획팀 + 담임목사 승인 |
| 월간 교육·운영 | `/팀-월간` + 실행팀 agents |
| 분기 평가·준비 | `/팀-분기` + 전략·기획·교육·운영팀 |
| 건강상태 검증·반영 | `/팀-건강` + validators + state 권한 |
| 설교·주간 콘텐츠 | `weekly-works-bridge.md` 이후 downstream workflow |
| 주보·회원·재정·행정 | `church-admin-bridge.md` 이후 downstream workflow |
| 정식 산출물 저장·완료처리 | agents + `workflow-state.yaml` + `state.yaml` |

## 6. 스킬 단독 완결이 불가능한 이유

1. `SKILL.md`는 라우팅표와 보호장치를 정의하지만 팀 실행 순서·병렬화·산출물 계약·재시도·상태 전이 로직은 갖고 있지 않다.
2. 실제 실행 절차는 `.claude/commands/팀*.md`에 존재한다.
3. 실제 실행 주체와 쓰기권한은 `.claude/agents/`에 존재한다.
4. `state.yaml`은 총괄팀장 단독 쓰기이고, 다른 Lead Orchestrator는 `workflow-state.yaml`만 쓸 수 있다.
5. 주간사역·교회행정은 bridge를 통해 별도 저장소의 command·workflow로 위임한다.

## 7. 발견된 운영 리스크

스킬 등록·발동에는 결함이 없지만, 현재 데이터에는 다음 정합성 위험이 있다.

- `pastor/philosophy/`에 철학 문서가 존재하지만 `state.yaml`의 `philosophy_exists` 값은 `false`
- `pastor/annual-plans/`의 연간기획 파일명이 workflow 기대명과 다르고 `annual_plan_exists` 값은 `false`

따라서 정식 사역 산출 전에는 workflow가 실제 파일과 SOT 플래그를 다시 검증해야 한다. 이 문제는 `c501c71`의 Skill wrapper 결함은 아니며, 기존 상태데이터 정합성 문제다.

## 8. 결론 및 잔여

- 실제 푸시된 `c501c71`은 **정상적인 Skill wrapper 전환 커밋**이다.
- 원격 계보 포함, 공용 등록, 프론트매터, 호출 메타데이터, 실제 발동을 모두 확인했다.
- Skill 진입점 전환 작업의 구현 잔여는 **0건**이다.
- 전체 팀 실행을 skill-only 구조로 바꾸는 작업은 완료된 것도, 현재 필요한 것도 아니다.
- 만약 전체 실행까지 Skill로 이전하려면 각 `/팀*` command, agent orchestration, state writer, 승인 게이트, bridge 호출, 실패 재시도를 실행형 Skill 체계 안에 다시 구현해야 하므로 별도 대규모 개편 과제다.

## 9. 근거

- 실제 발동 증거: `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/개발본부/점검보고/0729_AI_churchteam_스킬발동실측/EVIDENCE_실제발동.md`
- 기존 경계점검: `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/개발본부/점검보고/0729_AI_churchteam_스킬발동실측/AI_churchteam_스킬발동_경계점검보고.md`
- 푸시 커밋: `c501c713fc68aa97c7e4543c02254ea5adf0932a`
