# T4 Integration Specialist — 핵심 발견 요약 (Round-02)

## 메타데이터
- 조사 차수: 2 / Teammate: t4 / 조사 축: 기술·이론 축 / 생성일: 2026-04-29

---

## 핵심 결론 (1문장)
핵심 기능(설교·신학·묵상)은 최소 연동으로 LOCAL-OK, 원어 DB와 A4 캡처는 로컬 설치 추가로 커버, NotebookLM MCP는 LOCAL-PARTIAL로 인증 재시도 로직 필수다.

## 연동 분류 (PRD용 축약)

| 분류 | 항목 | 로컬 실행 |
|-----|-----|---------|
| 필수 | state.yaml, .claude/ 구조 | LOCAL-OK |
| 권장 | OSIS XML 원어 DB, Playwright | LOCAL-OK (설치) |
| 선택 | cron, pandoc, yt-dlp | LOCAL-OK |
| 선택·주의 | NotebookLM MCP, Telegram | LOCAL-PARTIAL |
| 제외 | Logos, Accordance (SaaS) | LOCAL-BLOCKED |

## LOCAL-BLOCKED 항목
- **Logos / Accordance**: 유료 SaaS 클라우드 구독 전제. 로컬 실행 불변 위반.

## PRD에 전달할 것
- "필수 연동 vs 선택 연동" 표를 에이전트별로 포함
- LOCAL-PARTIAL 항목에 대한 폴백 전략 명시
- Logos/Accordance는 LOCAL-BLOCKED로 명시하고 OSIS XML을 대안으로 권장
