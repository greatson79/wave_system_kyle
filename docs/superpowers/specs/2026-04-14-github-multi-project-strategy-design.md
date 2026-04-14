# GitHub 다중 프로젝트 운영 전략 — 구현 스펙

> **작성일:** 2026-04-14  
> **기반 문서:** `/Users/kylechoi/Desktop/Ai_works/github-multi-project-strategy.md`  
> **GitHub 계정:** greatson79  
> **원작자:** https://github.com/idoforgod

---

## 1. 아키텍처

```
github.com/idoforgod/AgenticWorkflow-Template  (원작자 — 수정 불가)
                    ↓ GitHub 포크 (브라우저 1회)
github.com/greatson79/agenticworkflow-mirror   (STEP 1 허브)
     ├── greatson79/environmentscan            (STEP 2 — output 경로 커스텀)
     ├── greatson79/globalnews                 (STEP 2 — output 경로 커스텀, remote 정리)
     ├── greatson79/sermon-assistant           (STEP 2 — 수정 없음, 구조 셋업)
     └── greatson79/dissertation-simulator    (STEP 2 — 수정 없음, 구조 셋업)
```

---

## 2. 프로젝트 현황

| 프로젝트 | 로컬 경로 | git 상태 | GitHub repo | Kyle 수정 |
|----------|-----------|----------|-------------|-----------|
| agenticworkflow-mirror | 신규 생성 | 없음 | 포크 필요 | - |
| environmentscan | Vibe-Practice/EnvironmentScan-system-main-v4-main | git 없음 | 없음 | output 경로 |
| globalnews | Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow | git 있음 (remote 오염) | 있음 | output 경로 |
| sermon-assistant | Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main | git 없음 | 없음 | 없음 |
| dissertation-simulator | Vibe-Practice/Dissertation-Simulator-AgenticWorkflow-main | git 없음 | 없음 | 없음 |

### GlobalNews remote 오염 내역
- `origin` → `https://github.com/greatson79/church-automation.git` ← 잘못된 연결 (삭제 대상)
- `globalnews` → `https://github.com/greatson79/GlobalNews-Crawling-AgenticWorkflow.git` ← 정상 (upstream으로 rename)
- `chatting-room` → 불명 (삭제 대상)

---

## 3. 각 프로젝트 공통 구조 (STEP 2)

```
project/
├── core/           # idoforgod 원본 코드 전체를 그대로 이동 (수정 절대 금지)
├── shared/         # agenticworkflow-mirror/shared 공통 자산
├── custom/         # Kyle님 수정 코드만 여기에 (output 경로 등)
│   └── config/     #   커스텀 설정 파일
├── config/         # 프로젝트별 설정
└── .upstream-version
```

> **core/ 이동 원칙:** 다운로드된 원작자 파일 전체(docs, scripts, agents 등)를 core/ 하위로 이동.  
> 기존 파일 구조는 core/ 안에서 그대로 유지. Kyle님 수정분만 custom/에 별도 보관.

`.upstream-version` 형식:
```
upstream_commit: <해시>
upstream_tag: <버전>
synced_at: 2026-04-14
```

---

## 4. 브랜치 전략 (STEP 3) — 4개 프로젝트 공통

```
main        ← base(agenticworkflow-mirror) 상태 유지. 직접 커밋 금지.
  └── dev   ← 커스텀 개발 브랜치
        └── feature/xxx
```

| 브랜치 | 역할 | 직접 커밋 |
|--------|------|----------|
| `main` | upstream 상태 유지 | 금지 |
| `dev` | 커스텀 코드 통합 | 머지만 |
| `feature/*` | 기능 단위 개발 | 허용 |

---

## 5. Remote 구성 (각 프로젝트)

```
origin    → github.com/greatson79/<프로젝트명>   (내 GitHub repo)
base      → github.com/greatson79/agenticworkflow-mirror (부모 프레임워크 허브)
upstream  → github.com/idoforgod/<원작자 레포명>  (원작자 프로젝트별 레포)
```

### 원작자 upstream URL 매핑
| 프로젝트 | upstream URL |
|----------|-------------|
| environmentscan | https://github.com/idoforgod/EnvironmentScan-system |
| globalnews | https://github.com/idoforgod/GlobalNews-Crawling-AgenticWorkflow |
| sermon-assistant | https://github.com/idoforgod/Sermon-Assistant-AgenticWorkflow |
| dissertation-simulator | https://github.com/idoforgod/Dissertation-Simulator-AgenticWorkflow |

> ⚠️ 위 URL은 추정값. 구현 시작 전 https://github.com/idoforgod 에서 정확한 레포명 확인 필요.

### GitHub repo 공개 범위
| 프로젝트 | public/private |
|----------|---------------|
| agenticworkflow-mirror | public (원작자 코드 포크) |
| environmentscan | public |
| globalnews | public (이미 존재) |
| sermon-assistant | public |
| dissertation-simulator | public |

---

## 6. agenticworkflow-mirror 디렉토리 구조 (STEP 1)

```
agenticworkflow-mirror/
├── core/           # AgenticWorkflow-Template 원본 코드 (수정 금지)
├── shared/         # 4개 프로젝트 공통 자산
│   ├── config/     #   공통 환경설정 템플릿
│   └── utils/      #   공통 헬퍼 함수·유틸리티
└── .upstream-version
```

---

## 7. Upstream 싱크 절차 (STEP 5)

### Phase 1: agenticworkflow-mirror에서 먼저 검증
```bash
cd agenticworkflow-mirror
git fetch upstream
git log upstream/main --oneline -10
git merge upstream/main
echo "upstream_commit: $(git rev-parse upstream/main | head -c 7)" > .upstream-version
git push origin main
```

### Phase 2: 각 프로젝트에 선택적 반영
```bash
cd <project>
git fetch base
git checkout main && git merge base/main
git checkout dev && git merge main
```

---

## 8. 구현 순서

| 순서 | 작업 | 방법 | 선행 조건 |
|------|------|------|----------|
| 0 | idoforgod/AgenticWorkflow-Template 포크 | 브라우저 (Kyle님 직접) | - |
| 1 | agenticworkflow-mirror 로컬 셋업 (core/, shared/, .upstream-version) | 터미널 | Step 0 완료 |
| 2 | environmentscan: git init + 구조 셋업 + GitHub repo 생성 + push | 터미널 | Step 1 완료 |
| 3 | globalnews: remote 정리 + 구조 셋업 + push | 터미널 | Step 1 완료 |
| 4 | sermon-assistant: git init + 구조 셋업 + GitHub repo 생성 + push | 터미널 | Step 1 완료 |
| 5 | dissertation-simulator: git init + 구조 셋업 + GitHub repo 생성 + push | 터미널 | Step 1 완료 |

---

## 9. 제외 항목 (별도 작업)

| 프로젝트 | 이유 |
|----------|------|
| InvestScan | Kyle님 독자 설계 프로젝트 |
| weekly-works | Kyle님 독자 설계 프로젝트 |

---

## 10. 코드 작성 원칙 (STEP 4)

- `core/` 절대 수정 금지
- 모든 커스텀 코드는 `custom/`에만
- upstream 업데이트는 반드시 `git merge`로 (덮어쓰기 금지)

```python
# custom/config/output_path.py — 커스텀 예시
OUTPUT_BASE_PATH = "/Users/kylechoi/Desktop/Ai_works/output"
```
