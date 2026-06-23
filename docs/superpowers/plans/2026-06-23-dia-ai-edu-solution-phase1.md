# DiA Ai Edu. Solution — Phase 1 구축 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 자비스(Master-Worker)를 매트릭스 부서 조직으로 격상하는 거버넌스 스캐폴딩(`.claude/org/`)을 구축하고, 목회사역 사업부 파일럿으로 운영 모델을 검증한다.

**Architecture:** 기존 스킬·커맨드 위에 **거버넌스 레이어**만 얹는다 — 부서 헌장·부서 메모리·노드 레지스트리·대기모드(L0/L1/L2) 프로토콜·커맨드 귀속 매핑. 애플리케이션 코드 변경은 없다. "테스트"는 실측 검증(파일 구조 grep, cmux 노드 핑, 기존 커맨드 resolve 확인)으로 한다. 물리 노드 13개 전면 기동은 파일럿 검증 후 Phase 1b(별도 계획)로 미룬다 — 본 계획은 스캐폴딩 + 목회사역 1개 사업부 파일럿까지.

**Tech Stack:** Markdown(헌장·프로토콜), cmux(Unix 소켓 멀티에이전트), Claude Code skills/commands, bash(검증).

## Global Constraints

> 모든 태스크의 요구사항에 암묵적으로 포함된다. spec에서 그대로 인용.

- 회사명 = **DiA Ai Edu. Solution**.
- 기존 커맨드(`/주간총괄`·`/설교`·`/주간현황`·`/묵상`)·weekly-works·스킬 레지스트리(394) **100% 유지** — 삭제·이동·이름변경 금지.
- 3대 헌장(MASTER/CSO/WORKER_DIRECTIVE)·자율주행 위임권·콜드복구(SESSION_STATE/RECOVERY) **유지·확장**(원본 변경 금지, 포인터로 참조).
- 산출물 경로 규칙 유지(`output/{주제}/`·환경스캐닝·뉴스크롤링·weekly-works/output).
- **백그라운드 서버 0** — 작업 시만 띄우고 즉시 kill. idle 노드 누적 금지.
- 루트 `CLAUDE.md` 변경 = denylist → 본 계획에서 건드리지 않음(별도 승인 시 Phase 후반).
- 상주 = **13 AI 노드** (주인님=오너 role·surface 없음 → 카운트 제외; 품질감사실=agy+Codex **2노드**; CEO 1 + CSO 1 + agy 1 + Codex 1 + 사업부 3 + 본부 6 = 13). 물리 기동은 **이벤트 구동**(희소 부서 L2 동면, 활성 부서만 L1 단기; 전면 동시 기동 금지).
- **Virtual Matrix**: 기존 커맨드는 사업부장 노드가 단독 실행(보존), 매트릭스는 sub-agent 스폰 시 대상 본부 SOP 결합으로 구현(무거운 inter-pane 위임 강제 금지).
- **이원화 검증**: 리서치·검증본부=Fact Validation(사실·출처·환각) / 품질감사실=Value&Logic(전략·신학·문체). 게이트 격리.
- cmux send/send-key는 항상 `--workspace`+`--surface` 둘 다 명시, 회전ID는 `cmux tree --all`로 동적 해소.

---

## File Structure

생성/수정 파일과 책임:

- `.claude/org/README.md` — (생성) 조직도·매트릭스 작동원리·부서 색인. 조직의 진입점.
- `.claude/org/_charter_template.md` — (생성) 부서 헌장 표준 템플릿(8필드).
- `.claude/org/divisions/{ministry,intelligence,vision-edu}.md` — (생성) 사업부 헌장 3.
- `.claude/org/hq/{strategy,production,marketing,ai-tech,finance,research}.md` — (생성) 본부 헌장 6.
- `.claude/org/exec/{board,ceo,cso,qa-office}.md` — (생성) 경영 거버넌스 헌장 4(기존 DIRECTIVE 포인터+조직 역할).
- `.claude/org/lifecycle.md` — (생성) 상주 3단계(L0/L1/L2) 수명주기·CSO watchdog 프로토콜.
- `.claude/org/command-map.md` — (생성) 기존 커맨드·스킬 → 소유 부서 귀속표.
- `.claude/org/memory/<dept>.md` × 13 — (생성) 부서별 영구기억 stub(누적 학습처).
- `SESSION_STATE.md` — (수정) 노드 레지스트리를 13노드 + 상태(L0/L1/L2) 컬럼으로 확장.

