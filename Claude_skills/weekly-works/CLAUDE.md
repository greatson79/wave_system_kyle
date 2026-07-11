# Weekly Works — 디딤교회 주간 콘텐츠 통합 시스템

주간 반복 콘텐츠(설교, 매일묵상, 수요기도회, 소그룹 나눔지, SNS 카드뉴스)를
**하나의 폴더에서 통합 관리**하는 시스템입니다.

---

## 절대 기준 (Constitutional Rules)

> 이 섹션의 규칙은 어떤 상황에서도 예외 없이 적용된다.
> 효율, 속도, 편의를 이유로 절대 기준을 우회할 수 없다.
> 이 기준이 존재하는 이유는 `soul.md`에 기술되어 있다.

### 1. 품질 우선 (Quality First)

산출물의 품질이 최우선이다. 속도나 비용을 위해 품질을 타협하지 않는다.

- 15개 묵상 중 12개만 만들고 끝내는 것은 허용되지 않는다
- 토큰 절약을 위해 나눔지 질문을 축약하지 않는다
- 설교 단계를 건너뛰어 빠르게 끝내는 것보다, 단계를 밟아 품질을 높인다
- **신학적 정확성**은 모든 콘텐츠의 최소 요건이다

### 2. SOT 준수 (Single Source of Truth)

모든 데이터는 단일 진실 원천에서 읽어온다. AI가 "기억"으로 데이터를 만들지 않는다.

| SOT 데이터 | 파일 | 쓰기 권한 |
|-----------|------|----------|
| 주일설교 52주 | `data/sermon-plan-2026.json` → `sundays[]` | 사용자만 |
| 월삭 12개월 | `data/sermon-plan-2026.json` → `new_moon[]` | 사용자만 |
| 매일묵상 52주 | `.claude/skills/weekly-devotion/devotion-data.json` | 사용자만 |
| 수요기도회 | `data/prayer/*.csv` | 사용자만 |
| 설교 맥락 | `output/{월}/{주차}/설교/sermon-context.md` | Team Leader 생성 (Sermon Agent 산출물 기반) |
| 진행 상태 | `output/{월}/{주차}/status.md` | Team Leader만 |

위반 시: 산출물을 폐기하고 SOT에서 다시 읽어 재생성한다.

### 3. CCP 준수 (Context-Continuity Protocol)

세션 간 맥락을 반드시 이어받는다.

- 작업 시작 전 `output/{월}/{주차}/status.md` 확인 — 이미 완료된 작업을 중복 실행하지 않는다
- 설교 재개 시 기존 산출물(`1_상황파악.md` ~ `5_원고.md`) 존재 여부를 확인하고 이어서 진행한다
- `이어서` 플래그가 없더라도, status.md가 있으면 읽고 현황을 사용자에게 보고한다

### 4. 오류 복구 (Sisyphus Persistence)

에러 발생 시 포기하지 않는다.

1. 1차: 동일 방법 재시도
2. 2차: 대안 방법 시도 (다른 템플릿, 다른 경로, 다른 도구)
3. 3차: 또 다른 대안 시도
4. 3회 실패 후: 사용자에게 정직하게 보고 — 무엇을 시도했고, 왜 실패했는지 명시

"일부만 완료"는 보고 대상이다. 조용히 넘어가지 않는다.

## 프로젝트 구조

```
weekly-works/
├── CLAUDE.md              ← 이 파일
├── .claude/
│   ├── commands/
│   │   ├── 주간총괄.md    ← /주간총괄 [주차] 커맨드
│   │   └── 주간현황.md    ← /주간현황 커맨드
│   └── skills/
│       ├── team-leader/   ← 주간 작업 총괄 팀 리더
│       │   ├── team-leader_SKILL.md
│       │   └── rules/
│       │       ├── workflow-dag.md      ← DAG 의존성 맵
│       │       ├── quality-gates.md     ← 품질 게이트
│       │       ├── agent-registry.md    ← 소환 가능 에이전트 등록부
│       │       └── agent-protocol.md    ← 3가지 소환 패턴 (A/B/C)
│       ├── sermon/        ← 설교 준비 5단계
│       │   ├── sermon_SKILL.md
│       │   └── rules/
│       ├── weekly-devotion/ ← 매일묵상 15개 HTML
│       │   ├── SKILL.md
│       │   ├── devotion-data.json
│       │   └── templates/
│       ├── insert-images/ ← 묵상 이미지 삽입 + A4 캡쳐
│       │   └── SKILL.md
│       ├── prayer-doc/    ← 수요기도회 기도카드
│       │   ├── SKILL.md
│       │   └── scripts/
│       ├── small-group/   ← 소그룹 나눔지 (장년+청소년)
│       │   ├── small-group_SKILL.md
│       │   └── rules/
│       └── sns-cardnews/  ← SNS 카드뉴스
│           ├── sns-cardnews_SKILL.md
│           └── rules/
├── data/
│   ├── sermon-plan-2026.json  ← 52주 설교 + 12개월 월삭
│   └── prayer/*.csv           ← 수요기도회 CSV
├── src/
│   ├── assets/
│   │   ├── colors/brand-guide.md
│   │   └── logos/ (didim-logo.png, prayer-logo.png)
│   ├── templates/
│   ├── scripts/capture-a4.js
│   └── samples/
├── output/                ← 모든 결과물 (월/주차별 정리)
│   └── {월}/{월내주차}주차/
│       ├── 매일묵상/     (html-original, html-with-images, captured, images)
│       ├── 수요기도회/   (HTML + PNG)
│       ├── 설교/         (5단계 산출물)
│       ├── 소그룹나눔지/ (장년 + 청소년)
│       └── 카드뉴스/     (슬라이드 + 캡션)
├── package.json           ← Puppeteer 등 Node 의존성
└── .wp-config.json        ← WordPress 인증 (gitignore)
```

