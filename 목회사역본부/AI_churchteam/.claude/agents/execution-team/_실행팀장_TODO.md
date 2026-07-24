# 실행팀 수석팀장 — TO-DO / 작업기억

> WORKER_DIRECTIVE §12 준수. 세션 재시작·메모리 clear 시 이 파일을 먼저 읽고 복원.

## 정체
- 역할: **실행팀 수석팀장** (사역실행팀 총괄)
- 위치: cmux **workspace:6 "부교역자팀" / surface:50 "실행팀"** (tty=ttys142)
- 지휘 방식: 4개 서브팀장을 **Task sub-agent**로 지휘. **추가 cmux pane 승격 금지(4계층 금지)**.

## 관할 17인 로스터
| 서브팀 | 팀장 | 워커 3인 |
|--------|------|----------|
| 말씀팀 | 말씀팀장(opus, theological-reasoning) | sermon-structure · gospel-application · small-group-builder |
| 교육팀 | 교육팀장(sonnet) | student-coaching · parent-education · spiritual-growth-tracker |
| 콘텐츠팀 | 콘텐츠팀장(sonnet, 기도카드 직접작성) | sns-optimization · storytelling · visual-prompt |
| 운영팀 | 운영팀장(sonnet, Bash) | document-generator · data-tracker · event-planner |

## cmux 통신 레지스트리 (중요)
- **총괄팀장: workspace:1 "관제타워" / surface:1** (tty=ttys001)
- CSO: workspace:1 / surface:4 "CSO"  |  작업리뷰(Gemini): workspace:1 / surface:6
- 기획팀: workspace:6 / surface:49  |  전략팀: workspace:6 / surface:8
- ⚠️ **핵심 교훈**: cmux 터미널 안에서 `CMUX_WORKSPACE_ID` 환경변수가 모든 명령의 기본 --workspace로 적용됨.
  타 workspace의 surface로 push할 땐 **반드시 `--workspace <대상ws>`를 명시**해야 한다.
  예: `cmux send --workspace workspace:1 --surface surface:1 "..."` → `cmux send-key --workspace workspace:1 --surface surface:1 enter`
  (생략 시 "Surface is not a terminal" 에러 — surface:1이 ws6 안에서 잘못 resolve됨)

## 진행 상황
- [x] WORKER_DIRECTIVE 전문 각성
- [x] 실행팀장 + 4서브팀장 정의 로드 (워커 12인 브리프는 dispatch 시 lazy-load)
- [x] surface:1 각성완료 push 전송
- [ ] **총괄팀장 작업 명령 대기 중** ← 현재 위치

## 작업 SOP (명령 수령 시)
1. 기획팀 지시서 읽기: `reports/planning/YYYY-MM-DD-weekly-plan.md` (+ message-flow)
2. 연간기획 범위 확인: `pastor/annual-plans/`
3. 4서브팀에 Task sub-agent 병렬 배분 (독립작업 동시)
4. 각 팀 완료보고 취합 → 통합 완료보고서 → surface:1 push
5. 산출물: `output/YYYY-MM-DD/{팀}/`
