# Wave AI Networks — 에이전트 간 실행 흐름

> 작성일: 2026-04-08
> 목적: 에이전트들이 서로 어떻게 연결되고, 어떤 순서로 작동하는지 정의

---

## 1. 기본 실행 원칙

```
모든 요청은 Chief Wave Architect(Kyle Choi)에서 시작된다.
모든 에이전트는 ON-DEMAND — 호출받을 때만 활성화된다.
에이전트는 직접 실행하지 않는다 — 반드시 Orchestrator를 통해 흐른다.
```

---

## 2. 실행 경로 (두 가지 트랙)

```
Track A — 운영 작업 (콘텐츠, 교육, 네트워크, 출판, 운영)
Chief Wave Architect
    → Flow Operations Orchestrator
        → [해당 Lead Agent]

Track B — AI 기술 작업 (에이전트 설계, 자동화 구축)
Chief Wave Architect
    → AI Systems Orchestrator
        → AI Systems Lead
```

---

## 3. 표준 실행 흐름

### Step 1. 요청 접수
```
Chief Wave Architect가 요청을 입력한다.
예: "다음 주 목회자 세미나 준비해줘"
```

### Step 2. Orchestrator 분석
```
Flow Operations Orchestrator가 요청을 받아:
1. 요청 의도 분석 (Intent Analysis)
2. 작업 분해 (Task Decomposition)
3. 담당 팀 선정 (Routing)
4. 실행 순서 설계 (Flow Control)
5. 실행 계획서 출력
```

### Step 3. Lead Agent 실행
```
각 Lead Agent가 순서에 따라 호출되어 작업 수행.
완료 시 결과를 Orchestrator에게 반환.
```

### Step 4. 통합 보고
```
Flow Operations Orchestrator가 모든 결과를 취합하여
Chief Wave Architect에게 최종 보고.
```

---

## 4. 시나리오별 실행 흐름

### 시나리오 A — 세미나 준비

```
Chief Wave Architect: "목회자 AI 활용 세미나 준비"
        ↓
Flow Operations Orchestrator
├─ [1순위] Learning Wave Lead → 커리큘럼 + 강의안 생성
├─ [2순위] Content Wave Lead  → 홍보 콘텐츠 + SNS 게시물
└─ [3순위] Flow Operations Lead → 일정표 + 공지문
        ↓
최종 결과 → Chief Wave Architect
```

### 시나리오 B — 콘텐츠 제작

```
Chief Wave Architect: "이번 주 설교 메시지로 SNS 콘텐츠 만들어줘"
        ↓
Flow Operations Orchestrator
└─ Content Wave Lead → Hook + 카피 + 플랫폼 변환 + 비주얼 기획
        ↓
최종 결과 → Chief Wave Architect
```

### 시나리오 C — 파트너십 제안

```
Chief Wave Architect: "A 교회에 Wave AI 강의 제안서 보내줘"
        ↓
Flow Operations Orchestrator
├─ [1순위] Network Wave Lead → 제안서 작성
└─ [2순위] Content Wave Lead → 소개 자료 생성 (선택)
        ↓
최종 결과 → Chief Wave Architect
```

### 시나리오 D — 지식 자산화

```
Chief Wave Architect: "지난 3개월 강의 내용을 책으로 만들어줘"
        ↓
Flow Operations Orchestrator
├─ [1순위] Knowledge Wave Lead → 원고 구조화 + 작성
└─ [2순위] Content Wave Lead   → 출판 홍보 콘텐츠 (선택)
        ↓
최종 결과 → Chief Wave Architect
```

### 시나리오 E — AI 에이전트 개발

```
Chief Wave Architect: "설교 자동 요약 에이전트 만들어줘"
        ↓
AI Systems Orchestrator
└─ AI Systems Lead → 프롬프트 설계 + 워크플로우 구성 + QA
        ↓
최종 결과 → Chief Wave Architect
```

---

## 5. 에이전트 간 핸드오프 프로토콜

### 핸드오프 조건
```
호출하는 에이전트가 제공해야 할 것:
- 작업 목적 (왜 이 에이전트를 호출하는가)
- 입력 데이터 (무엇을 처리할 것인가)
- 출력 형식 (어떤 형태로 받고 싶은가)
- 우선순위 (언제까지 필요한가)
```

### 완료 보고 형식
```
호출받은 에이전트가 반환할 것:
- 완료 여부 (completed / failed / partial)
- 산출물 (파일, 텍스트, 링크 등)
- 소요 작업 (무엇을 했는가)
- 후속 필요사항 (다음에 필요한 것이 있는가)
```

---

## 6. 에러 처리

```
1차: 동일 작업 재시도
2차: 대안 방법 시도 (다른 접근으로 같은 목표)
3차: 최소 기능 모드 (핵심 결과만 생성)
3회 실패 후: Chief Wave Architect에게 보고
  - 무엇을 시도했는가
  - 왜 실패했는가
  - 사용자 결정이 필요한 사항
```

---

## 7. 병렬 실행 조건

```
병렬 실행 가능 조건:
- 두 작업 간 의존성이 없을 때
- 각 작업의 입력이 독립적일 때

예시:
  ✅ 병렬: Content Wave + Flow Operations Lead (둘 다 독립적)
  ❌ 순서 필요: Learning Wave → Content Wave (강의안이 있어야 홍보 가능)
```

---

## 8. 다음 단계 (미래 확장)

```
현재: Orchestrator → Lead Agent (2단계)
확장: Orchestrator → Lead Agent → Sub Agent (3단계)

Sub Agent 추가 조건:
- Lead Agent 혼자 처리하기에 작업량이 과다할 때
- 특정 기능의 전문성이 높아져 분리가 필요할 때
- 동시 다수 작업이 일상화될 때
```
