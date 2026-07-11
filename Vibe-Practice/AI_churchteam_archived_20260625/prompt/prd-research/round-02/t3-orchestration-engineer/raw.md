# T3 Orchestration Engineer — 원본 산출 (Round-02)

## 메타데이터
- 조사 차수: 2
- Teammate: Orchestration Engineer (t3)
- 조사 축: 기술·이론 축 — 오케스트레이션 구조
- 생성일: 2026-04-29
- 근거 출처: Claude Code Task tool 공식 문서 / weekly-works DAG 실무 사례 / SaaS-AgenticWorkflow RATELIMIT_FAILURE_ANALYSIS.md

---

## Branch 3.1: Lightweight Orchestration (경량)

**관점**: "단순한 파이프라인이 가장 안정적이다."

### 실행 구조
```
사용자: /설교 [본문]
Orchestrator:
  Step 1. ExegesisAgent (원어 분석)  → 완료 후 →
  Step 2. TheologyAgent (신학 검증)  → 완료 후 →
  Step 3. SermonAgent (설교 초안)    → 완료 후 →
  Step 4. ReviewAgent (품질 검토)    → 완료 후 →
  Step 5. 목회자 승인 (human 단계)

상태: state.yaml
  sermon:
    status: pending | in_progress | completed | failed
    current_step: 1~5
    step_outputs: {step1: path, step2: path, ...}
```

### 상태 관리
- 파일 기반 단순 상태 저장 (state.yaml key-value)
- 세션 간 상태 전달: state.yaml 읽기
- 체크포인트: 각 단계 완료 시 상태 파일 업데이트

### 에러 처리
- 실패 감지: 단계 출력 파일 존재 여부 확인
- 복구: 사용자 수동 재시작 (완료된 단계는 state.yaml 기반 스킵)
- 에러 로그: output/{주차}/error.log

### 한계
- 3개 파이프라인 (설교·묵상·행정) 동시 실행 불가
- 12 에이전트 전체 직렬 실행 추정 시간: 20~40분
- Discipleship + Operations를 설교와 동시에 실행 불가

**적합 조건**: Phase 1 MVP, 에이전트 4~5개, 단일 파이프라인

**로컬 실행**: LOCAL-OK

---

## Branch 3.2: Advanced Orchestration (고도)

**관점**: "자동화된 오케스트레이션이 대규모 워크플로우의 핵심이다."

### 실행 구조
```
Orchestrator:
  병렬 소환:
  ├── Task("sermon-pipeline")    → 독립 컨텍스트
  ├── Task("devotion-pipeline")  → 독립 컨텍스트
  └── Task("admin-pipeline")     → 독립 컨텍스트

  각 Task 내부:
  └── 단계별 서브에이전트 순차 호출

공유 상태: output/{주차}/status.yaml
  pipelines:
    sermon: {status, step, output_path}
    devotion: {status, step, output_path}
    admin: {status, step, output_path}
```

### 강점
1. 3개 파이프라인 동시 실행 → 총 실행 시간 최대 1/3
2. 부분 실패 격리: 행정 파이프라인 실패가 설교 파이프라인에 영향 없음
3. Orchestrator가 전체 상태 모니터링 → 관찰 가능성 확보

### 트레이드오프
- 병렬 Task 간 컨텍스트 격리: 에이전트 간 상태 공유는 파일만 가능
- 디버깅 복잡도: 어느 Task에서 실패했는지 추적 어려움
- rate limit 위험: 동시 Task 시 Claude Code Max 5배 한도도 초과 가능

### 반증 사례
- SaaS-AgenticWorkflow: 3개 Task 병렬 시 rate limit 초과로 2개 중단 기록 (RATELIMIT_FAILURE_ANALYSIS.md)
- Claude Code Max 5배 한도에서도 대규모 병렬 실행 보증 없음

**적합 조건**: Phase 2+, 에이전트 8~12개, 3개 파이프라인 분리 완료 후

**로컬 실행**: LOCAL-OK (단, rate limit 모니터링 필수)

---

## Branch 3 통합 결론

- **Phase 1 MVP: 경량 오케스트레이션 (필수)**
- **Phase 2+: 고도 오케스트레이션 점진 도입** (설교·묵상·행정 3개 파이프라인 안정화 후)
- PRD에서 Phase별 오케스트레이션 수준을 명시해야 함
- 처음부터 고도 오케스트레이션 시도 시 디버깅 불능 상태 가능성 있음
- 오케스트레이션 스펙트럼 위치: **Phase 1 경량 / Phase 2+ 고도**
