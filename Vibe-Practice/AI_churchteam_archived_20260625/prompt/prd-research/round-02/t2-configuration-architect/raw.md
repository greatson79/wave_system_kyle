# T2 Configuration Architect — 원본 산출 (Round-02)

## 메타데이터
- 조사 차수: 2
- Teammate: Configuration Architect (t2)
- 조사 축: 기술·이론 축 — 설정 아키텍처 (CLAUDE.md·Hooks 설계)
- 생성일: 2026-04-29
- 근거 출처: Claude Code 공식 문서 / AgenticWorkflow CLAUDE.md 실제 구조 / weekly-works 실무 사례

---

## Branch 2.1: Minimal Configuration (단순 설정)

**관점**: "설정이 단순할수록 유지보수가 쉽고 에러가 적다."

### 설계 구조
```
CLAUDE.md (단일 파일)
├── 시스템 정체성 (AI 목회 보조)
├── 신학 제약 (ABSOLUTE ANCHOR)
├── 에이전트 라우팅 규칙 (12 에이전트)
└── 슬래시 커맨드 목록

.claude/
├── settings.json (2~3개 Hook)
├── skills/ (에이전트별 SKILL.md)
└── commands/ (슬래시 커맨드)
```

### 장점
1. 초기 구축 빠름 (1~2일)
2. 설정 파일 수 최소 → 디버깅 쉬움
3. 새 에이전트 추가 시 SKILL.md 1개만 추가

### 한계
- CLAUDE.md가 12 에이전트 지시 + 신학 제약 + 라우팅 모두 담으면 **컨텍스트 소비 과다** (CLAUDE.md 전체가 모든 세션에 로드됨)
- 에이전트별 세부 지시 부족 → 산출물 품질 저하 위험
- 워크플로우 종류 5개 이상 시 CLAUDE.md 비대화 불가피

**커버 가능 범위**: 에이전트 4~5개 이하, 워크플로우 2~3개

**로컬 실행**: LOCAL-OK

🅿️ 파킹 로트: CLAUDE.md 컨텍스트 소비량 정확한 측정 필요 (현재 감각치만 존재)

---

## Branch 2.2: Precision Configuration (정밀 설정)

**관점**: "세밀하게 조정된 설정이 워크플로우의 정확도와 효율을 높인다."

### 설계 구조
```
CLAUDE.md (경량 TOC, 200라인 이하)
├── 절대 기준 (신학, 로컬 실행, SOT)
├── 에이전트 registry (이름 + 스킬 경로만)
└── 슬래시 커맨드 목록

.claude/skills/
├── orchestrator/SKILL.md       ← DAG + 상태 관리
├── sermon-pipeline/SKILL.md    ← 5단계 설교 준비
├── theology-filter/SKILL.md    ← 신학 검증 로직
├── exegesis/SKILL.md
├── discipleship/SKILL.md
├── operations/SKILL.md
└── strategy/SKILL.md

.claude/hooks/scripts/
├── theology_guard.py    ← PostToolUse: 신학 위반 키워드 차단
├── state_manager.py     ← SessionStart/Stop 상태 복원
└── output_validator.py  ← 산출물 품질 검증
```

### 강점 Top 3
1. CLAUDE.md 컨텍스트 소비 최소화 (에이전트 스킬은 필요 시만 로드)
2. 에이전트별 독립 버전 관리 → 신학 필터 단독 업데이트 가능
3. Theology Filter Hook 전용 격리 → 신학 제약 강제 신뢰성 확보

### 위험
- 설정 파일 수 증가 → 초기 구축 3~4배 시간
- 파일 간 참조 오류 발생 가능
- 신규 에이전트 추가 시 registry + SKILL.md 양쪽 수정 필요

**적합 조건**: 에이전트 5개 이상, 워크플로우 3개 이상, 신학 필터 신뢰성 요구 높음

**로컬 실행**: LOCAL-OK

---

## Branch 2 통합 결론

- 이 시스템(12 에이전트 + 신학 필터 + 3 파이프라인)은 **정밀 설정이 필수**
- 단순 설정으로 시작하면 3개월 내 CLAUDE.md 비대화로 유지보수 불능
- **CLAUDE.md 경량 TOC + .claude/skills/ 분산 패턴**이 이 시스템의 요구 복잡도에 적합
- 설정 스펙트럼 위치: **정밀 80%**
