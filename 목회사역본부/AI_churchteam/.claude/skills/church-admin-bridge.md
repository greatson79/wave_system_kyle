---
name: church-admin-bridge
description: AI_churchteam 백본에서 church-admin 교회행정 시스템을 호출하는 브릿지. 내부 변경 없이 경로 참조·호출 방법만 기술한다.
---

# Church-Admin 브릿지

> ★절대 규칙: church-admin 내부 = 절대 수정 불가.
> 이 파일은 AI_churchteam → church-admin 단방향 호출 인터페이스다.

## 경로

| 항목 | 절대 경로 |
|------|----------|
| church-admin ROOT | `/Users/kylechoi/Desktop/Ai_works/목회사역본부/church-admin/church-admin/` |
| 스킬 | `.claude/skills/church-admin/SKILL.md` |
| 데이터 | `data/` (교인·교적·재정 DB) |

## 호출 가능 커맨드

| 커맨드/트리거 | 기능 | 실행 위치 |
|--------------|------|----------|
| `/start` | 교회행정 메인 메뉴 | church-admin/ |
| "주보 만들어줘" | 주간 주보 생성 | church-admin/ |
| "새신자 현황" | 새신자 현황 보고서 | church-admin/ |
| "교인 검색 [이름]" | 교인 정보 검색 | church-admin/ |
| "이번 달 재정 보고서" | 월간 재정 보고서 | church-admin/ |

## AI_churchteam → church-admin 호출 시점

| AI_churchteam 팀 | 호출 조건 | 커맨드 |
|-----------------|----------|--------|
| 운영·행정팀 | 주보 생성 필요 | "주보 만들어줘" |
| 운영·행정팀 | 새신자 현황 확인 | "새신자 현황" |
| 운영·행정팀 | 교인 정보 검색 | "교인 검색 [이름]" |
| 사역기획팀 | 행사 기획 시 교인 통계 필요 | church-admin 쿼리 |

## 호출 프로토콜

1. church-admin ROOT 디렉토리로 컨텍스트 이동 후 커맨드 실행
2. 산출물: church-admin `output/` 하위 (주보·보고서 등)
3. 담임목사 최종 결정권은 AI 판단 아닌 주인님 승인으로 처리

## 데이터 흐름

```
AI_churchteam 운영팀 행사기획
    → church-admin 교인 통계 쿼리
    → 결과 → AI_churchteam 기획안 반영
```
