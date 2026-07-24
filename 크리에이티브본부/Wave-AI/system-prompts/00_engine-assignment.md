# Wave AI Networks — 에이전트별 엔진 배정표

> 작성일: 2026-04-08
> 기준: 각 모델의 강점 + 에이전트 작업 특성 매칭

---

## 배정 요약

| 에이전트 | 엔진 | 모델 | 배정 이유 |
|----------|------|------|-----------|
| Flow Operations Orchestrator | Claude | claude-sonnet-4-6 | 복잡한 라우팅 판단 + 다중 지시 추적 = Claude 최강점 |
| AI Systems Orchestrator | GPT | gpt-4o | 기술 아키텍처 설계 + 시스템 구조 판단 = GPT 강점 |
| Learning Wave Lead | Claude | claude-sonnet-4-6 | 신학적 제약 준수 + 교육 구조화 = Claude 정밀도 |
| Content Wave Lead | GPT | gpt-4o | 창의적 카피 + 훅 + 플랫폼 최적화 = GPT 창의성 |
| Network Wave Lead | Claude | claude-sonnet-4-6 | 외교적 뉘앙스 + 관계 커뮤니케이션 = Claude 톤 제어 |
| Knowledge Wave Lead | Gemini | gemini-2.5-pro | 장문 문서 처리 + 리서치 합성 + 출판 구조화 = Gemini 장점 |
| Flow Operations Lead | Gemini | gemini-2.0-flash | 반복적 구조 문서 (공지/일정/행정) = Gemini Flash 속도+효율 |
| AI Systems Lead | GPT | gpt-4o | 프롬프트 엔지니어링 + 기술 구현 + QA = GPT 기술력 |

---

## 엔진별 담당 에이전트

### Claude (claude-sonnet-4-6) — 3개
```
Flow Operations Orchestrator  ← 핵심 오케스트레이션
Learning Wave Lead             ← 신학 정확성 필수
Network Wave Lead              ← 관계 커뮤니케이션 뉘앙스
```
**공통점:** 제약 조건이 많고 판단의 정밀도가 중요한 작업

### GPT (gpt-4o) — 3개
```
AI Systems Orchestrator  ← 기술 아키텍처 설계
Content Wave Lead        ← 창의적 콘텐츠 생성
AI Systems Lead          ← 프롬프트/코드 구현
```
**공통점:** 창의성 또는 기술 구현이 핵심인 작업

### Gemini — 2개
```
Knowledge Wave Lead    ← 장문 처리 + 리서치 합성 (gemini-2.5-pro)
Flow Operations Lead   ← 구조적 반복 문서 (gemini-2.0-flash)
```
**공통점:** 문서 처리량이 많거나 빠른 구조화 출력이 필요한 작업

---

## 비용 효율 분석

```
고비용 (Sonnet/GPT-4o):  6개 에이전트 — 판단/창의/기술 작업
저비용 (Gemini Flash):   1개 에이전트 — 반복 행정 작업
중간 (Gemini Pro):       1개 에이전트 — 장문 처리 특화
```

Flow Operations Lead를 Gemini Flash로 배정하여 행정 문서 비용을 절감합니다.