각 파일은 단일 책임(부서 1개 = 헌장 1개). 헌장은 200줄 이하 유지.

---

### Task 1: 조직 스캐폴딩 + 헌장 템플릿 + 조직 README

**Files:**
- Create: `.claude/org/README.md`
- Create: `.claude/org/_charter_template.md`
- Create (dir): `.claude/org/{divisions,hq,exec,memory}/`

**Interfaces:**
- Produces: `_charter_template.md`의 8필드 구조(미션·책임범위·SOP·산출물경로·전속스킬·엔진·영구기억·협업라우팅) — Task 2·3·4가 이 템플릿을 채운다.

- [ ] **Step 1: 디렉토리 생성**

Run:
```bash
mkdir -p /Users/kylechoi/Desktop/Ai_works/.claude/org/{divisions,hq,exec,memory}
```

- [ ] **Step 2: 헌장 템플릿 작성**

Create `.claude/org/_charter_template.md`:
```markdown
# <부서명> 헌장

> DiA Ai Edu. Solution · <계층: 경영/사업부/본부> · 엔진: <Claude/Codex/agy>

- **미션**: <한 줄 존재 이유>
- **책임 범위(Owns)**: <무엇의 결과를 책임지는가>
- **SOP**: <표준 작업 절차 — 단계·게이트>
- **산출물 경로**: <output/... 또는 폴더 규칙>
- **전속 스킬**: <발동할 핵심 스킬 목록>
- **엔진**: <Claude / Codex / agy>
- **영구기억**: `.claude/org/memory/<slug>.md`
- **협업 라우팅**: <주로 협업하는 본부/사업부 + 품질게이트>
```

- [ ] **Step 3: 조직 README 작성**

Create `.claude/org/README.md` — spec 3·4장의 조직도 + 매트릭스 작동원리 + 13부서 색인 링크. (내용: spec `docs/superpowers/specs/2026-06-23-wave-ai-networks-org-design.md` 3~4장을 요약 인용하고 각 헌장 파일로 링크.)

- [ ] **Step 4: 구조 검증**

Run:
```bash
ls -R /Users/kylechoi/Desktop/Ai_works/.claude/org/ && grep -c "미션\|책임 범위\|SOP\|영구기억" /Users/kylechoi/Desktop/Ai_works/.claude/org/_charter_template.md
```
Expected: divisions/hq/exec/memory 디렉토리 표출 + 템플릿 필드 카운트 ≥ 4.

- [ ] **Step 5: 커밋**

```bash
git add .claude/org/README.md .claude/org/_charter_template.md
git commit -m "feat(org): 조직 스캐폴딩 + 헌장 템플릿 + 조직 README"
```

---

### Task 2: 사업부 헌장 3 (목회사역·인텔리전스·비전교육)

**Files:**
- Create: `.claude/org/divisions/ministry.md`, `intelligence.md`, `vision-edu.md`

**Interfaces:**
- Consumes: Task 1 `_charter_template.md` 8필드.
- Produces: 3 사업부 헌장 — Task 6 command-map·Task 8 파일럿이 참조.

각 헌장은 템플릿을 아래 값으로 채운다(verbatim):

