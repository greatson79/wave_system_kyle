# GitHub 다중 프로젝트 운영 전략 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** idoforgod의 AgenticWorkflow-Template을 허브로 포크하고, 4개 하위 프로젝트(environmentscan, globalnews, sermon-assistant, dissertation-simulator)를 독립 GitHub 레포로 구성하여 upstream 싱크 구조를 완성한다.

**Architecture:** agenticworkflow-mirror(허브)를 idoforgod/AgenticWorkflow-Template의 포크로 생성하고, 각 프로젝트에 `origin`(내 GitHub repo), `base`(허브), `upstream`(idoforgod 개별 레포) 3개의 remote를 설정한다. 각 프로젝트는 main(upstream 상태 유지)과 dev(커스텀 개발) 브랜치를 운영한다.

**Tech Stack:** git, GitHub CLI (gh), bash

---

## 사전 확인 사항 (구현 전 Kyle님 수동 작업)

> ⚠️ 아래 두 작업은 브라우저와 GitHub 계정이 필요하여 Claude가 직접 실행 불가.

1. **AgenticWorkflow-Template 포크:** 브라우저에서 `https://github.com/idoforgod/AgenticWorkflow-Template` → Fork → 레포 이름: `agenticworkflow-mirror` → `greatson79/agenticworkflow-mirror` 생성
2. **idoforgod 레포명 확인:** `https://github.com/idoforgod` 에서 아래 4개 레포의 정확한 이름 확인

| 예상 이름 | 실제 이름 (확인 후 기입) |
|----------|----------------------|
| EnvironmentScan-system | |
| GlobalNews-Crawling-AgenticWorkflow | |
| Sermon-Assistant-AgenticWorkflow | |
| Dissertation-Simulator-AgenticWorkflow | |

---

## Task 1: agenticworkflow-mirror 허브 셋업

**Files:**
- Create: `/Users/kylechoi/Desktop/Ai_works/agenticworkflow-mirror/shared/.gitkeep`
- Create: `/Users/kylechoi/Desktop/Ai_works/agenticworkflow-mirror/.upstream-version`

- [ ] **Step 1: 포크된 레포를 로컬에 클론**

```bash
cd /Users/kylechoi/Desktop/Ai_works
git clone https://github.com/greatson79/agenticworkflow-mirror
cd agenticworkflow-mirror
```

- [ ] **Step 2: upstream remote 등록**

```bash
git remote add upstream https://github.com/idoforgod/AgenticWorkflow-Template
git fetch upstream
```

- [ ] **Step 3: remote 구성 확인**

```bash
git remote -v
```
Expected:
```
origin    https://github.com/greatson79/agenticworkflow-mirror.git (fetch)
origin    https://github.com/greatson79/agenticworkflow-mirror.git (push)
upstream  https://github.com/idoforgod/AgenticWorkflow-Template.git (fetch)
upstream  https://github.com/idoforgod/AgenticWorkflow-Template.git (push)
```

- [ ] **Step 4: 디렉토리 구조 생성**

```bash
mkdir -p shared/config shared/utils
touch shared/.gitkeep
```

- [ ] **Step 5: .upstream-version 파일 생성**

```bash
COMMIT=$(git rev-parse upstream/main | head -c 7)
cat > .upstream-version << EOF
upstream_commit: ${COMMIT}
upstream_tag: latest
synced_at: $(date +%Y-%m-%d)
EOF
cat .upstream-version
```

- [ ] **Step 6: 커밋 및 push**

```bash
git add shared/ .upstream-version
git commit -m "feat: agenticworkflow-mirror 허브 구조 셋업 — shared/, .upstream-version 추가"
git push origin main
```

- [ ] **Step 7: GitHub에서 확인**

```bash
gh repo view greatson79/agenticworkflow-mirror
```
Expected: repo 정보 출력 확인

---

## Task 2: environmentscan 셋업

**로컬 경로:** `/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/EnvironmentScan-system-main-v4-main`  
**GitHub 레포:** `greatson79/environmentscan` (신규 생성)

**Files:**
- Create: `Vibe-Practice/EnvironmentScan-system-main-v4-main/custom/config/output_path.md`
- Create: `Vibe-Practice/EnvironmentScan-system-main-v4-main/shared/.gitkeep`
- Create: `Vibe-Practice/EnvironmentScan-system-main-v4-main/.upstream-version`
- Create: `Vibe-Practice/EnvironmentScan-system-main-v4-main/.gitignore`

