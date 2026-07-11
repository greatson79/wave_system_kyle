# PRD 제작 방향 조언 (Round-02 — 기술·이론 축)

## 메타데이터
- 조사 차수: 2 / 생성일: 2026-04-29
- 조사 축: 기술·이론 축
- 성격: 방향 조언 (PRD 본문 아님)

---

## 조언 T-1: 기술 전제 섹션을 PRD 앞부분에 추가하라

현재 PRD(churchTeamPRD.md)에 기술 전제 섹션이 없다. 없으면 구현 시 잘못된 가정 위에 설계한다.

```
## 기술 전제 (Technical Constraints)
- 실행 환경: 로컬 MacOS, Claude Code Max 단독
- 자동 트리거: 불가 (사용자 슬래시 커맨드 개시 필수) [LOCAL-BLOCKED]
- 병렬 실행: Phase 2 이후 점진 도입 (Phase 1은 순차)
- 상태 관리: YAML 파일 기반 SOT (인메모리 상태 없음)
- 신학 필터: 2중 방어 (프롬프트 1차 + Hook 키워드 2차)
- LOCAL-BLOCKED 항목: Logos/Accordance (SaaS), Claude Code 단독 자동 실행
```

---

## 조언 T-2: 설정 아키텍처를 PRD 아키텍처 섹션에 다이어그램으로 포함하라

구현자가 처음부터 올바른 구조로 시작하게 하려면 .claude/ 디렉터리 구조가 PRD에 있어야 한다.

권장 구조:
```
.claude/
├── CLAUDE.md                    (경량 TOC, 200라인 이하)
│   ├── 절대 기준 (신학, 로컬 실행, SOT)
│   ├── 에이전트 registry (이름 + 스킬 경로)
│   └── 슬래시 커맨드 목록
├── skills/
│   ├── orchestrator/SKILL.md
│   ├── sermon-pipeline/SKILL.md
│   ├── theology-filter/SKILL.md
│   ├── exegesis/SKILL.md
│   ├── discipleship/SKILL.md
│   └── operations/SKILL.md
├── hooks/scripts/
│   ├── theology_guard.py        (PostToolUse 키워드 차단)
│   └── state_manager.py         (SessionStart/Stop 상태 복원)
└── commands/                    (슬래시 커맨드)
```

---

## 조언 T-3: Theology Filter를 독립 설계 항목으로 격상하라

현재 PRD에서 신학 제약은 Rules 섹션에만 있다. 기술 컴포넌트로 별도 섹션이 필요하다.

포함할 내용:
- 1차 방어: 모든 에이전트 프롬프트에 개혁주의 신학 제약 삽입 [LOCAL-OK]
- 2차 방어: PostToolUse Hook이 금지 키워드/패턴 탐지 [LOCAL-OK]
- 검증 방법: 신학 회귀 테스트 케이스 최소 20개 (Round-03 조사 필요)
- 최종 판단: 목회자 승인 (자동화로 대체 불가 — 이론적 근거: Anthropic 신뢰성 경고 2024)

---

## 조언 T-4: 에이전트별 로컬 실행 가능성 표를 PRD에 포함하라

| 에이전트 | 핵심 기능 | 로컬 실행 | 외부 의존 | 폴백 |
|---------|---------|---------|---------|-----|
| ExegesisAgent | 원어 분석 | LOCAL-PARTIAL | 원어 DB | OSIS XML 로컬 설치 |
| TheologyAgent | 신학 검증 | LOCAL-OK | — | — |
| SermonAgent | 설교 초안 | LOCAL-OK | — | — |
| ResearchAgent | 리서치 | LOCAL-PARTIAL | NotebookLM MCP | 파일 기반 수동 주입 |
| DevotionAgent | 묵상 생성 | LOCAL-OK | — | — |
| AdminAgent | 행정 자동화 | LOCAL-OK | — | — |

---

## 조언 T-5: Phase 구조에 기술 복잡도 수준을 연동하라

| Phase | 기능 | 오케스트레이션 | 에이전트 수 | 기술 복잡도 |
|-------|-----|-------------|---------|-----------|
| Phase 1 MVP | 설교 파이프라인 | 순차(경량) | 4~5개 | 낮음 |
| Phase 2 | 묵상·행정 추가 | 병렬(고도) | 8~9개 | 중간 |
| Phase 3 | 전략 Intelligence | 완전 오케스트레이션 | 12개 | 높음 |

---

## 조언 T-6: 미조사 항목 3개를 Round-03 우선 조사 대상으로 지정하라

1. **Theology Filter 회귀 테스트 방법** — 구현 전 필수 확보 (우선도: 최고)
2. **원어 DB 로컬 설치 옵션 비교** — ExegesisAgent 설계 전 필요 (우선도: 높음)
3. **설교 파이프라인 실제 토큰 소비 측정** — Phase 1 범위 결정 근거 (우선도: 높음)

---

## 조사 품질 검증

### 1층위 (사실 확인) — 미조사 항목
- 원어 DB 구체 설치 방법: 비교 없음 (OSIS XML 언급만)
- Theology Filter 실제 신학 오류 탐지율: 측정 없음
- 설교 파이프라인 토큰 소비: 추정치(50k~100k)만, 실측 없음

### 2층위 (구조 분석) — 가장 먼저 무너지는 지점
- **Theology Filter 신뢰성**: "2중 방어"가 신학적으로 올바른지 검증 방법이 미확보
- **컨텍스트 소비량**: 추정치 기반 Phase 1 설계 → 실측과 다를 경우 Phase 범위 재조정 필요

### 3층위 (역방향 점검) — 저장에서 빠뜨린 것

| 미조사 항목 | PRD 결정 영향 |
|-----------|-------------|
| Theology Filter 회귀 테스트 방법 | 신학 품질 보증 섹션 전체 |
| 한국어 신학 용어 임베딩 특성 | 에이전트 프롬프트 언어 전략 |
| 원어 성경 로컬 DB 설치 비교 | ExegesisAgent 설계 |
| 설교 파이프라인 실제 토큰 소비 | Phase 1 MVP 범위 |
| 담임목사 실제 UX 마찰 | 사용자 채택 위험 |
| 병렬 Task 수 상한 실험 검증 | Phase 2 병렬화 안정성 |

---

## 최종 요약

1. **구현 가능하다** — Claude Code Max + 로컬 파일 기반으로 핵심 기능 전부 LOCAL-OK
2. **2개의 구조적 제약이 PRD를 바꿔야 한다** — 자동 트리거 불가, 병렬 실행 Phase 2 이후
3. **Theology Filter가 기술적으로 가장 어렵다** — 신뢰성 보증 방법 미해결
4. **Pragmatic 시나리오 권장** — Phase 1: 4~5개 에이전트 + 경량 오케스트레이션 + 2중 신학 방어