| slug | 미션 | 책임범위(Owns) | 전속 스킬 | 산출물 경로 | 엔진 | 협업 |
|---|---|---|---|---|---|---|
| **ministry** | 디딤교회 회중을 섬기는 주간 사역 콘텐츠 생산 | 설교·묵상·나눔지·기도카드·카드뉴스·교회행정·주간총괄 | sermon·weekly-devotion·small-group·sns-cardnews·prayer-doc·church-admin·theological-reasoning·wave-orchestrator | `Claude_skills/weekly-works/output/` | Claude | 제작본부(비주얼)·리서치본부(예화·배경)·품질감사실(신학검증) |
| **intelligence** | 투자·미래 통찰 의사결정 제품 생산 | 투자신호 분석·통찰보고서 | financial(plugin 20)·insight-report·투자분석 workflow | `output/투자분석/`·`output/환경스캐닝/`(소비) | Claude | 리서치본부(환경스캐닝·뉴스·검증=input)·품질감사실(환각검증) |
| **vision-edu** | 청소년 인생계획·비전코칭 (66스킬 활성화) | 인터뷰·수련회·반기회고·비전코칭 패키지 | youth-life-planner·vision-*(66) | `Claude_skills/youth_life_plan/output/` | Claude | 제작본부(강의·핸드아웃)·기획본부(방법론) |

- [ ] **Step 1: 세 헌장 작성** — 템플릿에 위 표 값을 채워 `ministry.md`·`intelligence.md`·`vision-edu.md` 생성. SOP는 각 사업부의 기존 워크플로우 단계를 기술(예: ministry SOP = `/주간총괄` 5단계 + 품질게이트).

- [ ] **Step 2: 스킬 실존 검증** (환각 방지 — 참조 스킬이 실제 레지스트리에 있는지)

Run:
```bash
ls /Users/kylechoi/Desktop/Ai_works/.claude/skills/ | grep -E "sermon|weekly-devotion|youth-life-planner|insight-report|theological-reasoning" | sort
```
Expected: 참조한 핵심 스킬들이 레지스트리에 실존(각 1행 이상).

- [ ] **Step 3: 헌장 완전성 검증**

Run:
```bash
for f in ministry intelligence vision-edu; do echo "== $f =="; grep -c "미션\|책임 범위\|전속 스킬\|영구기억\|협업" /Users/kylechoi/Desktop/Ai_works/.claude/org/divisions/$f.md; done
```
Expected: 각 파일 필드 카운트 ≥ 5.

- [ ] **Step 4: 커밋**

```bash
git add .claude/org/divisions/
git commit -m "feat(org): 사업부 헌장 3 (목회사역·인텔리전스·비전교육)"
```

---

### Task 3: 공유기능본부 헌장 6 (A~F)

**Files:**
- Create: `.claude/org/hq/{strategy,production,marketing,ai-tech,finance,research}.md`

**Interfaces:**
- Consumes: Task 1 템플릿.
- Produces: 6 본부 헌장 — Task 6·8이 참조. 특히 `research.md`는 환경스캐닝·뉴스크롤링 SOP 보유.

| slug | 미션 | 책임범위 | 전속 스킬 | 엔진 | 비고 |
|---|---|---|---|---|---|
| **strategy** | 전략·로드맵·신규기획·방법론 공급 (Enabling) | 로드맵·블루프린트·강의 커리큘럼 방법론 | wave-orchestrator·blueprint·planner·workflow-generator | Claude | |
| **production** | 비주얼·글·교육콘텐츠 생산 (Stream-support) | 카드뉴스·이미지·슬라이드·영상·블로그·아티클·교안 | 셀1: sns-cardnews·frontend-slides·manim-video·canvas-design / 셀2: article-writing·brunch-writing-workflow / 셀3: lecture-design | Claude(+이미지: codex gpt-image) | 3셀 독립 실행 |
| **marketing** | SEO·광고·채널 배포 (Stream-support) | SEO·광고·캠페인·소셜 배포 | seo-strategy·content-engine·content-marketing·(마케팅 172) | Claude | |
| **ai-tech** | 웹앱·대시보드·앱·하네스·자동화 (Platform) | 모든 사업부 앱 수요 제작 | harness-init·gan-*·frontend-design·backend-patterns·deployment-patterns·(Vercel MCP) | Claude+Codex | "앱개발 부서" |
| **finance** | 회계·예산·정산·법무 (Support) | 교회회계·예산·법무검토 | finance-billing-ops·church-accounting(웹앱)·(korean-law MCP) | Claude | 법무 흡수 |
| **research** | 정보 수집·검증 엔진 (Enabling/Platform) | 환경스캐닝·뉴스크롤링·딥리서치·팩트체크·할루시네이션 방지 | env-scanner·deep-research·exa-search·market-research·research-ops·search-first | Claude | `output/환경스캐닝/`·`output/뉴스크롤링/` |

