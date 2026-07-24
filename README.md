# Wave System Kyle — Wave AI Networks 운영 저장소

> **Wave AI Networks** · 한 명의 목회자(오너)를 섬기는 **멀티-에이전트 AI 조직 시스템**.
> 디딤교회 콘텐츠 자동화(설교·주간사역·교육)와 회사(Wave AI Networks) 운영 — 콘텐츠 제작·발행·리서치·개발 — 을
> **8본부 15팀의 AI 에이전트 조직**이 거버넌스 규율 아래 수행한다.

---

## 1. 시스템 개요

이 저장소는 단순한 코드 저장소가 아니라 **AI 에이전트 조직의 본사(HQ)** 다.

- **오너(주인님)** 가 최종 승인·방향을 결정하고,
- **총괄(CEO·마스터)** 이 전략·게이트·라우팅을 맡으며,
- **COO·CSO·리뷰어(agy·Codex)** 가 상주 관제타워를 이루고,
- **8개 본부**의 AI 본부장·팀·워커가 실작업을 수행한다.

에이전트는 Claude·Codex(OpenAI)·agy(Antigravity/Gemini) **3엔진**을 적재적소에 선발해 쓰며,
모든 산출물은 **적대적 검수(빌더≠리뷰어)** 와 **결정론 검증**(도구 출력만이 사실)을 거친다.

## 2. 거버넌스 2계층

| 계층 | 위치 | 내용 |
|---|---|---|
| **엔진 계층 (CYS)** | `~/.cys/pack/directives/` (외부) · git 동결사본 = [`.claude/_engine-snapshot/`](.claude/_engine-snapshot/) | 부트·결정론 검증·라운드 루프·컨텍스트 사이클의 메커니즘 정본 |
| **조직 확장층** | [`.claude/`](.claude/) (이 저장소) | Wave AI Networks 조직·발행 거버넌스·도메인 규칙 — 오너가 설계 |

**지침 계층 (상속 하향)**: `soul.md`(L0 불변 정체) → `CLAUDE.md`+DIRECTIVE 4종(L1) →
[`.claude/org/README.md`](.claude/org/README.md)(L2 조직도) →
[`.claude/org/전체작업진행지침.md`](.claude/org/전체작업진행지침.md)(**L2.5 — 운영 정본**) →
[`.claude/org/hq/{본부}/`](.claude/org/hq/)(L3 본부·팀 지침 31파일).
하위는 상위를 복붙하지 않고 **참조·상속**하며, 상위보다 느슨한 기준은 무효다.

## 3. 조직 — 8본부 단층 · 15팀 (2026-07-23 개정)

```
오너(주인님) ← 총괄(CEO) ← COO ← 본부장 ← (작업팀장) ← 워커      [운영 평면·불변]
                └ 본부장 전략회의(CEO+COO+안건 본부장·매주 월)      [전략 평면]
```

| # | 본부 | 팀 | 핵심 소관 |
|---|---|---|---|
| 1 | **경영본부** | 전략팀 | 전략·조직설계·지침·llm-wiki |
| 2 | **개발본부** | AI제품개발팀 · 플랫폼·릴리즈팀 | 앱·홈페이지·발행 포스팅·Git/Vercel·자동화 |
| 3 | **크리에이티브본부** | 콘텐츠제작팀 · 검수·브랜드팀 | 콘텐츠 제작 / 브랜드·디자인시스템 스튜어드 |
| 4 | **마케팅본부** | SNS운영팀 · 성장마케팅팀 | 오가닉 소셜 / SEO·광고·퍼널 |
| 5 | **재무본부** | (본부장 직할) | 회사 재무 |
| 6 | **리서치본부** | 리서치1(envscan)·리서치2·투자분석·포사이트 | 환경스캐닝·조사·투자분석·미래예측 |
| 7 | **목회사역본부** | 주간콘텐츠팀 · 교회행정팀 | 주간사역(설교·묵상)·교회행정·church-accounting |
| 8 | **Edu본부** | 커리큘럼설계팀 · 비전코칭팀 | 교육 설계 / 청소년 비전코칭 |

- **상주 = 관제타워 4종**(CEO·COO·CSO·리뷰어 2)뿐 — 본부는 **이벤트 구동**(소환→작업→완료보고→해제).
- 본부장 임명 = **3엔진 선발**(Codex·agy·Claude — [`본부장_임명지침.md`](.claude/org/본부장_임명지침.md)).

## 4. 폴더 구조 — 축(axis) 체계

