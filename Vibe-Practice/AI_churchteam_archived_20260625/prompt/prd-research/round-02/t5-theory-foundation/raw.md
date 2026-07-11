# T5 Theory Foundation Expert — 원본 산출 (Round-02)

## 메타데이터
- 조사 차수: 2
- Teammate: Theory Foundation Expert (t5)
- 조사 축: 기술·이론 축 — 에이전틱 이론 + 자동화 원칙
- 생성일: 2026-04-29
- 근거 출처: 학술 논문 (원저자·발표년도 명시) / Anthropic 공식 문서 / AgenticWorkflow 실무 검증

---

## Branch 5.1: Modern Agentic Theory (최신 에이전틱 이론)

**관점**: "최신 이론이 에이전틱 워크플로우 설계의 미래를 결정한다."

---

### 1. ReAct (Reasoning + Acting) 패턴

**원저자·출처**: Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", ICLR 2023
**핵심 원칙**: LLM이 Thought(추론) → Action(행동) → Observation(관찰) 루프를 반복하며 목표 달성

**이 시스템 적용**
- Orchestrator가 "다음 에이전트 선택 추론 → Task 호출 → 산출물 관찰 → 재추론" 루프로 동작 가능
- Claude 3.5 Sonnet 이상은 이 패턴을 자연스럽게 따름 (Anthropic 공식 문서)

**전제 조건**
- Orchestrator 프롬프트에 ReAct 루프 명시 필요
- 각 단계 관찰 결과를 다음 추론에 주입하는 메커니즘 필요

**트레이드오프**
- 추론 단계가 길어질수록 컨텍스트 소진 가속
- 루프 반복 횟수 상한 설정 필요 (무한 루프 방지)

**한계**
- 신학 콘텐츠처럼 오류 비용이 높은 도메인: ReAct 루프만으로 신학적 정확성 보증 불가
- 목회자 최종 검토 단계가 이론보다 우선

**로컬 실행**: LOCAL-OK

---

### 2. Multi-Agent Collaboration Theory

**원저자·출처**:
- Li et al., "MetaGPT: Meta Programming for Multi-Agent Collaborative Framework", arXiv 2023
- Park et al., "Generative Agents: Interactive Simulacra of Human Behavior", Stanford UIST 2023

**핵심 원칙**: 역할 분화(Role specialization) + 구조화된 커뮤니케이션 프로토콜

**이 시스템 적용**
- 12 에이전트 역할 분화 (Exegesis/Theology/Sermon/Operations 등)가 이 이론의 직접 구현
- 에이전트 간 커뮤니케이션: 파일 기반 SOT (인메모리 공유 불가 → 이 시스템의 제약)

**트레이드오프**
- 에이전트 수 증가 시 커뮤니케이션 오버헤드 기하급수 증가
- 12개 에이전트는 이미 상당한 복잡도

**반증 사례**
- MetaGPT의 실험 환경은 완전 자동화 전제 (사용자 개입 없음)
- 이 시스템은 목회자 판단이 필수 → 완전 자동화 이론 그대로 적용 불가
- 적용 가능한 부분: 역할 분화 원칙 + 파일 기반 커뮤니케이션 패턴

**로컬 실행**: LOCAL-OK

---

### 3. Self-Reflection / Self-Critique 패턴

**원저자·출처**: Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning", NeurIPS 2023

**핵심 원칙**: 에이전트가 자신의 산출물을 스스로 비판하고 개선

**이 시스템 적용**
- Theology Filter 에이전트가 설교 초안을 신학적으로 자기 검토하는 역할로 적용

**한계**
- 자기 비판 루프가 항상 올바른 신학 판단을 보장하지 않음
- LLM의 자기 비판은 편향 증폭 위험 (동일 모델이 생성 + 검토)
- **목회자의 최종 승인으로 보완 필수**

**로컬 실행**: LOCAL-OK

---

### 4. 최근 2년 패턴 (2024~2025)

**Agentic RAG (Retrieval-Augmented Generation)**
- 에이전트가 필요한 정보를 자율 검색·합성
- 이 시스템 적용: 원어 DB + 신학 자료 검색에 적용 가능
- 로컬 실행: LOCAL-OK (로컬 DB 전제)

**Tool Use / Function Calling 표준화**
- Anthropic Tool Use API가 에이전트 도구 호출 표준화
- Claude Code의 Task tool이 이 패턴의 구현체

**Anthropic 자체 한계 인정**
- 출처: Anthropic Safety Policy, 2024
- "현재 에이전틱 시스템은 신뢰성이 낮다"고 명시
- **신학 콘텐츠처럼 오류 비용이 높은 도메인에서는 인간 검토 단계가 필수**

---

### 이론과 현실의 갭 (최신 이론)

| 이론 | Claude Code 현실 | 타협점 |
|-----|---------------|------|
| ReAct: 완전 자동 루프 | 사용자 개시 필수 | 슬래시 커맨드 → ReAct 루프 시작 |
| Multi-Agent: 실시간 커뮤니케이션 | 파일 기반 비동기만 가능 | state.yaml SOT로 대체 |
| Self-Critique: 신뢰성 보장 | LLM 편향 증폭 위험 | 목회자 최종 검토 필수 |