- [ ] **Step 1: 여섯 헌장 작성** — 템플릿에 위 표 값을 채워 생성. `production.md`는 3셀 구조를 명시. `research.md` SOP = 환경스캐닝 퀸투플(WF1~4) + 뉴스크롤링 + 출처검증 게이트.

- [ ] **Step 2: 스킬 실존 검증**

Run:
```bash
ls /Users/kylechoi/Desktop/Ai_works/.claude/skills/ | grep -E "env-scanner|lecture-design|article-writing|seo-strategy|harness-init|sns-cardnews" | sort
```
Expected: 참조 핵심 스킬 실존.

- [ ] **Step 3: 완전성 검증**

Run:
```bash
for f in strategy production marketing ai-tech finance research; do echo "== $f =="; grep -c "미션\|책임 범위\|전속 스킬\|영구기억" /Users/kylechoi/Desktop/Ai_works/.claude/org/hq/$f.md; done
```
Expected: 각 ≥ 4.

- [ ] **Step 4: 커밋**

```bash
git add .claude/org/hq/
git commit -m "feat(org): 공유기능본부 헌장 6 (기획·제작·마케팅·AI Tech·재무·리서치)"
```

---

### Task 4: 경영 거버넌스 헌장 4 (이사회·CEO·CSO·품질감사실)

**Files:**
- Create: `.claude/org/exec/{board,ceo,cso,qa-office}.md`

**Interfaces:**
- Consumes: 기존 `.claude/MASTER_DIRECTIVE.md`·`CSO_DIRECTIVE.md`·`WORKER_DIRECTIVE.md`(원본 불변).
- Produces: 4 경영 헌장 — 기존 DIRECTIVE를 **포인터로 참조**하고 조직 역할만 추가(중복 금지·drift 방지).

| slug | 역할 | 포인터 | 추가 조직 역할 |
|---|---|---|---|
| **board** | 이사회/오너 = 주인님 | `.claude/MASTER_DIRECTIVE.md` denylist | 최종승인·kill-switch·외부발행·비가역 결정 |
| **ceo** | CEO = Master(Opus) | `.claude/MASTER_DIRECTIVE.md` | 전 부서 라우팅·승인게이트·자원충돌 중재·회장 보고 |
| **cso** | CSO + 지식관리/SOT | `.claude/CSO_DIRECTIVE.md` | 노드 수명주기(L0/L1/L2) 집행·SESSION_STATE/SOT 관리·자원 watchdog |
| **qa-office** | 품질감사실 = agy + Codex | `.claude/WORKER_DIRECTIVE.md` 6조 | 전 산출물 적대 검증 게이트(agy=콘텐츠·신학·전략 / Codex=코드·기술) |

- [ ] **Step 1: 네 헌장 작성** — 각 파일은 "원본 헌장은 <포인터>에 있음, 여기는 조직 역할만 기록" 명시. 중복 금지.

- [ ] **Step 2: 포인터 무결성 검증** (참조 DIRECTIVE 실존)

Run:
```bash
ls /Users/kylechoi/Desktop/Ai_works/.claude/{MASTER_DIRECTIVE,CSO_DIRECTIVE,WORKER_DIRECTIVE}.md
```
Expected: 3개 DIRECTIVE 모두 실존.

- [ ] **Step 3: 커밋**

```bash
git add .claude/org/exec/
git commit -m "feat(org): 경영 거버넌스 헌장 4 (이사회·CEO·CSO·품질감사실)"
```

---

### Task 5: 노드 레지스트리 확장 + 대기모드 수명주기 프로토콜

**Files:**
- Create: `.claude/org/lifecycle.md`
- Modify: `SESSION_STATE.md` (노드 통신 레지스트리 표를 13노드 + 상태 컬럼으로 확장)

**Interfaces:**
- Consumes: Task 2·3·4 부서 slug.
- Produces: L0/L1/L2 상태 정의 + 전이 규칙 — Task 8 파일럿이 이 프로토콜로 노드를 검증한다.

