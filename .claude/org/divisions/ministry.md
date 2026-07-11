# 목회사역 사업부 헌장

> DiA Ai Edu. Solution · 사업부 · 엔진: Claude

- **미션**: 디딤교회 회중을 섬기는 주간 사역 콘텐츠 생산 및 목회 행정 지원
- **책임 범위(Owns)**: 설교·묵상·나눔지·기도카드·카드뉴스·주간총괄 (콘텐츠) + **교회 운영·행정**(AI churchteam: 주보·교적·새신자 현황·교인 검색·일정) — 재정/회계 부분은 재무·관리본부와 매트릭스 협업

---

## 시스템 구조 (2026-06-25 통합 — 느슨한 브릿지)

```
AI_churchteam (디딤 백본 오케스트레이터 · 31인)
  위치: Claude_skills/AI_churchteam/
  진입: /팀 /팀-전략분析 /팀-연간계획 /팀-월간 /팀-분기 /팀-건강
    ↓ 브릿지 호출 (AI_churchteam 측에만 추가, 대상 시스템 내부 불가침)
  weekly-works (설교·주간콘텐츠 · 1892파일)
    위치: Claude_skills/weekly-works/
    진입: /설교 /주간총괄 /주간현황
    ★내부 불가침: sermon_SKILL·research-bridge·team-leader registry
    ↓
  church-admin (교회행정)
    위치: Claude_skills/Church-Admin-AgenticWorkflow-main/church-admin/
    진입: /start "주보 만들어줘" "새신자 현황"
```

---

- **SOP**:
  1. `/팀` 진입 — AI_churchteam Lead Orchestrator 소환
  2. 주간 콘텐츠 필요 시: weekly-works 브릿지 → `/주간총괄` 또는 `/설교` 실행
  3. 교회행정 필요 시: church-admin 브릿지 → `/start` 또는 자연어 커맨드
  4. 리서치본부 gate → 예화·배경 사실 검증 (Fact Validation)
  5. 품질감사실 gate → 신학검증(agy) + 구조검증(Codex)
  6. CEO 취합 → 회장 보고
  7. 주간현황 대시보드 갱신 → 배포 준비

- **★완결성 불가침 규칙(2026-06-24, 26주차 누락 교훈)**:
  - **묵상 이미지**: `image-prompts.txt` 작성 완료 = **즉시 코덱스 자동 소환→gpt-image-2 이미지 생성(★샘플 스타일 통일·16:9)→insert-images 삽입→A4 PNG 캡쳐**. 프롬프트만 만들고 멈추면 미완료([[feedback_devotion_image_codex]]).
  - **설교 단계**: 1→2-1~2-4→3→**4-1 제목·4-2 구조·4-3 예화·4-4 아웃라인**(★4-4 스킵 금지 — **Mode A/B/C 모두 필수**)→5 원고. 단계 건너뛰기 금지(품질 우선).
    - Mode A 4-4: 나선아웃라인 (`4-4_나선아웃라인.md`)
    - Mode B 4-4: 서사 플롯 상세 아웃라인 (`4-4_플롯아웃라인.md`)
    - Mode C 4-4: M1-M5 + Bridge + Cross Impact 상세 아웃라인 (`4-4_Movement아웃라인.md`)
  - 완료 보고 전 **산출물 완결성 실측 대조**(파일 존재 ≠ 완료).
  - **★설교준비 불가침(2026-06-25 확정)**: weekly-works `sermon_SKILL.md`·`research-bridge.md`·`team-leader/agent-registry.md`·`team-leader/agent-protocol.md` = **단 한 줄도 수정 불가**. AI_churchteam 브릿지는 호출만, 내부 변경 절대 없음.

- **산출물 경로**: `Claude_skills/weekly-works/output/`
- **전속 스킬**:
  - weekly-works: sermon·weekly-devotion·small-group·sns-cardnews·prayer-doc
  - church-admin: church-admin
  - AI_churchteam: theological-reasoning·theology_filter_dual·health-dashboard
  - 브릿지: weekly-works-bridge·church-admin-bridge
  - 공통: wave-orchestrator
- **엔진**: Claude
- **영구기억**: `.claude/org/memory/ministry.md`
- **협업 라우팅**: 크리에이티브본부(비주얼)·리서치본부(예화·배경)·품질감사실(신학검증)
