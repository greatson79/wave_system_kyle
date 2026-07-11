# T2 Configuration Architect — 핵심 발견 요약 (Round-02)

## 메타데이터
- 조사 차수: 2 / Teammate: t2 / 조사 축: 기술·이론 축 / 생성일: 2026-04-29

---

## 핵심 결론 (1문장)
12 에이전트 + 신학 필터 + 3 파이프라인 복잡도에서는 CLAUDE.md 경량 TOC + .claude/skills/ 분산이 유일하게 유지보수 가능한 설정 구조다.

## 필수 구성요소 Top 3
1. CLAUDE.md 200라인 이하 경량 TOC — 컨텍스트 소비 최소화
2. .claude/skills/theology-filter/SKILL.md — 신학 필터 독립 격리
3. theology_guard.py Hook — PostToolUse 키워드 2차 방어

## 로컬 실행 태그 요약
| 항목 | 태그 |
|-----|-----|
| CLAUDE.md 경량 TOC 구조 | LOCAL-OK |
| .claude/skills/ 분산 구조 | LOCAL-OK |
| Hook 스크립트 (Python) | LOCAL-OK |

## 반드시 피해야 할 것
- CLAUDE.md에 12 에이전트 지시 전체 삽입 → 모든 세션에 과다 로드
- Hook에 복잡한 신학 판단 위임 → Hook은 단순 키워드만 처리

## PRD에 전달할 것
- 아키텍처 섹션에 .claude/ 디렉터리 구조 다이어그램 포함
- "CLAUDE.md 크기 제한 200라인" 설계 원칙으로 명시