- [ ] **Step 1: 수명주기 프로토콜 작성**

Create `.claude/org/lifecycle.md`:
```markdown
# 상주 노드 수명주기 (이벤트 구동형 — 적대검증 H2 반영)

**Charter-level 상주**(전 부서 헌장 상시) ≠ **pane-level 상주**(물리 프로세스). CSO = 중앙 메시지 큐·라우터.

- **L0 활성(Active)**: 작업 수행 중. 병렬은 sub-agent fan-out(pane 추가 금지). 백그라운드 서버 0.
- **L1 대기(Idle, 단기)**: 작업 직후 짧은 유휴. 후속 작업 즉응용 잠깐 유지, 토큰 0.
- **L2 동면(Hibernate, 기본 휴지)**: 유휴 임계 초과 시 CSO가 핸드오프 저장 → pane 종료(메모리 회수).

## 전이 규칙
- L0→L1: 작업 완료·큐 빔.
- L1→L2: CSO가 유휴 임계 초과 감지 시 핸드오프 저장 후 pane 종료(기본 휴지 상태).
- L2→L0: 신규 작업 라우팅 시 CSO가 재기동 + 헌장·핸드오프 복원.
- 희소 부서는 평소 L2, 활성 부서만 L1 단기. 전 부서 L1/L2 = 감시 루프 중단([[feedback_monitoring_only_when_working]]).

## CSO watchdog 책무
- 13노드 메모리·load·컨텍스트 60% 상시 감시.
- 컨텍스트 60% → 관리형 /clear. 장기 idle → L2 동면.
- 메모리·동시 토큰예산 임계 → 회장 에스컬레이션.
- "완전 상주"는 charter/identity 수준(전 부서 헌장 상주). 물리 pane은 수요 기반(활성 L1, 희소 L2). 13 pane 동시 강제 기동 금지.
```

- [ ] **Step 2: SESSION_STATE 노드 레지스트리 확장** — 기존 노드 표에 13부서 행 + `상태(L0/L1/L2)` 컬럼 추가. 현재 가동 노드(CEO=Master·CSO·Codex·agy·디딤=목회사역·환경=리서치·강의·투자)를 신 조직 slug에 매핑.

- [ ] **Step 3: 검증**

Run (스키마 무결성 — 적대검증 M3 반영, false-positive 차단):
```bash
grep -c "L0\|L1\|L2" /Users/kylechoi/Desktop/Ai_works/.claude/org/lifecycle.md
# 13 AI 노드 slug 전수 + 상태 컬럼 존재 확인 (누락행·빈주소 적발)
for s in ceo cso agy codex ministry intelligence vision-edu strategy production marketing ai-tech finance research; do grep -q "$s" /Users/kylechoi/Desktop/Ai_works/SESSION_STATE.md && echo "OK $s" || echo "MISSING $s"; done | grep -c OK
```
Expected: lifecycle 상태 토큰 ≥ 3; slug OK 카운트 = 13(MISSING 0). 주인님=오너 role은 노드표 제외(surface 없음).

- [ ] **Step 4: 커밋**

```bash
git add .claude/org/lifecycle.md SESSION_STATE.md
git commit -m "feat(org): 노드 레지스트리 13노드 확장 + 대기모드 L0/L1/L2 수명주기 프로토콜"
```

---

### Task 6: 커맨드·스킬 → 부서 귀속 매핑

**Files:**
- Create: `.claude/org/command-map.md`

**Interfaces:**
- Consumes: Task 2·3 부서 헌장.
- Produces: 커맨드→소유부서 표 — CEO 라우팅이 참조.

- [ ] **Step 1: 귀속표 작성**