**이론 근거의 탄탄함**: 8/10
**이 이론에 근거한 구현 난이도**: 중간 (Claude Code 제약 수용 필요)

---

## Branch 5.2: Established Automation Theory (검증된 자동화 원칙)

**관점**: "검증된 원칙이 가장 신뢰할 수 있는 기초다."

---

### 1. Unix 철학 (1978~)

**원저자**: Ken Thompson, Dennis Ritchie (Bell Labs)
**원칙**: 한 가지 일을 잘 하는 작은 도구 + 파이프라인 조합

**이 시스템 적용**
- 각 에이전트 = 단일 책임 (Exegesis는 원어만, Theology는 검증만)
- Orchestrator = 파이프라인 조합자
- .claude/skills/theology-filter/ 독립 분리 = Unix 철학 구현

**에이전틱 시스템에서 주의점**
- Unix 파이프와 달리 에이전트 파이프라인은 컨텍스트 병목 발생
- 에이전트 수 최소화 필요 (Unix의 "작은 도구"를 너무 많이 쌓으면 오히려 복잡)

**검증 기간**: 47년 (1978~2025)
**로컬 실행**: LOCAL-OK

---

### 2. 멱등성 원칙 (Idempotency)

**원칙**: 같은 입력에 대해 여러 번 실행해도 같은 결과

**에이전틱 시스템에서의 현실**
- LLM 기반 에이전트는 구조적으로 멱등성 불가 (동일 프롬프트 → 다른 출력)
- **대안**: 체크포인트(status.yaml)로 이미 완료된 단계 스킵 → 유사 멱등성 확보
- 결론: 완전 적용 불가, 부분 적용(체크포인트)으로 보완

**로컬 실행**: LOCAL-OK

---

### 3. 실패 격리 (Bulkhead Pattern)

**원칙**: 한 컴포넌트 실패가 전체 시스템에 전파되지 않도록 격리

**이 시스템 적용**
- Task tool 독립 컨텍스트: 설교 파이프라인 실패 → 묵상 파이프라인 영향 없음
- Phase 1: 단일 파이프라인이라 격리 단순
- Phase 2+: Task tool로 격리 완전 구현

**검증 기간**: 마이크로서비스 아키텍처 패턴, 2010년대 이후 광범위 검증
**로컬 실행**: LOCAL-OK

---

### 4. 상태 머신 설계 (Finite State Machine)

**원칙**: 시스템 상태를 유한 상태 집합으로 명시. 전이 조건 명확히 정의.

**이 시스템 적용**
```yaml
# state.yaml 상태 머신 예시
sermon:
  status: pending | in_progress | completed | failed
  current_step: 1~5
  transitions:
    pending → in_progress: 슬래시 커맨드 실행 시
    in_progress → completed: 모든 단계 통과 시
    in_progress → failed: 에러 발생 + 목회자 중단 시
```

**이 시스템에서 핵심 원칙**
- weekly-works에서 status.md 활용으로 이미 검증됨
- Orchestrator가 상태 머신을 읽어 다음 단계 결정

**검증 기간**: 수십 년 (자동화·제어 공학 기초)
**로컬 실행**: LOCAL-OK

---

### 고전 원칙 vs 에이전틱 현실 종합

| 원칙 | 에이전틱 시스템에서 | 비고 |
|-----|---------------|-----|
| 멱등성 | 부분 적용 (LLM 비결정적) | 체크포인트로 보완 |
| 실패 격리 | 완전 적용 가능 | Task tool 활용 |
| Unix 파이프라인 | 적용 가능 (컨텍스트 병목 유의) | 에이전트 수 최소화 |
| 상태 머신 | 완전 적용 가능 | state.yaml SOT |
| DRY | 적용 가능 | 스킬 파일 재사용 |
| 관심사 분리 | 완전 적용 가능 | 에이전트 역할 분화 |

**이론적 확실성**: 9/10
**미래 유효성**: 높음 (구조 원칙은 LLM 시대에도 유효)

---

### 이론과 현실의 갭 (검증 원칙)

- "멱등성": 에이전틱 시스템에서 부분만 적용 가능 → 체크포인트로 보완
- "DRY": 스킬 파일 재사용으로 적용 가능하나, 프롬프트 DRY는 추상화 과도 위험
- 타협점: 검증된 구조 원칙(상태 머신·실패 격리·관심사 분리) 적용 + LLM 특성(비결정성) 수용

---

## Branch 5 통합 결론

- 최신 에이전틱 이론(ReAct, Multi-Agent)은 이 시스템의 **설계 언어** 제공
- 고전 자동화 원칙(상태 머신, 실패 격리)은 이 시스템의 **구현 신뢰성** 보장
- **두 이론 모두 필요하며 충돌하지 않는다**
- **절대적 갭**: LLM 비결정성. 신학 콘텐츠처럼 오류 비용이 높은 도메인에서 이론이 뭐든 **목회자 검토 단계가 이론보다 우선**
- 이론 스펙트럼 위치: **균형 (설계=최신 이론, 구현=검증 원칙)**
