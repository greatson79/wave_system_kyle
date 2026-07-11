# DiA Ai Edu. Solution 조직도

> **조직 설계**: 기존 자비스 시스템(Master-Worker)을 매트릭스 부서 조직으로 격상
> **주소화 AI 노드 정의상 14**: CEO·COO·CSO·agy·Codex·사업부 3·본부 6 (주인님=오너 role·surface 없음→노드 제외; 품질감사실=agy+Codex 2노드). ★현행 물리 상주는 이벤트 구동, 실측 정본은 `SESSION_STATE.md` 노드 레지스트리.
> **핵심 원칙**: 기존 커맨드·스킬 100% 유지, 거버넌스 레이어만 추가 (Virtual Matrix)

---

## 조직도

### 경영·거버넌스 (5)
- **이사회/오너** (`board`) — 주인님 · 최종승인·denylist·kill-switch · *(role only, no surface — 노드 카운트 제외)*
- **CEO** (`ceo`) — Master(Opus) · 전략·라우팅·승인게이트·회장 보고
- **COO** (`coo`) — Claude · 운영총괄·일상 워커취합·진행게이트·CEO 보고경유 · ws1(경영본부) · ★현행 surface는 `SESSION_STATE.md` 레지스트리·`cmux tree --all` 동적해소(회전 대비) *(2026-06-25 신설·CEO 승인)*
- **CSO** (`cso`) — Claude · 자원·cmux·컨텍스트·IT·지식관리/SOT 겸직
- **품질감사실** (`agy` + `codex` 2노드) — agy(콘텐츠·신학·전략) + Codex(코드·기술) · 적대적 반박 검증

### 사업부 3 (세로축 — 가치흐름 end-to-end 소유)
> ★사업부문장(사업부장) = **본부장 겸직**(2026-06-30 확정), 전략 평면(중역회의 주1회) 전용 — 운영 hop 아님. 매핑·중역회의 상세 ↓「운영·전략 두 평면」.
| 사업부 | 미션 | 핵심 자산 | 엔진 |
|---|---|---|---|
| **목회사역** (`ministry`) 🏆 | 디딤교회 주간 콘텐츠·설교 (주력) | sermon·weekly-works·church-admin·theological | Claude |
| **인텔리전스** (`intelligence`) | 투자신호·통찰보고서 | financial·투자분석·insight-report | Claude |
| **비전교육** (`vision-edu`) | 청소년 인생계획·비전코칭 (66스킬) | vision-*·youth-life-planner | Claude |

> ★**목회사역 사업부 내부 조직 (2026-07-01 밤 신설·주인님 임명·ai_churchteam 3계층 실노드화)**: **본부장 = 총괄팀장**(기존 디딤팀장 ws4/s8 승격·ai_churchteam lead-orchestrator) · **기획팀장 = Codex**(ws4/s44) · **실행팀장 = agy**(ws4/s45). 말씀·교육 등 부서워커는 각 팀장 산하 sub-agent. ※'총괄팀장'은 목회사역본부장 직함이며 경영본부 CEO(총괄팀장)와 별개. 노드 주소=회전대비 `SESSION_STATE.md` 레지스트리 정본.

### 공유기능본부 6 (가로축 — 전 사업부 지원, 전문가 센터)
| 본부 | 역할 | 핵심 자산 | 엔진 |
|---|---|---|---|
| **기획·전략** (`strategy`) | Enabling | wave-orchestrator·blueprint·planner | Claude |
| **크리에이티브** (`production`) | Stream-support | sns-cardnews·slides·manim·article-writing·lecture-design | Claude |
| **마케팅·배포** (`marketing`) | Stream-support | seo·content-marketing·172스킬 | Claude |
| **AI Tech** (`ai-tech`) | Platform | harness·gan·웹앱·대시보드·개발 91 | Claude+Codex |
| **재무·관리** (`finance`) | Support | church-accounting·finance-ops·korean-law | Claude |
| **리서치·검증** (`research`) | Enabling/Platform | env-scanner·GlobalNews·deep-research·exa | Claude |

---

## 매트릭스 작동 원리

### 1. 사업부 = 결과 책임자
CEO가 목표 위임 → 사업부장이 마감·품질·산출물 소유.

### 2. 공유기능본부 = 전문가 센터
각 본부가 능력의 표준·SOP·템플릿·스킬·품질바를 소유·관리.

### 3. 실행 흐름 (Virtual Matrix)
기존 커맨드는 **사업부장 노드가 단독 실행**(100% 보존). 매트릭스는 무거운 inter-pane 소켓 위임이 아니라 **SOP 결합**으로 구현 — sub-agent 스폰 시 대상 본부 헌장·SOP를 시스템 프롬프트에 결합. 진짜 무거운/크로스-사업부 작업만 본부 노드에 정식 의뢰.

### 4. 충돌 조율
두 사업부가 같은 본부 자원 경합 → CEO(Master) 중앙 중재.