Create `.claude/org/command-map.md` (verbatim 시작값):
```markdown
# 커맨드·스킬 → 소유 부서 귀속표

| 커맨드/스킬 | 소유 부서 | 협업 본부 |
|---|---|---|
| /주간총괄·/설교·/묵상·/주간현황 | 목회사역 | 제작·리서치 |
| sermon·weekly-devotion·small-group·prayer-doc | 목회사역 | 품질감사(신학) |
| /인터뷰·/수련회·/반기회고·vision-* | 비전교육 | 제작·기획 |
| env-scanner(환경스캐닝)·GlobalNews(뉴스크롤링) | 리서치·검증 | — |
| deep-research·exa·market-research | 리서치·검증 | (전 사업부 지원) |
| 투자분석·insight-report·financial | 인텔리전스 | 리서치 |
| sns-cardnews·frontend-slides·manim | 제작본부(셀1) | (발주 사업부) |
| lecture-design | **주제 사업부 소유** — 제작본부 셀3 협업 생산 | 기획본부(방법론) |
| article-writing·brunch | 제작본부(글쓰기셀) | 마케팅 |
| seo·광고·마케팅 스킬 | 마케팅·배포 | — |
| harness·gan·webapp·dashboard | AI Tech | (발주 사업부) |
| church-accounting·finance·korean-law | 재무·관리 | — |
```

- [ ] **Step 2: 기존 커맨드 보존 검증** (Global Constraint — 커맨드 100% 유지)

Run:
```bash
ls /Users/kylechoi/Desktop/Ai_works/.claude/skills/ | grep -E "^sermon$|^env-scanner$|^lecture-design$|^youth-life-planner$" | sort
```
Expected: 핵심 스킬 실존(귀속만 추가, 변경 없음).

- [ ] **Step 3: 커밋**

```bash
git add .claude/org/command-map.md
git commit -m "feat(org): 커맨드·스킬 부서 귀속 매핑 (기존 커맨드 보존)"
```

---

### Task 7: 부서별 영구기억 초기화

**Files:**
- Create: `.claude/org/memory/<slug>.md` × 13 (board·ceo·cso·qa-office·ministry·intelligence·vision-edu·strategy·production·marketing·ai-tech·finance·research)

**Interfaces:**
- Produces: 13 부서 메모리 stub — 재귀적 자기개선 5단계의 저장처([[feedback_recursive_self_improvement]]).

- [ ] **Step 1: 13 메모리 stub 생성** — 각 파일은 동일 stub:
```markdown
# <부서명> 영구기억

> 부서 단위 누적 학습·SOP 개선 기록. 재귀적 자기개선 5단계의 4단계(저장) 결과를 여기 적재.

## 학습 로그
- (작업 완료마다 부서장이 추출한 패턴·교훈을 1줄씩 추가)
```

Run (생성 자동화 예시):
```bash
cd /Users/kylechoi/Desktop/Ai_works/.claude/org/memory
for s in board ceo cso qa-office ministry intelligence vision-edu strategy production marketing ai-tech finance research; do printf '# %s 영구기억\n\n> 부서 단위 누적 학습·SOP 개선 기록.\n\n## 학습 로그\n- (작업 완료마다 패턴·교훈 1줄 추가)\n' "$s" > "$s.md"; done
```

- [ ] **Step 2: 검증**

Run:
```bash
ls /Users/kylechoi/Desktop/Ai_works/.claude/org/memory/*.md | wc -l
```
Expected: 13.

- [ ] **Step 3: 커밋**

```bash
git add .claude/org/memory/
git commit -m "feat(org): 부서별 영구기억 13 stub 초기화"
```

---

### Task 8: 목회사역 사업부 파일럿 브링업 + 1사이클 검증 (운영)

> 전체 13노드 롤아웃 전에 **1개 사업부로 운영 모델을 검증**한다. CSO 공동 집행(자원 감시). 기존 디딤팀장(ws2/s5) 노드를 "목회사역 사업부장"으로 재정의해 재사용(신규 pane 최소화).

**Files:**
- Modify: `SESSION_STATE.md` (목회사역 노드 상태 갱신)
- Reference: `.claude/org/divisions/ministry.md`

**Interfaces:**
- Consumes: Task 2 ministry 헌장, Task 5 lifecycle 프로토콜.

- [ ] **Step 1: 현 노드 동적 해소** (회전ID 하드코딩 금지)

Run:
```bash
cmux tree --all
```
Expected: 디딤팀장 노드(탭="디딤주간작업") 현재 ws/surface 식별.