- [ ] **Step 1: 디렉토리로 이동 및 git 초기화**

```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/EnvironmentScan-system-main-v4-main
git init
git checkout -b main
```

- [ ] **Step 2: custom/, shared/ 디렉토리 생성**

```bash
mkdir -p custom/config
touch custom/config/.gitkeep shared/.gitkeep
```

- [ ] **Step 3: output 경로 커스텀 설정 파일 작성**

output 경로 수정 내역을 `custom/config/output_path.md`에 문서화:

```bash
cat > custom/config/output_path.md << 'EOF'
# EnvironmentScan 출력 경로 커스텀 설정

## 수정된 output 경로
- 기본값: [원작자 기본 경로]
- 커스텀 값: /Users/kylechoi/Desktop/Ai_works/output/환경스캐닝/{날짜}_{주제}/

## 수정 위치
- 수정한 파일: [실제 수정한 파일명 기입]
- 수정한 설정: [실제 수정한 설정키 기입]
EOF
```

> ⚠️ 실제 수정한 파일이 있다면 해당 파일을 custom/config/ 아래로 복사해두기

- [ ] **Step 4: .gitignore 생성**

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
.env
.DS_Store
firebase-debug*.log
EOF
```

- [ ] **Step 5: .upstream-version 생성**

```bash
cat > .upstream-version << 'EOF'
upstream_commit: unknown
upstream_tag: latest
synced_at: 2026-04-14
note: git clone 없이 다운로드된 레포. 원작자 커밋 해시 미확인.
EOF
```

- [ ] **Step 6: GitHub 레포 생성**

```bash
gh repo create greatson79/environmentscan --public --description "EnvironmentScan AgenticWorkflow — idoforgod 기반, output 경로 커스텀"
```

- [ ] **Step 7: remote 등록**

```bash
git remote add origin https://github.com/greatson79/environmentscan.git
git remote add base https://github.com/greatson79/agenticworkflow-mirror.git
git remote add upstream https://github.com/idoforgod/<실제 EnvironmentScan 레포명>.git
```

- [ ] **Step 8: remote 확인**

```bash
git remote -v
```
Expected: `origin`, `base`, `upstream` 3개 확인

- [ ] **Step 9: 전체 파일 커밋 및 push**

```bash
git add -A
git commit -m "feat: environmentscan 초기 셋업 — custom/config, shared, .upstream-version 추가"
git push -u origin main
```

- [ ] **Step 10: dev 브랜치 생성**

```bash
git checkout -b dev
git push -u origin dev
git checkout main
```

- [ ] **Step 11: 확인**

```bash
gh repo view greatson79/environmentscan
git branch -a
```
Expected: `main`, `dev`, `remotes/origin/main`, `remotes/origin/dev` 확인

---

## Task 3: globalnews 셋업

**로컬 경로:** `/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow`  
**GitHub 레포:** `greatson79/GlobalNews-Crawling-AgenticWorkflow` (이미 존재)

> ⚠️ 이 프로젝트는 remote 오염 상태: `origin`→church-automation(잘못됨), `chatting-room`(불명), git 오브젝트 손상 가능성

**Files:**
- Create: `Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow/custom/config/output_path.md`
- Create: `Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow/shared/.gitkeep`
- Create: `Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow/.upstream-version`

- [ ] **Step 1: git 상태 전체 확인**

```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow
git status
git remote -v
git branch -a
git fsck --full 2>&1 | head -20
```

Expected: 현재 remote 3개(`origin`/`globalnews`/`chatting-room`), 브랜치 main

- [ ] **Step 2: 잘못된 remote 제거**

```bash
git remote remove origin
git remote remove chatting-room
git remote -v
```
Expected: `globalnews` 1개만 남음

- [ ] **Step 3: remote 재편성**

```bash
# globalnews(Kyle의 GitHub 레포) → origin으로 rename
git remote rename globalnews origin

# base: 허브 연결
git remote add base https://github.com/greatson79/agenticworkflow-mirror.git

# upstream: 원작자 레포 연결
git remote add upstream https://github.com/idoforgod/<실제 GlobalNews 레포명>.git