| 축 | 폴더 | git | 내용 |
|---|---|---|---|
| **지침 축** | [`.claude/`](.claude/) + `soul.md`·`CLAUDE.md`·`memory.md`·`RECOVERY.md` | ✅ 추적 | 정본 지침·헌장·스킬 레지스트리·어댑터 |
| **산출물 축** | `output/WaveAI/{본부}/{팀}/` | ❌ 미추적 | 작업 산출물(보고서·콘텐츠·검수판정) — 4슬롯(`_round`·`_assets`·`_archive`·`projects`·`deliverables`) |
| **워크플로우 정본** | [`_workflowhome/`](_workflowhome/) | ✅ | 모든 워크플로우 원본(envscan·GlobalNews·Sermon-Assistant·하네스 등) — 본부는 심링크로 접근 |
| **본부 작업 축** | `개발본부/`·`리서치본부/`·`목회사역본부/`·`크리에이티브본부/`·`경영본부/`·`Edu본부/` | ✅ | 본부별 작업 자산(실폴더+워크플로우 심링크). 자산 0인 본부(마케팅·재무)는 폴더 없음(빈 폴더 금지) |
| **스킬 축** | [`_skills/`](_skills/) + `.claude/skills/`(심링크 레지스트리 430+) | ✅ | external(오픈소스 gitlink)·standalone(자체 스킬) |
| **문서 축** | [`_Docs/`](_Docs/) | ✅ | 참고 문서·PDF·Translive 등 |
| **이력 축** | `_archive/`·`_zip-archives/` | ✅ | 구본·백업(치환 금지 — 역사 증적) |

**핵심 원칙**: 지침을 산출물 축에 두지 않는다(미추적=소실 위험). 산출물을 지침 축에 두지 않는다.
gitlink(외부 repo)는 **물리이동 금지 — 심링크 접근만**.

## 5. 런타임

- **메인 = cmux.app** (2026-07-10 확정) · cys.app = 보조. 본부 = cmux 물리 워크스페이스(오너 화면에 실 pane 가시화).
- 관제타워 부트: `bash .claude/cmux-adapters/boot_tower.sh` (4종 의무 노드·멱등).
- **통신 규약**: 주소는 항상 `workspace:N`/`surface:M` **prefixed ref** — bare 숫자 금지(positional index 오배송 실증으로 규약화). 완결보고급은 read-screen 착지 확인.
- 본부 소환 표준: [`.claude/org/HQ_SUMMON_STANDARD.md`](.claude/org/HQ_SUMMON_STANDARD.md).

## 6. 운영 원칙 (요약 — 정본은 `전체작업진행지침.md`)

1. **품질 절대우선·환각 0** — 검색-우선·회의주의·2-cycle 검증. 속도·토큰은 이유가 못 된다.
2. **결정론 환원** — 진행률·존재검증·게이트 판정은 도구 출력만이 사실(눈대중 금지).
3. **자율주행 + denylist** — denylist(soul·헌장 변경·외부발행·비가역삭제) 밖·가역이면 무정지 진행. denylist는 오너 게이트.
4. **검수 게이트** — 모든 산출물은 완결보고 전 리뷰어(agy+Codex 적대검수) 통과. verdict 계약(`ACCEPT|REVISE|BLOCK`+evidence).
5. **발행 대원칙** — 제작→발행 전자동 + **발행 직전 오너 최종검수가 유일한 격발**(블로그만 CEO 위임 예외).
6. **스킬베이스 2트랙** — 트랙1(파이프라인: envscan·주간작업 등)은 완주가 준수, 트랙2는 업무유형별 필수 스킬 발동+기록 의무.
7. **무손실 연속성** — 콜드 복구 = [`RECOVERY.md`](RECOVERY.md) + `_round/SESSION_STATE.md`(훅 주입 정본).

## 7. 주요 워크플로우

| 워크플로우 | 소관 | 진입 |
|---|---|---|
| 주간사역(설교·묵상·기도카드·나눔지·카드뉴스) | 목회사역본부 | `/주간총괄` (`목회사역본부/weekly-works/`) |
| 환경스캐닝(envscan 5WF·일일) | 리서치본부 | `_workflowhome/EnvironmentScan-…` (launchd) |
| 블로그 발행(주 5회 편성) | 크리(제작)→개발(포스팅) | [`.claude/org/WEEKLY_SCHEDULE.md`](.claude/org/WEEKLY_SCHEDULE.md) |
| 투자분석(invest_scan·주간) | 리서치본부 | `리서치본부/invest_scan/` |
| 청소년 비전코칭 | Edu본부 | `/인터뷰`·`/수련회` (`Edu본부/youth_life_plan/`) |
| 홈페이지(waveainetworks.com) | 개발본부 | `wave-homepage` |

