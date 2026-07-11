# Round-03 Cross-Analysis — Parking Lot

- **차수/축**: 3차 / 코딩·구현
- **생성**: 2026-04-29
- **목적**: 본 차수 범위 밖이지만 종합(synthesis) 단계 또는 PRD 작성 단계에서 다뤄야 할 발견 사항.

## 카테고리 A — PRD 단계에서 결정 필요 (Open Questions)

| # | 항목 | 출처 Branch | 영향 섹션 (예상) | 태그 |
|---|---|---|---|---|
| 1 | Telegram MCP 인입을 워크플로우 트리거로 쓸 때의 권한·인젝션 모델 (`<channel source="telegram">` 게이트) | t2/t3 외부 발견 | §Risks, §Integration | `[LOCAL-OK]` 단 인증 경계 미정의 |
| 2 | NotebookLM MCP `refresh_auth` 실패 시 재시도/우회/차단 정책 | t3 외부 발견, 2차 t4 와 연계 | §Risks, §Integration | `[LOCAL-PARTIAL]` |
| 3 | Skill 패키징·버전 관리 (skill 내부 prompt 변경의 versioning) | t3 | §Skills Catalog | `[LOCAL-OK]` |
| 4 | PreCompact 가 status.md 갱신 *중간* 발화했을 때의 일관성 (`_state.json` 진실 vs status.md 파생) | t5 | §State & Recovery | `[LOCAL-OK]` |
| 5 | workflow.md DAG 에 대한 단위/통합 테스트(Claude Code 외부 dry-run) 부재 | t1/t2 | §Testing | `[LOCAL-OK]` |
| 6 | 비결정 산출(카드뉴스 PNG, 슬라이드) 회귀 검출 — hash 비교 부적합 | t4 | §Quality Gates | `[LOCAL-OK]` |
| 7 | 다중 사용자 협업 시나리오 (목사 외 보조 인력 동시 편집) — 단일 쓰기자 가정 붕괴 | t2/t5 | §Operations | `[LOCAL-OK]` 단, 가정 변경 영향 큼 |

## 카테고리 B — 본 축 범위 밖 (다음 차수 또는 별도 조사)

- 분산 채택 시 합의 알고리즘 (Paxos lite, lease) — over-engineering 후보, 본 PRD 에 불필요할 가능성 높음.
- General hook 의 버전 호환성 정책.
- HSM 채택 시 시각화 도구.
- "intent 자체를 LLM 이 표준화" 하는 메타 단계.
- LLM-judge false-positive 를 사용자 피드백으로 학습하는 구조.
- DAG 정적 표현의 형상관리(version control) 정책 (workflow.md 변경 이력 추적).

## 카테고리 C — 1·2차에서 이미 박혀 있고 본 차수가 *재확인* 만 한 항목 (별도 조치 불필요)

- Claude Code 단독 완결 우위 (1차).
- 적극 연동(MCP) + 검증된 원칙 (2차).
- L0-L2 4계층 quality-gates (부모 게놈).
- Context Preservation System (부모 게놈).