### 5. 이원화 검증 게이트
모든 산출물 → ① **리서치·검증본부 = Fact Validation**(사실·출처·환각) → ② **품질감사실 = Value & Logic Validation**(전략·신학·문체) → CEO → 회장 보고. 두 게이트 격리.

---

## 운영·전략 두 평면 + 중역회의 (★2026-06-30 주인님 확정)

> **설계 원리**: 계층을 *더하지* 않고, 위로 올라가는 것을 *줄인다*. 조직을 두 평면으로 분리하되, **사업부문장(=사업부장)은 전략 평면 전용 역할이며 운영 보고 hop이 아니다**(계층 추가로 인한 latency·병목 방지).

### 평면 분리
| | 운영 평면 (빠름·평면, **불변**) | 전략 평면 (작음·숙고) |
|---|---|---|
| 흐름 | 팀 → 본부장 → COO → CEO → 주인님 | **중역회의** |
| 구성 | 본부장·워커·COO | 사업부문장3 + CEO + COO |
| 사업부문장 | ❌ 미개입 (hop 추가 없음) | ✅ 주역 |

### 사업부문장 = 본부장 겸직 (주인님 확정)
상시 노드 신설 없이 본부장이 **전략 hat을 겸직**(자원·컨텍스트 절약·YAGNI — 노드 수 불변). 시작 매핑(잠정·부하 시 재배정):
- **목회사역 사업부문장** ← 목회사역(디딤) 워크스테이션 팀장
- **인텔리전스 사업부문장** ← 리서치본부장
- **비전교육 사업부문장** ← 크리에이티브본부장
- 권한: 자기 사업부 **outcome·우선순위·전략의 단일 책임**. ★본부장에 대한 명령·승인권 없음(점선 coordination) — 운영 지휘는 COO 라인 그대로.

### 중역회의 (전략 평면의 유일 의식 — ★매주 월요일 오전)
- **구성**: 사업부문장3 + CEO + COO. (CSO=자원안건 시 / agy·Codex=적대검증 시 / 본부장=자기 안건 시만 소환.)
- **안건**: 전략·주간 방향 · cross-사업부 우선순위 · 공유본부 자원배분 중재 · denylist급 결정. ★일상 운영 제외(COO·본부장 소관).
- **주기**: **매주 월요일 오전** (★개시 시각 = 주인님 호출 시 — CEO가 안건·자료 사전 준비해 대기) + 이벤트(cross-사업부 충돌·중대결정). 작고 드물게.
- **산출**: 결정·우선순위 → COO가 운영 평면 언어로 번역·집행.

### 매트릭스 보존 (불가침)
공유기능본부(크리에이티브·AITech·마케팅·리서치·재무·기획)는 그대로 다(多)사업부 봉사. **사업부문장=데맨드**(무엇이 필요) / **본부=서플라이**(기능 역량) / **COO=일상 서플라이 배분 중재** / **중역회의=전략 데맨드 우선순위**. 본부 자원충돌 → COO 1차 중재 → 안 풀리면 중역회의 상정.

---

## 부서 헌장 및 문서

### 경영 거버넌스 (board role + 5 노드)
- [이사회/오너 헌장](./exec/board.md) — role only (no node/memory)
- [CEO 헌장](./exec/ceo.md)
- [COO 헌장](../COO_DIRECTIVE.md) — 운영총괄(2026-06-25 신설·ws1 경영본부, surface는 `SESSION_STATE.md` 동적해소)
- [CSO 헌장](./exec/cso.md)
- [품질감사 agy 헌장](./exec/agy.md) — Value & Logic 검증
- [품질감사 codex 헌장](./exec/codex.md) — 코드·기술 검증

### 사업부 (3)
- [목회사역 헌장](./divisions/ministry.md)
- [인텔리전스 헌장](./divisions/intelligence.md)
- [비전교육 헌장](./divisions/vision-edu.md)

### 공유기능본부 (6)
- [기획·전략본부 헌장](./hq/strategy.md)
- [크리에이티브본부 헌장](./hq/production.md)
- [마케팅본부 헌장](./hq/marketing.md)
- [AI Tech 본부 헌장](./hq/ai-tech.md)
- [재무·관리본부 헌장](./hq/finance.md)
- [리서치·검증본부 헌장](./hq/research.md)

### 부서별 영구기억
모든 부서의 누적 학습·SOP 개선: [`memory/` 폴더](./memory/)

---

## 상주 인프라

- **부서별 헌장 템플릿**: [_charter_template.md](./_charter_template.md)
- **대기모드 수명주기 프로토콜**: [lifecycle.md](./lifecycle.md)
- **커맨드·스킬 부서 귀속 매핑**: [command-map.md](./command-map.md)
- **노드 레지스트리**: `SESSION_STATE.md` 14노드 + 상태(L0/L1/L2) 컬럼

---

## 참고 문서

- **조직 설계 스펙**: `docs/superpowers/specs/2026-06-23-wave-ai-networks-org-design.md`
- **구축 계획**: `docs/superpowers/plans/2026-06-23-dia-ai-edu-solution-phase1.md`