## 사용 방법

### 주간 전체 실행 (Team Leader)
```
/주간총괄 [주차번호]
```
- Phase 1-Auto: 매일묵상 + 기도카드 (Agent 백그라운드 병렬 소환)
- Phase 1-Interactive: 설교 (메인 대화 — 심층 연구 에이전트 소환 가능)
- Phase 2: 소그룹 나눔지 + SNS 카드뉴스 (설교 완료 후 백그라운드 병렬 소환)

### 외부 에이전트 등록
`agent-registry.md`에 새 섹션을 추가하면 Team Leader가 소환 가능:
- Sermon-Assistant 11개 연구 에이전트 (심층 연구)
- Wave-AI 4개 범용 에이전트 (리서치, 콘텐츠, 지식설계)
- 새 프로젝트 에이전트: source 경로 + type(auto/interactive/research) 지정

### 선택 실행
| 플래그 | 동작 |
|--------|------|
| `--설교만` | 설교 준비만 |
| `--묵상만` | 매일묵상만 |
| `--기도만` | 기도카드만 |
| `--나눔지만` | 소그룹 나눔지만 (설교 완료 전제) |
| `--카드뉴스만` | SNS 카드뉴스만 (설교 완료 전제) |
| `이어서` | 진행 중 작업 재개 |

### 개별 스킬 실행
- `/weekly-devotion [주차]` — 매일묵상 15개 HTML
- `/insert-images [주차] [이미지경로]` — 이미지 삽입 + PNG 캡쳐
- `/설교 [본문]` — 설교 준비 5단계
- `/주간현황` — 진행 상태 대시보드

## DAG (워크플로우 순서)

```
설교 1~4-4단계(대화형) ∥ 매일묵상(자동) ∥ 기도카드(자동)
         ↓
    4-1 제목확정 → 4-2 전개방식확정 → 4-3 예화설계 → 4-4 아웃라인작성 → sermon-context.md 갱신
         ↓               ↓                    ↓
  5단계 원고(대화형)  소그룹 나눔지(자동)   디자인스카우트(자동)
                                                   ↓
                                            SNS 카드뉴스(자동)
                     ↓                          ↓
                         주간 보고서 (D+E 완료 후)
```
> **Phase 2 트리거**: 4-4단계 아웃라인 작성 완료 시 소그룹 나눔지(D)·디자인스카우트(E0) 자동 동시 소환. 5단계 원고 완료를 기다리지 않는다.

## 자동화 훅 — 이미지 감지 → insert-images 자동 실행

매일묵상 `images/` 폴더에 mon~fri 이미지 5장이 모이면 insert-images 파이프라인이 자동 실행됩니다.

### 작동 방식
| 경로 | 역할 |
|------|------|
| `src/scripts/watch-devotion-images.sh` | fswatch 기반 파일시스템 감시 (수동 이미지 추가 시) |
| `src/scripts/auto-insert-trigger.sh` | Claude Write 훅 (Claude가 이미지 생성 시) |
| `src/scripts/check-devotion-done.sh` | captured/ 10개+ 시 status.md 자동 완료 처리 |
| `.claude/settings.local.json` | PostToolUse Write 훅 등록 |

### 시작 방법
```bash
# fswatch 최초 설치 (1회)
npm run setup:watcher

# 감시 시작 (주간 작업 시작 시 별도 터미널에서 실행)
npm run watch:images
```

### 트리거 조건
- `output/{월}/{주차}/매일묵상/images/` 폴더에 mon/tue/wed/thu/fri 확장자 파일 5장 감지
- 락 파일(`.pipeline_running`) 으로 중복 실행 방지
- 완료 시 `status.md` B. 매일묵상 → ✅완료 자동 갱신

## 실행 환경
- Node.js 18+ (Puppeteer A4 캡쳐)
- Python 3.12+ (기도카드 파이프라인)
- fswatch (이미지 자동감지): `brew install fswatch`
- wkhtmltoimage (PNG 캡쳐, 선택)