git remote -v
```
Expected: `origin`/`base`/`upstream` 3개

- [ ] **Step 4: upstream 최신 상태로 로컬 main 정렬**

```bash
git fetch upstream
git log upstream/main --oneline -5
git log main --oneline -5
```

> ⚠️ 로컬 main(3개 커밋)과 upstream/main 차이를 먼저 확인할 것.  
> 로컬에만 있는 커밋이 Kyle님 작업이라면 백업 후 진행.

```bash
git checkout main
git reset --hard upstream/main
```

- [ ] **Step 5: custom/, shared/ 디렉토리 생성**

```bash
mkdir -p custom/config
touch custom/config/.gitkeep shared/.gitkeep
```

- [ ] **Step 6: output 경로 커스텀 설정 문서화**

```bash
cat > custom/config/output_path.md << 'EOF'
# GlobalNews 출력 경로 커스텀 설정

## 수정된 output 경로
- 기본값: [원작자 기본 경로]
- 커스텀 값: /Users/kylechoi/Desktop/Ai_works/output/뉴스크롤링/{날짜}/

## 수정 위치
- 수정한 파일: [실제 수정한 파일명 기입]
- 수정한 설정: [실제 수정한 설정키 기입]
EOF
```

> ⚠️ 덮어쓰기로 수정한 파일이 있다면 해당 파일을 custom/config/ 아래로 복사해두기

- [ ] **Step 7: .upstream-version 생성**

```bash
COMMIT=$(git rev-parse upstream/main | head -c 7)
cat > .upstream-version << EOF
upstream_commit: ${COMMIT}
upstream_tag: latest
synced_at: $(date +%Y-%m-%d)
EOF
```

- [ ] **Step 8: 커밋 및 origin push**

```bash
git add custom/ shared/ .upstream-version
git commit -m "feat: globalnews remote 정리 + custom/config, shared, .upstream-version 추가"
git push -u origin main
```

- [ ] **Step 9: dev 브랜치 생성**

```bash
git checkout -b dev
git push -u origin dev
git checkout main
```

- [ ] **Step 10: 확인**

```bash
git remote -v
git branch -a
gh repo view greatson79/GlobalNews-Crawling-AgenticWorkflow
```
Expected: remote 3개, main/dev 브랜치 확인

---

## Task 4: sermon-assistant 셋업

**로컬 경로:** `/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main`  
**GitHub 레포:** `greatson79/sermon-assistant` (신규 생성)

**Files:**
- Create: `Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main/custom/.gitkeep`
- Create: `Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main/shared/.gitkeep`
- Create: `Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main/.upstream-version`
- Create: `Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main/.gitignore`

- [ ] **Step 1: 디렉토리로 이동 및 git 초기화**

```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main
git init
git checkout -b main
```

- [ ] **Step 2: 디렉토리 생성**

```bash
mkdir -p custom shared
touch custom/.gitkeep shared/.gitkeep
```

- [ ] **Step 3: .gitignore 생성**

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
.DS_Store
output/
sermon-output/
tmux-*.log
state.yaml
EOF
```

- [ ] **Step 4: .upstream-version 생성**

```bash
cat > .upstream-version << 'EOF'
upstream_commit: unknown
upstream_tag: latest
synced_at: 2026-04-14
note: git clone 없이 다운로드된 레포. 원작자 커밋 해시 미확인.
EOF
```

- [ ] **Step 5: GitHub 레포 생성 및 remote 등록**

```bash
gh repo create greatson79/sermon-assistant --public --description "Sermon Assistant AgenticWorkflow — idoforgod 기반, weekly-works 엔진"
git remote add origin https://github.com/greatson79/sermon-assistant.git
git remote add base https://github.com/greatson79/agenticworkflow-mirror.git
git remote add upstream https://github.com/idoforgod/<실제 Sermon-Assistant 레포명>.git
git remote -v
```
Expected: `origin`, `base`, `upstream` 3개

- [ ] **Step 6: 커밋 및 push**

```bash
git add -A
git commit -m "feat: sermon-assistant 초기 셋업 — custom, shared, .upstream-version 추가"
git push -u origin main
```

- [ ] **Step 7: dev 브랜치 생성**

```bash
git checkout -b dev
git push -u origin dev
git checkout main
```

- [ ] **Step 8: 확인**

```bash
git branch -a && git remote -v
gh repo view greatson79/sermon-assistant
```
Expected: main/dev 브랜치, remote 3개 확인