## 8. 설치 방법

### 8-1. 사전 요구사항

| 도구 | 용도 | 설치 |
|---|---|---|
| **macOS** | 기준 플랫폼(launchd·cmux) | — |
| **Claude Code CLI** | 메인 에이전트 엔진 | `npm install -g @anthropic-ai/claude-code` → `claude` 로그인 |
| **cmux.app** | 메인 런타임(워크스페이스·pane) | cmux.app 설치 → `/Applications/cmux.app` (CLI: `cmux` PATH 등록) |
| **Codex CLI** | 코드·이미지 워커 엔진 | `npm install -g @openai/codex` → `codex` 로그인(오너 구독 계정) |
| **agy (Antigravity)** | 리뷰·디자인 엔진 | `~/.local/bin/agy` — Gemini 계열·`greatson79@dia-io.com` 인증 |
| **gh (GitHub CLI)** | 저장소·발행 자동화 | `brew install gh` → `gh auth login` |
| **git 2.40+ / python3 / node 18+** | 기반 도구 | brew·pyenv·fnm 등(★fnm은 launchd에서 고정경로 필요 — 함정 주의) |
| **cys.app** (선택·보조) | 보조 런타임(`cys recall` 등) | 설치 시 `~/.cys/pack/` 엔진 지침 제공 |

### 8-2. 저장소 설치

```bash
# 1) 클론 (private — gh 인증 필요)
gh repo clone greatson79/wave_system_kyle ~/Desktop/Ai_works
cd ~/Desktop/Ai_works

# 2) ★gitlink(외부 워크플로우 repo) 초기화 — 이 저장소는 .gitmodules 없는 gitlink 방식.
#    필요한 워크플로우만 개별 클론한다(전부 필수 아님·해당 본부 가동 시):
git ls-files -s | awk '$1=="160000" {print $4}'          # gitlink 목록 확인
gh repo clone greatson79/EnvironmentScan-system-main-v4 "_workflowhome/EnvironmentScan-system-main-v4-main"   # 예: envscan
#    ⚠ remote 없는 gitlink 3종(church-accounting·Translive·youth-life-planner)은 오너 로컬/백업에서만 복원 가능.

# 3) 스킬 레지스트리 재구축 (심링크 430+ — 경로 의존이라 클론 후 필수)
bash .claude/build_skill_registry.sh

# 4) 주간사역 파이프라인 의존성 (목회사역본부 가동 시)
cd 목회사역본부/weekly-works && npm install && cd ../..

# 5) 전역 도구 (해당 기능 사용 시)
uv tool install notebooklm-mcp-cli && nlm login          # NotebookLM MCP
uv tool install yt-dlp                                    # 영상 수집
```

### 8-3. MCP·자동화 배선 (선택 — 기능별)

- **MCP 서버**: `.mcp.json`에 선언(korean-law=`npx korean-law-mcp`·notebooklm·serena 등) — Claude Code가 자동 기동.
- **launchd 잡**: 정기 자동화(envscan 일일·주간 발행 리마인더 등)는 `~/Library/LaunchAgents/com.wave.*` +
  실행 스크립트는 **TCC 경로 밖**(`~/WAVE/aiworks-jobs/`) 배치가 규율(무음실패 방지).
- **비밀값**: API 키·인증은 저장소에 두지 않는다 — 각 CLI 로그인·환경변수·keyring으로만.

### 8-4. 시작하기 (새 세션·콜드 복구)

```bash
cd ~/Desktop/Ai_works
claude --dangerously-skip-permissions   # CLAUDE.md가 거버넌스 자동 로드
```

1. 오너가 **"너는 마스터다"** 선언 → 총괄(CEO) 각성
2. 프리플라이트(`python3 ~/.cys/pack/bin/javis_preflight.py` — cys 설치 시) → 콜드 앵커 재독(`_round/SESSION_STATE.md`·`RECOVERY.md`)
3. `bash .claude/cmux-adapters/boot_tower.sh` → 관제타워 4종(COO·CSO·리뷰어 2) 자동 편성
4. 본부는 필요 시 소환([`HQ_SUMMON_STANDARD.md`](.claude/org/HQ_SUMMON_STANDARD.md))

상세: [`CLAUDE.md`](CLAUDE.md)(진입 정본) · [`RECOVERY.md`](RECOVERY.md)(콜드 복구) ·
[`AGENTS.md`](AGENTS.md)(비-Claude 에이전트용 미러).

---

*Private repository · Wave AI Networks · 정본 지침과 충돌 시 [`전체작업진행지침.md`](.claude/org/전체작업진행지침.md)이 우선한다.*
