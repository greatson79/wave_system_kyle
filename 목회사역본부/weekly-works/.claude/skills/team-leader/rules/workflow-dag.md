# Workflow DAG 규칙

## 의존성 맵

| 작업 | 의존 | 병렬 가능 | 에이전트 |
|------|------|----------|---------|
| A. 설교 준비 | 없음 | B,C와 병렬 | Sermon Agent |
| B. 매일묵상 | 없음 | A,C와 병렬 | Weekly Devotion |
| C. 수요기도회 | 없음 | A,B와 병렬 | Prayer Doc |
| D. 소그룹 나눔지 | A 4-4단계 (아웃라인작성 완료) | E,H,S와 병렬 | Small Group Agent |
| E. SNS 카드뉴스 | A 4-4단계 (아웃라인작성 완료) | D,H,S와 병렬 | SNS Card News |
| H. 주보 | A 4-4단계 (아웃라인작성 완료) + 광고 사용자 입력 | D,E,S와 병렬 | Bulletin Agent |
| S. 숏츠 | A 4-4단계 (아웃라인작성 완료) | D,E,H와 병렬 | Shorts Agent |

## 실용적 실행 순서

Agent 도구의 `run_in_background=true`로 **실제 병렬 실행**을 구현한다.

```
Phase 1-Auto (백그라운드 병렬):
  Agent(B 매일묵상, run_in_background=true)
  Agent(C 기도카드, run_in_background=true)
  → 두 에이전트가 독립적으로 실행, 완료 알림 수신

Phase 1-Interactive (메인 대화):
  A (설교) — 대화형, 목사 피드백 필수
  1단계 → 2단계 → 3단계 → 4-1단계 제목확정 → 4-2단계 전개방식확정 → 4-3단계 예화설계 → 4-4단계 아웃라인작성
  → 설교 중 백그라운드 완료 알림이 도착할 수 있음

[게이트 1] 4-4단계 아웃라인작성 완료 → sermon-context.md 갱신

Phase 2 (백그라운드 — 4-4단계 완료 직후 즉시, 자동 병렬 소환):
  [필수] 사용자에게 광고 내용 요청 → 입력 받은 후 H 소환
  Agent(D 소그룹 나눔지, run_in_background=true) ← sermon-context.md 입력
  Agent(E0 디자인스카우트, run_in_background=true) ← sermon-context.md 입력
  Agent(H 주보, run_in_background=true) ← sermon-context.md + 광고 내용 입력
  Agent(S 숏츠, run_in_background=true) ← sermon-context.md 입력
  → D, E0, H, S 동시에 백그라운드 시작

[게이트 1.5] E0 디자인스카우트 완료 → design-guide.md 생성됨

Phase 2-Cardnews (백그라운드 — design-guide.md 생성 직후):
  Agent(E SNS 카드뉴스, run_in_background=true) ← sermon-context.md + design-guide.md 입력

Phase 1-Interactive 계속 (메인 대화):
  A-5단계 원고 작성 — D·E와 병렬 진행

주간보고서 (D + E 완료 확인 후 생성)
```

### DAG 시각화

```
설교 1~4-4단계(대화형)  ∥  매일묵상(자동)  ∥  기도카드(자동)
       ↓
  4-1 제목확정
       ↓
  4-2 전개방식확정
       ↓
  4-3 예화설계
       ↓
  4-4 아웃라인작성 → sermon-context.md 갱신
       ↓
  [광고 내용 사용자 입력 요청 → 수신 후 진행]
       ↓
  ┌────────────┬──────────────────┬─────────────────────┐
  │            │                  │                     │
5단계 원고   WK-H 주보(자동)   WK-D 소그룹나눔지(자동)  WK-E0 디자인스카우트(자동)
(대화형)    PNG+PDF 산출                                       ↓
                                                      design-guide.md
                                                             ↓
                                                      WK-E SNS 카드뉴스(자동)
       ↓
    주간 보고서 (D + E + H 완료 후)
```

> **소환 패턴**: `rules/agent-protocol.md` 참조 (패턴 A: 자동, 패턴 B: 크로스폴더, 패턴 C: 순차)

## 중단/재개 규칙

- 설교 중 세션이 끊기면: status.md에 A: in-progress 기록
- "이어서" 시: status.md 읽고 완료된 작업 건너뜀
- 설교 재개: sermon output 폴더의 파일 존재 감지로 단계 판단
- 4-4단계까지 완료 + 카드뉴스 미완: 카드뉴스만 재실행
