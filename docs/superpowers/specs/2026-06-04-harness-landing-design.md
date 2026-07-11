# harness-landing — Next.js 랜딩페이지 전용 하네스 설계

> 작성일: 2026-06-04 · 상태: 승인됨 · 기반: 기존 `harness/` (3-에이전트 GAN 루프)

## 목표

기존 `harness/`(Planner → Generator ↔ Evaluator GAN 루프)를 **통째 복사**해
`harness-landing/`을 만들고, **Next.js/React 랜딩페이지**를 자율적으로 빌드하도록 특화한다.
검증된 오케스트레이션 배관(`run_harness.py`·`_runtime.py`·`_context.py`·schemas)은
변경하지 않는다.

## 결정 사항 (사용자 승인)

| 축 | 결정 |
|----|------|
| 홈페이지 종류 | 랜딩페이지 전문 |
| 기술 스택 | Next.js(App Router) + TypeScript + Tailwind |
| 실행 방식 | 기존 Python GAN 루프 재사용 |
| 특화 방식 | **전용 복사본**(`harness-landing/`) 생성 — 기존 범용 빌더 무손상 |

## 아키텍처 (불변)

파일 기반 통신(`artifacts/`) + 시그널 토큰 + JSON 사이드카 스키마 검증 +
`workspace/<run-id>/` 격리 빌드(자체 git) + 스프린트별 커밋 롤백.
오케스트레이터 로직은 그대로 둔다.

## 변경 대상

### 1. `config/harness_config.yaml`
- `max_sprints: 8 → 5` (단일 페이지는 과분해 시 패딩 발생)
- 평가 가중치 재조정 (합 1.0 유지, 로더 강제):
  - design_quality 0.35 (유지)
  - originality 0.30 → **0.25**
  - craft 0.20 → **0.25** (반응형·성능·접근성이 앱보다 중요)
  - functionality 0.15 (유지)
- thresholds: design 6 / originality 6 / craft 7 / functionality 7 (유지)

### 2. `criteria/landing_playbook.md` (신규 — 최고 가치 산출물)
`--bare` 모드가 전역 web 규칙(`~/.claude/rules/web/*`)을 차단하므로, 그 핵심을
하네스 내부에 번들해 인증 모드와 무관하게 3개 에이전트에 전달한다:
- Core Web Vitals 예산(LCP<2.5s, CLS<0.1, INP<200ms, FCP<1.5s) + 번들 버짓
- 반응형 브레이크포인트(320/375/768/1024/1440/1920)
- anti-template 디자인 체크리스트(금지 패턴 + 필수 품질)
- 시맨틱 HTML, CSS 커스텀 프로퍼티/디자인 토큰
- 컴포지터 친화 애니메이션(transform/opacity/clip-path만)
- Next.js App Router 컨벤션(Image/font/metadata/정적 export)
- 보안 헤더/CSP 기본

### 3. `prompts/planner_system.md`
- 기본 스택 Next.js, `backend: "None — static export"`, `ai: "None unless requested"`
- **AI 기능 의무 삭제** → 선택사항
- 랜딩페이지 스프린트 템플릿(아래) 제시, 플레이북 참조

### 4. `prompts/generator_system.md`
- 스택을 Next.js App Router + TS + Tailwind로 교체 (FastAPI/SQLite 기본값 제거)
- `npm run dev` / `http://localhost:3000`
- AI 통합 의무 제거, 플레이북 참조 의무화

### 5. `prompts/evaluator_system.md` + `criteria/evaluation_criteria.md`
- QA 항목: 320/768/1024/1440 반응형, CTA 작동, 폼 검증·제출, 링크 해결,
  오버플로 없음, CWV/Lighthouse, a11y(키보드·대비·reduced-motion)
- Functionality 차원을 "AI end-to-end" → "CTA 발동·폼 제출·링크 해결·반응형·CWV"로 재정의

### 6. `agents/planner.py` · `agents/generator.py`
- planner: `add_dirs`에 `criteria/` 추가(플레이북 접근), dry-run 스텁을 랜딩/Next.js로
- generator: dry-run 스텁 `tech_decisions` Next.js, `app_url` 5173 → **3000**

### 7. `HARNESS_README.md` · `CLAUDE.md` (복사본 내)
- 랜딩페이지 목적 반영, 변경 이력 기록

## 랜딩페이지 스프린트 템플릿

1. **히어로 + 셸 + 디자인 토큰** — 레이아웃 셸, 폰트/색 토큰, above-the-fold 히어로
2. **콘텐츠 섹션** — 기능/혜택, 사회적 증거, 가격, FAQ, 푸터
3. **반응형 + 모션** — 전 브레이크포인트, 스크롤/호버 모션(컴포지터 친화)
4. **접근성 + 성능 + SEO** — a11y, CWV 충족, 메타/OG/구조화 데이터
5. **(선택) 폼/통합/폴리시** — 리드 폼·뉴스레터, 최종 다듬기

## 스키마 변경 없음

`tech_stack.backend/ai`는 문자열이라 `"None"`으로 스키마 충족.
`ai_integration_points`는 선택 필드. 검증된 스키마/배관 그대로 유지.

## 검증

`python tests/test_harness_wiring.py`(무료) → `--check`(실 CLI, ~8¢) → `--dry-run` →
실 빌드. 프롬프트 수정 후 dry-run 재실행 필수. weights 합 1.0 확인.
