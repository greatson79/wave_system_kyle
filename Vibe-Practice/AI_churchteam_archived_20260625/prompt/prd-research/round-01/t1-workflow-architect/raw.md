# T1 Workflow Architect — 원본 산출 (Round-01)

## 메타데이터
- 조사 차수: 1
- Teammate: Workflow Architect (t1)
- 조사 축: 구조·파이프라인 설계
- 가정 축: Claude Code 단독 완결(Branch A) vs 외부 도구 연동(Branch B)
- 생성일: 2026-04-29
- 근거 출처: Claude Code 공식 문서 기준 / AGENT_PROMPTS_ADVANCED.md / prd_teammate_executable.md

---

## Branch A: Claude Code 단독 완결

### 가능한 것
- 12개 에이전트를 `.claude/agents/*.md`로 정의
- Orchestrator가 `Agent()` 도구로 각 에이전트 순차 호출
- 직렬 파이프라인: Exegesis → Structure → Filter → Application
- 각 에이전트 독립 컨텍스트 유지
- state.yaml SOT 패턴으로 에이전트 간 상태 관리

### 한계 (기술적 제약 구체적 지점)
- **진정한 병렬 실행 불가**: Claude Code는 서브에이전트를 순차 호출함. 병렬처럼 보이는 구조도 내부적으로는 직렬.
- **Theology Filter 분기 자동화 어려움**: PASS/FAIL 분기를 Hook으로 처리하려면 Bash Hook에서 파일 상태를 읽어야 하는데, Hook의 조건 분기 지원 범위가 제한적.
- **에이전트 간 컨텍스트 공유**: 파일 경유(state.yaml)만 가능. 메모리 공유 API 없음.
- **컨텍스트 윈도우 소진**: 파이프라인이 길어질수록 단일 세션에서 context가 누적됨. 서브에이전트 호출로 격리하지 않으면 위험.

### Top 3 필수 구성요소 (Branch A)
1. Orchestrator 에이전트 파일 (라우팅 로직 전담)
2. state.yaml (단일 SOT — 에이전트 간 상태 공유)
3. `.claude/agents/` 구조 (에이전트 파일 집중 관리)

### 파킹 로트
- 원어 성경 데이터 로컬 DB 옵션 검증 필요 (BibleOL, OSIS XML, Unbound Bible)
  - 카테고리: 기술 검증
  - 이유: Exegesis Agent가 헬라어·히브리어 데이터 없이는 환각 위험 있음

---

## Branch B: 외부 도구 연동 전제

### 외부 연동이 반드시 필요한 지점
1. **원어(헬라어/히브리어) 데이터**: 로컬 성경 DB 또는 오픈 API 없이는 Exegesis Agent 환각 위험 매우 높음
2. **Theology Filter**: 규칙이 복잡할수록 Python Hook이 LLM 판단보다 신뢰성 높음. 규칙 기반 검증은 코드가 프롬프트보다 추적 가능.
3. **산출물 저장/버전 관리**: 파일시스템 스크립트 필요 (state.yaml 쓰기 자동화)

### 연동의 위험
- 외부 의존성 증가 → 로컬 환경마다 설치·설정 달라짐
- 목사(비개발자) 환경에서 Python 스크립트 설치는 진입장벽
- 버전 관리 복잡도 증가

### Top 3 필수 구성요소 (Branch B)
1. Python Hook (Theology Filter 규칙 기반 검증)
2. 로컬 성경 DB (원어 데이터)
3. 파일시스템 자동화 스크립트 (산출물 저장·버전 관리)

### 파킹 로트
- Theology Filter를 Python Hook으로 구현 시 목사의 설치 복잡도 수용 가능 여부
  - 카테고리: 사용자 행동 가설 검증
  - 발견 Branch: B
  - 이유: ABSOLUTE ANCHOR ①(품질)과 운용성 간 충돌 지점

---

## Branch A vs B 비교 정리

| 항목 | Branch A (단독) | Branch B (연동) |
|------|----------------|----------------|
| 신학 필터 신뢰성 | LLM 판단 — 일관성 변동 가능 | Python 규칙 — 추적 가능, 일관성 높음 |
| 원어 분석 품질 | 환각 위험 있음 | 로컬 DB로 보완 가능 |
| 설치 복잡도 | 낮음 (Claude Code만) | 높음 (Python, DB 추가) |
| 유지보수 | Claude Code 구조 의존 | 외부 의존성 관리 부담 추가 |

### 결론 (Architect)
Branch A+B 혼합이 현실적. Claude Code 에이전트 구조(A)를 뼈대로, Theology Filter와 원어 데이터만 Python Hook·로컬 DB로 보강(B). 완전 단독 완결은 신학 정확도를 담보할 수 없어 ABSOLUTE ANCHOR ①(품질) 위반 위험.

### 후속 확인 필요 항목
- Claude Code의 현재 Hook에서 Python 스크립트 실행 시 로컬 환경 의존성 처리 방법 확인
- 로컬 성경 DB 옵션 구체적 비교 (설치 난이도, 데이터 완전성, 라이선스)