---

## Task 5: dissertation-simulator 셋업

**로컬 경로:** `/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Dissertation-Simulator-AgenticWorkflow-main`  
**GitHub 레포:** `greatson79/dissertation-simulator` (신규 생성)

**Files:**
- Create: `Vibe-Practice/Dissertation-Simulator-AgenticWorkflow-main/custom/.gitkeep`
- Create: `Vibe-Practice/Dissertation-Simulator-AgenticWorkflow-main/shared/.gitkeep`
- Create: `Vibe-Practice/Dissertation-Simulator-AgenticWorkflow-main/.upstream-version`
- Create: `Vibe-Practice/Dissertation-Simulator-AgenticWorkflow-main/.gitignore`

- [ ] **Step 1: 디렉토리로 이동 및 git 초기화**

```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Dissertation-Simulator-AgenticWorkflow-main
git init
git checkout -b main
```

- [ ] **Step 2: 디렉토리 생성**

```bash
mkdir -p custom shared
touch custom/.gitkeep shared/.gitkeep
```

- [ ] **Step 3: .gitignore 생성**

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
.DS_Store
thesis-output/
translations/
tmux-*.log
EOF
```

- [ ] **Step 4: .upstream-version 생성**

```bash
cat > .upstream-version << 'EOF'
upstream_commit: unknown
upstream_tag: latest
synced_at: 2026-04-14
note: git clone 없이 다운로드된 레포. 원작자 커밋 해시 미확인.
EOF
```

- [ ] **Step 5: GitHub 레포 생성 및 remote 등록**

```bash
gh repo create greatson79/dissertation-simulator --public --description "Dissertation Simulator AgenticWorkflow — idoforgod 기반"
git remote add origin https://github.com/greatson79/dissertation-simulator.git
git remote add base https://github.com/greatson79/agenticworkflow-mirror.git
git remote add upstream https://github.com/idoforgod/<실제 Dissertation-Simulator 레포명>.git
git remote -v
```
Expected: `origin`, `base`, `upstream` 3개

- [ ] **Step 6: 커밋 및 push**

```bash
git add -A
git commit -m "feat: dissertation-simulator 초기 셋업 — custom, shared, .upstream-version 추가"
git push -u origin main
```

- [ ] **Step 7: dev 브랜치 생성**

```bash
git checkout -b dev
git push -u origin dev
git checkout main
```

- [ ] **Step 8: 확인**

```bash
git branch -a && git remote -v
gh repo view greatson79/dissertation-simulator
```
Expected: main/dev 브랜치, remote 3개 확인

---

## Task 6: 전체 구조 최종 검증

- [ ] **Step 1: 허브 상태 확인**

```bash
cd /Users/kylechoi/Desktop/Ai_works/agenticworkflow-mirror
git remote -v
cat .upstream-version
```

- [ ] **Step 2: 4개 프로젝트 remote 일괄 확인**

```bash
for dir in \
  "/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/EnvironmentScan-system-main-v4-main" \
  "/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow" \
  "/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main" \
  "/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Dissertation-Simulator-AgenticWorkflow-main"
do
  echo "=== $(basename $dir) ==="
  git -C "$dir" remote -v
  git -C "$dir" branch -a
  echo ""
done
```
Expected: 각 프로젝트마다 `origin`, `base`, `upstream` + `main`, `dev` 브랜치

- [ ] **Step 3: GitHub 레포 목록 확인**

```bash
gh repo list greatson79 --limit 10
```
Expected: `agenticworkflow-mirror`, `environmentscan`, `GlobalNews-Crawling-AgenticWorkflow`, `sermon-assistant`, `dissertation-simulator` 포함

---

## Upstream 싱크 절차 (운영 참고)

원작자가 업데이트하면 아래 순서로 진행:

```bash
# Phase 1: 허브 업데이트
cd /Users/kylechoi/Desktop/Ai_works/agenticworkflow-mirror
git fetch upstream
git merge upstream/main
git push origin main

# Phase 2: 각 프로젝트에 반영 (선택적)
cd <project-dir>
git fetch upstream   # 프로젝트별 원작자 업데이트
git fetch base       # 허브 업데이트
git checkout main
git merge base/main  # 또는 upstream/main
git checkout dev
git merge main
```
