---
name: weekly-works-bridge
description: AI_churchteam 백본에서 weekly-works 설교준비·주간콘텐츠 시스템을 호출하는 브릿지. 내부 변경 없이 경로 참조·호출 방법만 기술한다.
---

# Weekly-Works 브릿지

> ★절대 규칙: weekly-works 내부(sermon·research-bridge·team-leader) = 절대 수정 불가.
> 이 파일은 AI_churchteam → weekly-works 단방향 호출 인터페이스다.

## 경로

| 항목 | 절대 경로 |
|------|----------|
| weekly-works ROOT | `/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/` |
| 설교 SOT | `data/sermon-plan-2026.json` |
| 매일묵상 SOT | `.claude/skills/weekly-devotion/devotion-data.json` |
| sermon-context.md | `output/{월}/{주차}/설교/sermon-context.md` |
| 주간 산출물 | `output/{월}/{주차}/` |

## 호출 가능 커맨드

| 커맨드 | 기능 | 실행 위치 |
|--------|------|----------|
| `/주간총괄 [주차]` | 설교·묵상·기도·나눔지·카드뉴스 통합 생성 | weekly-works/ |
| `/설교 [본문]` | 설교 5단계 (research-bridge 자동 가동) | weekly-works/ |
| `/주간현황` | 주간 대시보드 (dashboard.html 열기) | weekly-works/ |

## AI_churchteam → weekly-works 호출 시점

| AI_churchteam 팀 | 호출 조건 | 커맨드 |
|-----------------|----------|--------|
| 말씀·설교팀 | 주간 설교 생성 필요 | `/설교 [본문]` |
| 사역기획팀 | 주간 전체 콘텐츠 필요 | `/주간총괄 [주차]` |
| 총괄팀장 | 주간 진행 현황 확인 | `/주간현황` |

## 호출 프로토콜

1. weekly-works 디렉토리로 컨텍스트 이동 후 커맨드 실행
2. 완료 산출물 경로: `weekly-works/output/{월}/{주차}/`
3. sermon-context.md 생성 완료 후 → AI_churchteam 월간기획·연간계획에 반영 가능

## sermon-context.md 연결 (데이터 흐름)

```
weekly-works 설교 완료
    → sermon-context.md (설교 제목·본문·FCF·CMT·HP·예화)
    → AI_churchteam 사역기획팀이 읽어 월간기획·소그룹·SNS 방향 정렬
```

## ★불가침 확인 목록

이 브릿지를 통해 호출해도 다음 파일은 절대 변경되지 않는다:
- `weekly-works/.claude/skills/sermon/sermon_SKILL.md`
- `weekly-works/.claude/skills/sermon/rules/research-bridge.md`
- `weekly-works/.claude/skills/team-leader/rules/agent-registry.md`
- `weekly-works/.claude/skills/team-leader/rules/agent-protocol.md`
