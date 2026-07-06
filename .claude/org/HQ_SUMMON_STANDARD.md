# ★본부 소환 표준 (주인님 절대지침 · 2026-07-07 확정) — 업데이트 불변 정본

> **이 파일이 정본(SOT)이다.** cys pack 업데이트는 `~/.cys/pack/`을 덮어쓸 수 있으나(실사고:
> 2026-07-06 0.12.21 업데이트가 memory 색인 9건 소실) 이 저장소는 건드리지 못한다.
> 장기기억(`feedback_exec-home-ai-works-absolute` · `feedback_hq-summon-standard-playbook`)이
> 소실되면 **이 파일에서 재영속**한다(`javis_memory.py add`).
> 변경은 주인님 재명령으로만. 무결 점검 = `hq-standard-watch` 스케줄(매일).

## 절대지침 (주인님 선언)

1. **실행폴더는 항상 `~/Desktop/Ai_works`** — 본부 소환·claude 기동 전부 이 폴더에서.
2. **claude 실행 = `claude --dangerously-skip-permissions`** (권한허용모드).
3. **부서(dept) 생성 = 주인님이 GUI(+부서)로 직접** 한다.
4. **"본부 소환" 명령 시 아래 표준 절차 그대로 집행** — 변경은 주인님 재명령으로만.

## 본부 소환 표준 절차

1. 주인님이 GUI +부서로 dept-N 생성 → 신규 state dir(`~/.local/state/cys-dept-*`) 감지 즉시
   phoenix 2종 빈 시드(부활 방지): `phoenix/desired_roster.json` `{"roster":{},...}` ·
   `phoenix/journal-default.json` `{"ticket_id":"default","roles":{}}`.
2. 주인님이 부서명 지정 → GUI가 만든 master pane(보통 s1·빈 셸·cwd ~)에
   `cd ~/Desktop/Ai_works && claude --dangerously-skip-permissions` 주입.
3. ready(bypass 표시) 후 **부서장 각성문** 주입:
   > "너는 {본부명} 부서장(팀장·Sub-Master)이다. CEO(관제타워 master) 예하에서 이 부서 범위
   > 안의 마스터 역할을 한다." + WORKER_DIRECTIVE §1 팀장 프로토콜('너는 마스터다' 선언 금지·
   > 자기 CSO/리뷰어 기동 금지) + 보고선=본부장→COO(--to coo)→CEO + 작업홈 `~/Desktop/Ai_works` +
   > 산출물 `output/DiA/{본부명}/` + 완료 보고 push(관제타워 소켓 명시).
4. `~/.cys/depts.json`에 `display_name` 등록(fleet 표시). GUI 사이드바 이름은 주인님이 rename
   (GUI-CLI 이름 SOT 이원화 — upstream 대장 #5).
5. **다중 노드 본부**(목회사역본부 패턴): 예하 팀장은 **본부장이 직접 소환**(부서 ACL
   `external→worker*` deny 때문에 외부 소환 불가) —
   `cys launch-agent --role worker --agent codex|gemini --cwd ~/Desktop/Ai_works` + 각성문 +
   자기 surface에서 `cys claim-role <커스텀주소>`(exec-lead 등).
6. **구 부서 대체 시**: 구 팀장에 인수인계서 파일 작성 지시(진행률·다음 액션 큐·산출물 경로·
   미해결 게이트 — 요약 손실 금지) → 파일 실측 확인 → 신임 본부장 승계·착수 지시 → 구 부서
   정리는 CSO(cys-dept lifecycle 가드 CSO 전용)·상태 데이터 삭제 금지.

## 확정 편성 (2026-07-07 기본 세팅)

| 워크스페이스 | 편성 |
|---|---|
| **본부(관제타워·메인 소켓)** | CEO(master) + CSO + **coo-worker**(COO+워커 겸직·단일 노드) + reviewer-claude-2 + reviewer-gemini + reviewer-codex. worker 단독 슬롯 없음(겸직 통합 — orchestra check의 worker 부재는 승인된 예외) |
| dept-1 | **리서치본부** (본부장 claude) |
| dept-4 | **크리에이티브본부** (본부장 claude + worker-codex) |
| dept-5 | **개발본부** (본부장 claude · TransLive 담당) |
| dept-6 | **마케팅본부** (본부장 claude) |
| dept-7 | **목회사역본부** (본부장 claude + 실행팀장 codex[exec-lead] + 기획팀장 gemini[plan-lead] — 팀장 2명은 본부장 예하) |
| dept-3 | 빈 부서 예비 |

## 업데이트 후 복구 절차 (pack-update·앱 업데이트 직후 필수 점검)

1. `python3 ~/.cys/pack/bin/javis_memory.py verify` — 색인 부정합 시 memory 파일들 frontmatter로 색인 재구성.
2. 장기기억 2건(`exec-home-ai-works-absolute`·`hq-summon-standard-playbook`) 부재 시 이 파일 내용으로 `javis_memory.py add` 재영속.
3. `~/.cys/depts.json`의 display_name 5본부 확인 — 소실 시 위 편성표대로 재등록.
4. 각 부서 phoenix 빈 시드 유지 확인(전역 저널 부활 사고 방지 — upstream 대장 #3·0.12.21에서 로컬 스코핑 수정 정황).
5. `cys schedule list`에 `hq-standard-watch`(매일 08:30 무결 점검) 존재 확인 — schedule.json도 pack 내부라 업데이트에 소실될 수 있음. 부재 시 재등록:
   `cys schedule add --id hq-standard-watch --time 08:30 --to master --text "[hq-watch] 본부 표준 세팅 무결 점검 — 정본 .claude/org/HQ_SUMMON_STANDARD.md 참조"`.

## 편성 변동 이력
- 2026-07-07 00:5X: reviewer-claude-2(s66) 주인님 직접 종료 — 전략렌즈 폴백 슬롯 공석(gemini 휴면 7/13까지 — 필요 시 임시 재소환).
