# Wave AI Networks — 조직도

> 최종 업데이트: 2026-04-08
> 운영 방식: **Option B** — 팀장(Lead Agent) 8개로 시작, 필요 시 하위 에이전트 추가
> 모든 AI 에이전트는 **ON-DEMAND** — 작업 요청 시에만 활성화

---

## 전체 구조

```
Chief Wave Architect (대표)
Kyle Choi [Human]
│
├─ Flow Operations Orchestrator [AI] ← 운영총괄
│  activation: on_demand
│  │
│  ├─ Learning Wave Lead [AI]         ← 교육본부 팀장
│  ├─ Content Wave Lead [AI]          ← 콘텐츠본부 팀장
│  ├─ Network Wave Lead [AI]          ← 네트워크본부 팀장
│  ├─ Knowledge Wave Lead [AI]        ← 출판본부 팀장
│  └─ Flow Operations Lead [AI]       ← 운영본부 팀장
│
└─ AI Systems Orchestrator [AI]      ← CTO
   activation: on_demand
   │
   └─ AI Systems Lead [AI]           ← AI개발본부 팀장
```

---

## 에이전트 현황

| 포지션 | 직책 | 타입 | 보고 대상 | 활성화 | 파일 | 상태 |
|--------|------|------|-----------|--------|------|------|
| Chief Wave Architect | 대표 | Human | — | 상시 | `ceo/ceo_SKILL.md` | ✅ |
| Flow Operations Orchestrator | 운영총괄 | AI Agent | Chief Wave Architect | On-Demand | `flow-operations-orchestrator/` | ✅ |
| AI Systems Orchestrator | CTO | AI Agent | Chief Wave Architect | On-Demand | `ai-systems-orchestrator/` | ✅ |
| Learning Wave Lead | 교육본부 팀장 | AI Agent | Flow Ops Orchestrator | On-Demand | `learning-wave-lead/` | ✅ |
| Content Wave Lead | 콘텐츠본부 팀장 | AI Agent | Flow Ops Orchestrator | On-Demand | `content-wave-lead/` | ✅ |
| Network Wave Lead | 네트워크본부 팀장 | AI Agent | Flow Ops Orchestrator | On-Demand | `network-wave-lead/` | ✅ |
| Knowledge Wave Lead | 출판본부 팀장 | AI Agent | Flow Ops Orchestrator | On-Demand | `knowledge-wave-lead/` | ✅ |
| Flow Operations Lead | 운영본부 팀장 | AI Agent | Flow Ops Orchestrator | On-Demand | `flow-operations-lead/` | ✅ |
| AI Systems Lead | AI개발본부 팀장 | AI Agent | AI Systems Orchestrator | On-Demand | `ai-systems-lead/` | ✅ |

---

## 하위 에이전트 확장 계획 (필요 시 추가)

| 팀 | 추가 가능한 하위 에이전트 | 추가 조건 |
|----|--------------------------|-----------|
| Learning Wave | Curriculum / Lecture / Practice / Feedback | 교육 요청 빈도 증가 시 |
| Content Wave | Hook / Copywriting / Platform / Visual | 다채널 동시 생산 필요 시 |
| Network Wave | Outreach / Partnership / CRM / Community | 다수 파트너십 동시 관리 시 |
| Knowledge Wave | Writing / Editing / Distribution | 출판물 동시 제작 시 |
| Flow Operations | Notice / Scheduling / Finance / Admin | 운영 요청 일상화 시 |
| AI Systems | Prompt Architect / Workflow / QA | 동시 다수 개발 시 |

---

## 의사결정 체계

```
전략 결정          → Chief Wave Architect (Kyle Choi)
작업 배분/흐름     → Flow Operations Orchestrator
AI 시스템 설계     → AI Systems Orchestrator
본부별 실행        → 각 Lead Agent (팀장)
세부 작업 (미래)   → 하위 에이전트 (필요 시 추가)
```