- [ ] **Step 2: 사업부장 헌장 주입** — 해소된 노드에 ministry 헌장 + WORKER_DIRECTIVE를 주입(브리핑):
```bash
cmux send --workspace <ws> --surface <surface> "[CEO→목회사역 사업부장] 너는 DiA Ai Edu. Solution 목회사역 사업부장이다. 헌장=.claude/org/divisions/ministry.md, 수명주기=.claude/org/lifecycle.md, 절대지침=.claude/WORKER_DIRECTIVE.md 를 읽고 복창하라."
cmux send-key --workspace <ws> --surface <surface> enter
```

- [ ] **Step 3: 1사이클 작업 — 전체 QA 게이트 파일럿 (적대검증 M1 반영)**

사업부장에게 작은 실산출물 지시(예: 다음 주차 묵상 1편 초안 또는 `/주간현황`). 산출 후 **이원화 검증 게이트를 실제로 통과**시켜 모델을 검증한다: ① 리서치·검증(Fact — 본문·출처 사실성) → ② 품질감사실(agy=신학·문체 / Codex=구조) → CEO 취합 → 회장 보고. 기존 커맨드가 새 조직 하에서 정상 작동(Virtual Matrix)하는지 함께 확인.

- [ ] **Step 4: 수명주기 + 서버위생 검증** — 작업 완료 후 노드 L1 대기 전이 확인, CSO 병행 자원 청정 검사:

Run:
```bash
cmux read-screen --workspace <ws> --surface <surface> | tail -20
```
Expected: 작업 완료·idle(L1) 대기. CSO 병행 — 서버위생 false-positive 차단(bun/vite만이 아니라 광범위):
```bash
ps aux | grep -E 'bun|vite|next|node .*(server|dev)|npm|pnpm|python.*http|uv run|streamlit' | grep -v grep | wc -l
```
Expected: 작업 전 대비 **신규 장기 리스너 0** (서버위생 무결).

- [ ] **Step 5: 파일럿 결과 기록 + 커밋**

SESSION_STATE에 파일럿 결과(목회사역 사업부 L0→L1 검증·기존 커맨드 정상·자원 청정) 1줄 기록.
```bash
git add SESSION_STATE.md
git commit -m "feat(org): 목회사역 사업부 파일럿 검증 — 커맨드 무결·수명주기·자원 청정"
```

---

## Phase 1b (별도 계획 — 파일럿 검증 후)

파일럿 PASS 후 나머지 사업부·본부 노드를 수요 기반으로 순차 브링업(수명주기 L2→L0). 전면 동시 기동 금지. 별도 plan 문서로 작성.

## Phase 1.5 (별도 계획)

통합 대시보드(조직 상태·각 부서 작업·자원·산출물 한눈에) — 전체 구축 검증 후 AI Tech 본부가 설계·구현.

---

## Self-Review

**Spec coverage:** spec 8장 Phase 1 항목 — 13부서 헌장(Task 2·3·4) ✓ / 노드 레지스트리 확장(Task 5) ✓ / 상주 인프라 메모리·라우팅(Task 6·7) ✓ / 대기모드(Task 5) ✓ / 기존 커맨드 부서 귀속(Task 6) ✓ / 목회사역 파일럿(Task 8) ✓. 대시보드=Phase 1.5 명시 연기 ✓. 전체 13노드 물리 롤아웃=Phase 1b 연기 ✓.

**Placeholder scan:** 헌장 내용은 표로 verbatim 값 제공(placeholder 아님). SOP는 부서 기존 워크플로우 참조. 검증 대부분 실행가능 bash. **단 Task 8은 운영 태스크 — `<ws>/<surface>`를 Step 1 `cmux tree` 동적 해소 결과로 치환 후 실행**(정적 bash 아님, 의도된 운영 절차 — 적대검증 M4 반영). 통과.

**Type consistency:** slug 명칭 일관(ministry·intelligence·vision-edu·strategy·production·marketing·ai-tech·finance·research·board·ceo·cso·qa-office) — Task 2·3·4·6·7·8 전반에서 동일 사용. 디렉토리 구조(divisions/hq/exec/memory) Task 1과 후속 일치. 통과.
