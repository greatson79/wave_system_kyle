# churchTeam — 디딤교회 AI 부교역자 시스템

이 폴더는 담임목사님의 목회와 사역을 보조하는 AI 팀 시스템입니다.

---

## 절대 기준

1. **목회철학 우선** — `pastor/philosophy/` 의 목회철학이 모든 판단의 기준입니다
2. **최종 결정권은 담임목사님** — AI는 보조이며, 어떤 결정도 목사님의 승인이 필요합니다
3. **SOT 준수** — 상태는 `state.yaml` 하나에서 관리됩니다. 총괄팀장만 씁니다
4. **신학 필터** — 모든 산출물은 신학 필터를 통과합니다

---

## 진입점

```
/팀              ← 메인 진입점 (여기서 시작하세요)
/팀-전략분석     ← 시대통찰 보고서 발행
/팀-연간계획     ← 연간목회계획 작성
/팀-월간         ← 월간 사역 실행
/팀-분기         ← 분기 점검
/팀-건강         ← 시스템 상태 확인
```

---

## 팀 구조 (31인)

```
Lead Orchestrator (5인)
    총괄팀장 · Intent Interpreter · Task Planner · Team Router · Response Synthesizer

미래목회전략팀 (6인)
    Strategy Synthesizer(팀장) · Theology Alignment · Kingdom Vision
    Culture & Generation Analyst · AI & Ministry Innovation · Scenario Planner

사역기획팀 (3인)
    기획팀장 · 주간사역설계관 · 메시지정렬관

사역실행팀 (17인)
    실행팀장
    ├── 말씀·설교팀: 말씀팀장 · 설교구조 · 현대적용 · 나눔지·묵상
    ├── 양육·교육팀: 교육팀장 · 청소년코칭 · 부모교육 · 성장추적
    ├── 콘텐츠·소통팀: 콘텐츠팀장 · SNS · 스토리텔링 · 이미지프롬프트
    └── 운영·행정팀: 운영팀장 · 문서생성 · 데이터추적 · 행사기획
```

---

## 데이터 폴더

```
pastor/philosophy/      ← 목회철학 (업로드)
pastor/annual-plans/    ← 연간방향·연간기획
pastor/reference/       ← 참고자료 (업로드)
data/church-calendar.md ← 교회 절기·행사
data/sermon-data.md     ← 설교 계획
reports/strategy/       ← 시대통찰 보고서
reports/planning/       ← 주간 기획안
reports/alignment-check/ ← 정렬 검증 결과
output/YYYY-MM-DD/      ← 실행팀 산출물
```

---

## 하위 시스템 브릿지 (느슨한 연결)

이 팀이 오케스트레이터로 호출하는 하위 시스템들. 내부는 절대 건드리지 않는다.

| 시스템 | 브릿지 파일 | 핵심 커맨드 |
|--------|-----------|-----------|
| weekly-works (설교·주간) | `.claude/skills/weekly-works-bridge.md` | `/주간총괄` `/설교` `/주간현황` |
| church-admin (교회행정) | `.claude/skills/church-admin-bridge.md` | `/start` "주보 만들어줘" 등 |

> ★weekly-works 내 sermon·research-bridge·team-leader = 단 한 줄도 수정 불가.

---

## 부모 게놈

이 시스템은 `AgenticWorkflow-Template/` 의 자식입니다.
부모의 DNA(품질 우선·SOT·CCP·4계층 검증·Adversarial Review)를 상속합니다.
상세: `runtime/inheritance-manifest/inheritance-manifest.json`
