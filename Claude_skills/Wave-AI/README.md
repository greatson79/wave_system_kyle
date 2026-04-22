# Wave AI Networks — 파일 구조

> 최종 업데이트: 2026-04-08

---

## 디렉토리 구조

```
Wave-AI/
│
├── WAVE-AI.md                      ← 시스템 헌법 (마스터 개요)
├── soul.md                         ← 존재 이유 및 핵심 가치
├── org-chart.md                    ← 조직도 (현황 + 확장 계획)
├── execution-flow.md               ← 에이전트 간 실행 흐름
├── README.md                       ← 이 파일
│
├── agents/                         ← 에이전트 설계 문서 (SKILL.md)
│   ├── ceo/                        ✅ Chief Wave Architect
│   ├── flow-operations-orchestrator/ ✅ 운영총괄 (Claude)
│   ├── ai-systems-orchestrator/    ✅ CTO (GPT)
│   ├── learning-wave-lead/         ✅ 교육팀장 (Claude)
│   ├── content-wave-lead/          ✅ 콘텐츠팀장 (GPT)
│   ├── network-wave-lead/          ✅ 네트워크팀장 (Claude)
│   ├── knowledge-wave-lead/        ✅ 출판팀장 (Gemini Pro)
│   ├── flow-operations-lead/       ✅ 운영팀장 (Gemini Flash)
│   └── ai-systems-lead/            ✅ AI개발팀장 (GPT)
│
├── system-prompts/                 ← Paperclip 입력용 프롬프트
│   ├── 00_engine-assignment.md     ← 엔진 배정표
│   ├── 01_flow-operations-orchestrator.md  (Claude)
│   ├── 02_ai-systems-orchestrator.md       (GPT)
│   ├── 03_learning-wave-lead.md            (Claude)
│   ├── 04_content-wave-lead.md             (GPT)
│   ├── 05_network-wave-lead.md             (Claude)
│   ├── 06_knowledge-wave-lead.md           (Gemini Pro)
│   ├── 07_flow-operations-lead.md          (Gemini Flash)
│   └── 08_ai-systems-lead.md               (GPT)
│
├── paperclip/                      ← Paperclip 등록 패키지
│   ├── company-config.json         ← 전체 회사 설정
│   ├── registration-guide.md       ← 등록 단계별 가이드
│   └── test-scenarios.md           ← 6개 테스트 케이스
│
└── knowledge/                      ← Second Brain
    └── AI-Technology/
```

---

## 단계별 완료 현황

| 단계 | 내용 | 상태 |
|------|------|------|
| 조직 설계 | 조직도 + 에이전트 구조 확정 | ✅ |
| 에이전트 정의 | 8개 SKILL.md 작성 | ✅ |
| 실행 흐름 | 에이전트 간 프로토콜 설계 | ✅ |
| 시스템 프롬프트 | 8개 Paperclip 입력용 프롬프트 | ✅ |
| 엔진 배정 | Claude / GPT / Gemini 분배 | ✅ |
| Paperclip 설정 | company-config.json + 등록 가이드 | ✅ |
| 테스트 설계 | 6개 시나리오 테스트 케이스 | ✅ |
| Paperclip 실제 등록 | UI에서 직접 입력 | ⬜ 사용자 실행 |
| 테스트 실행 | 6개 시나리오 실제 검증 | ⬜ 사용자 실행 |

---

## Paperclip 등록 바로 시작하기

1. `paperclip/registration-guide.md` 열기
2. Step 1부터 순서대로 실행
3. 등록 완료 후 `paperclip/test-scenarios.md`의 테스트 1부터 실행
```
