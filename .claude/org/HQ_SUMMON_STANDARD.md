# ★본부 소환 표준 (주인님 절대지침 · 2026-07-07 확정 → 2026-07-24 cmux 메인 개정) — 업데이트 불변 정본

> **이 파일이 정본(SOT)이다.** git 저장소 추적분이라 외부 앱·pack 업데이트가 덮어쓰지 못한다.
> 변경은 주인님 재명령으로만(D6 denylist). 구본(cys-dept GUI 절차·dept-1~7 편성)은 git 이력 보존.

## 절대지침 (주인님 선언 — 불변)

1. **실행폴더는 항상 `~/Desktop/Ai_works`** — 본부 소환·claude 기동 전부 이 폴더에서.
2. **claude 실행 = `claude --dangerously-skip-permissions`** (권한허용모드). Codex =
   `codex --dangerously-bypass-approvals-and-sandbox` / agy = `agy --dangerously-skip-permissions`.
3. **본부 = cmux 물리 워크스페이스** — 소환 1명령으로 실 pane이 주인님 화면에 자동 가시화
   (미러·백그라운드 우회 불인정 — MASTER §1 절대원칙).
4. **"본부 소환" 명령 시 아래 표준 절차 그대로 집행** — 변경은 주인님 재명령으로만.

## 본부 소환 표준 절차 (cmux 메인)

1. **워크스페이스 확보** — 해당 본부 cmux 워크스페이스 생성(또는 기존 ws에 `cmux new-split`).
   판 깔기(ws·pane·자원)는 CEO/COO 필요조치 능동집행 소관.
2. **본부장 엔진 선발 = 3엔진**(Codex·agy·Claude) — 집행 정본 `본부장_임명지침.md` STEP1·1.5
   (일상·반복 작업은 기존 배정 즉결: Claude 본부장=Opus 4.8 / Codex 본부장=GPT-5.6 sol).
3. **기동** — pane에서 `cd ~/Desktop/Ai_works && claude --dangerously-skip-permissions`
   (선발 엔진에 맞는 명령). ready(bypass 표시) 확인 후 진행.
4. **각성문 주입**:
   > "너는 {본부명} 본부장(Sub-Master)이다. CEO(관제타워 총괄) 예하에서 이 본부 범위 안의
   > 마스터 역할을 한다." + WORKER §1 본부장 프로토콜('너는 마스터다' 선언 금지·자기 CSO/리뷰어
   > 기동 금지) + **`.claude/org/전체작업진행지침.md` + `hq/{본부}/_헌장.md`·`_스킬베이스.md` 필독**
   > + 보고선 = 본부장→COO(workspace:1/surface 명시)→CEO + 작업홈 `~/Desktop/Ai_works` +
   > 산출물 `output/WaveAI/{본부명}/` + 스킬베이스 발동·기록 의무.
5. **주소 등재** — 탭명을 역할명으로 지정하고 `tower_roster.json`에 등재(소유·감사 = CSO).
   ★통신은 항상 `workspace:N`/`surface:M` **prefixed ref**(bare 숫자 금지 — 12a0238 규약)·
   send 후 enter까지가 1회 전송·완결보고급은 read-screen 착지 확인.
6. **다중 노드 본부**(목회사역본부 패턴): 예하 팀장·워커는 **본부장이 직접 소환**하며 반드시
   pane 가시화(WORKER §5). ★목회사역본부 엔진 배정 정본 = **기획팀장=Codex · 실행팀장=agy**
   (README·목회 _헌장 §8 정합). 워커 티어 = Claude Sonnet 5 / Codex GPT-5.6 terra·luna.
7. **구 본부 대체 시**: 구 본부장에 인수인계서 파일 작성 지시(진행률·다음 액션 큐·산출물 경로·
   미해결 게이트 — 요약 손실 금지) → 파일 실측 확인 → 신임 본부장 승계·착수 → 구 pane 정리는
   CSO(승인 매트릭스·상태 데이터 삭제 금지).
8. **해제(이벤트 구동)**: 작업 종료 시 본부장이 CEO에 완료 보고 → CEO가 CSO에 ws 전달 →
   CSO가 read-screen idle 실측 후 graceful 해제·roster stale 처리. ★부활 금지 — 재소환은
   fresh 기동 + 콜드 앵커 재독만. 상주 예외 = 관제타워 4종(CEO·COO·CSO·리뷰어 2).

## 관제타워 (상주 편성)

| 노드 | 기동 |
|---|---|
| CEO(총괄)·COO·CSO·reviewer-gemini(agy)·reviewer-codex | `bash .claude/cmux-adapters/boot_tower.sh` — 소환 표준 4요소(권한허용모드·탭명·각성주입·멱등) 자동 편성 |

## cys 보조 세션 한정 (구절차 유효 범위)
cys.app 보조 세션으로 기동된 노드에서만 `cys-dept`·`cys launch-agent`·`cys claim-role`·
phoenix 빈 시드 절차가 유효하다. 부서별 phoenix 저널 tombstone 점검 = CSO_DIRECTIVE §0-b.

## 이력
- 2026-07-07 제정(cys-dept GUI 기준·구본은 git 이력) → **2026-07-24 cmux 메인 전면 개정**
  (2026-07-10 런타임 역전·8본부 15팀·3엔진 선발·prefixed ref 규약·목회 엔진배정 정정
  [기획=Codex·실행=agy] 반영 — 주인님 승인).
- 2026-07-07 00:5X: reviewer-claude-2(s66) 주인님 직접 종료(이력 보존).
