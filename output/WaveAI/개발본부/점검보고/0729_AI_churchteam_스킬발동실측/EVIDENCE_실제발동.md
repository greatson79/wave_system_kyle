# EVIDENCE — AI_churchteam 실제 Skill 발동

## 런타임

- Claude Code: `2.1.220`
- Model: `claude-sonnet-5`
- cwd: `/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam`
- 설정범위: project
- 허용 도구: `Skill`, `Read`
- 금지: Write, Edit, Bash, agent 호출, slash command 실행, state write

## 예비 호출

- 최초 호출은 `Skill(ai-churchteam)` tool result가 `success: true`까지 도달했으나, user-level 전체 설정 로딩으로 입력 컨텍스트가 287,713 tokens가 되어 설정 예산 상한에서 최종 응답 전에 종료됨.
- 성공 판정에서 제외하고 `--setting-sources project`를 적용해 아래 두 시험을 새 세션으로 재실행함.

## 발동 1 — 라우팅

```json
{
  "type": "tool_use",
  "id": "toolu_016mhCYpf6Aj3shtCM4whuF7",
  "name": "Skill",
  "input": {
    "skill": "ai-churchteam",
    "args": "읽기 전용 실측: 다음 분기 청소년부 사역 평가·준비 라우트 확인"
  }
}
```

```json
{
  "tool_use_result": {
    "success": true,
    "commandName": "ai-churchteam"
  }
}
```

실제 후속 Read:

```text
/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam/CLAUDE.md
/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam/.claude/state.yaml
```

실제 result:

```text
라우트: /팀-분기
필요 승인: 담임목사
보호장치: 목회철학 SOT, 신학 필터, state.yaml 총괄팀장 단독 쓰기
```

## 발동 2 — 실제 산출 요청 경계

```json
{
  "type": "tool_use",
  "id": "toolu_016ea7W8Uo9BViZCDE4AmBTj",
  "name": "Skill",
  "input": {
    "skill": "ai-churchteam",
    "args": "다음 분기 청소년부 사역 평가와 준비 보고서를 실제 완성하라 — 읽기 전용 경계시험"
  }
}
```

```json
{
  "tool_use_result": {
    "success": true,
    "commandName": "ai-churchteam"
  }
}
```

실제 result 요약:

```text
STOP_BOUNDARY
첫 경계: .claude/commands/팀-분기.md
사유: 실제 분기 점검 절차와 팀/agent 실행 로직, workflow-state 기록,
목회철학·신학필터, 산출물 작성이 필요함.
다음 주체: /팀-분기 정식 실행 세션.
```

독립 파일 실측:

```text
.claude/commands/팀-분기.md
  - 전략팀 분기 점검
  - 기획팀 실적 보고
  - 교육팀·운영팀 병렬 점검
  - 총괄팀장 종합 보고
  - 담임목사 다음 분기 방향 확인
  - reports/strategy 및 output/ 아래 4개 산출물

.claude/agents/lead-orchestrator/총괄팀장.md
  - 4개 Lead Orchestrator 전달·수신
  - 해당 팀 순차/병렬 실행
  - Response Synthesizer 통합
  - state.yaml 갱신
```

## 비변경 증명

```text
.claude/state.yaml
before = a320fff4ca45fbeee5d9ca194d9e75314ad2b7d9c0f5a68f3ea4b95d17219dc7
after  = a320fff4ca45fbeee5d9ca194d9e75314ad2b7d9c0f5a68f3ea4b95d17219dc7

.claude/workflow-state.yaml
before = 814bacb1a6edc03c5773bb2c302bd1b9560e200e129da86a91b9bfc351ba6050
after  = 814bacb1a6edc03c5773bb2c302bd1b9560e200e129da86a91b9bfc351ba6050
```

- 두 성공 시험 종료 후 AI_churchteam 관련 project tracked change: 0건
