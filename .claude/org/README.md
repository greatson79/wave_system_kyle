# DiA Ai Edu. Solution 조직도

> **조직 설계**: 기존 자비스 시스템(Master-Worker)을 매트릭스 부서 조직으로 격상
> **상주 노드**: 경영 4 + 사업부 3 + 본부 6 = 13개
> **핵심 원칙**: 기존 커맨드·스킬 100% 유지, 거버넌스 레이어만 추가

---

## 조직도

### 경영·거버넌스 (4)
- **이사회/오너** (`board`) — 주인님 · 최종승인·denylist·kill-switch
- **CEO** (`ceo`) — Master(Opus) · 전략·라우팅·승인게이트·회장 보고
- **CSO** (`cso`) — Claude · 자원·cmux·컨텍스트·IT·지식관리/SOT 겸직
- **품질감사실** (`qa-office`) — agy(콘텐츠·신학·전략) + Codex(코드·기술) · 적대적 반박 검증

### 사업부 3 (세로축 — 가치흐름 end-to-end 소유)
| 사업부 | 미션 | 핵심 자산 | 엔진 |
|---|---|---|---|
| **목회사역** (`ministry`) 🏆 | 디딤교회 주간 콘텐츠·설교 (주력) | sermon·weekly-works·church-admin·theological | Claude |
| **인텔리전스** (`intelligence`) | 투자신호·통찰보고서 | financial·투자분석·insight-report | Claude |
| **비전교육** (`vision-edu`) | 청소년 인생계획·비전코칭 (66스킬) | vision-*·youth-life-planner | Claude |

### 공유기능본부 6 (가로축 — 전 사업부 지원, 전문가 센터)
| 본부 | 역할 | 핵심 자산 | 엔진 |
|---|---|---|---|
| **기획·전략** (`strategy`) | Enabling | wave-orchestrator·blueprint·planner | Claude |
| **제작** (`production`) | Stream-support | sns-cardnews·slides·manim·article-writing·lecture-design | Claude |
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

### 3. 실행 흐름
```
사업부장이 분해
  ├─ 가벼운 건: 본부 SOP/스킬 로드한 sub-agent 직접 fan-out(자기완결)
  └─ 무겁거나 전문적인 건: 본부장(상주)에 정식 의뢰
```

### 4. 충돌 조율
두 사업부가 같은 본부 자원 경합 → CEO(Master) 중앙 중재.

### 5. 품질 게이트
모든 산출물 → 품질감사실(agy+Codex) 적대 검증 → CEO → 회장 보고.

---

## 부서 헌장 및 문서

### 경영 거버넌스 (4)
- [이사회/오너 헌장](./exec/board.md)
- [CEO 헌장](./exec/ceo.md)
- [CSO 헌장](./exec/cso.md)
- [품질감사실 헌장](./exec/qa-office.md)

### 사업부 (3)
- [목회사역 헌장](./divisions/ministry.md)
- [인텔리전스 헌장](./divisions/intelligence.md)
- [비전교육 헌장](./divisions/vision-edu.md)

### 공유기능본부 (6)
- [기획·전략본부 헌장](./hq/strategy.md)
- [제작본부 헌장](./hq/production.md)
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
- **노드 레지스트리**: `SESSION_STATE.md` 13노드 + 상태(L0/L1/L2) 컬럼

---

## 참고 문서

- **조직 설계 스펙**: `docs/superpowers/specs/2026-06-23-wave-ai-networks-org-design.md`
- **구축 계획**: `docs/superpowers/plans/2026-06-23-dia-ai-edu-solution-phase1.md`
