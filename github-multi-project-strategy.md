# 외부 코드베이스(upstream) 기반 다중 프로젝트 운영 전략

> **대상:** Claude Code 학습용 워크플로우 가이드  
> **목적:** 외부 GitHub 레포지토리(a)를 모체로, 다수의 독립 프로젝트를 안전하게 운영하는 최적 전략  
> **최종 확정일:** 2026-04-11

---

## 전체 아키텍처

```
[원작자] upstream/a  (원본 — 수정 불가)
         │
         ▼
[내 계정] my/a-mirror      ← ① Upstream 싱크 전담 + 공통 자산 허브
         │
    ┌────┴────┬─────────┐
    ▼         ▼         ▼
 my/b-proj  my/c-proj  my/d-proj   ← ② 각각 완전히 독립된 레포
```

**핵심 원칙:**
- `a-mirror`는 단 하나의 포크 — upstream과의 모든 동기화를 이 레포에서만 처리
- 각 프로젝트(b, c, d...)는 GitHub 포크가 아닌 **독립 레포**로 생성
- `core/` 코드는 절대 직접 수정하지 않음

---

## STEP 1. `a-mirror` — Upstream 허브 구축

### 1-1. GitHub에서 a를 포크 (1회만)

GitHub UI에서 `upstream/a` → `my/a-mirror` 포크 생성

### 1-2. 로컬 클론 및 upstream 등록

```bash
git clone https://github.com/내계정/a-mirror
cd a-mirror
git remote add upstream https://github.com/원작자/a
git fetch upstream
```

### 1-3. `a-mirror` 디렉토리 구조 설정

```
a-mirror/
├── core/           # upstream/a 원본 코드 (절대 수정 금지)
│   ├── engine/
│   └── utils/
├── shared/         # 모든 프로젝트 공통 자산 (이 레포에서만 관리)
│   ├── config/     #   공통 환경설정 템플릿
│   └── utils/      #   공통 헬퍼 함수·유틸리티
└── .upstream-version   # 마지막 싱크된 upstream 커밋 해시 기록
```

`.upstream-version` 파일 예시:
```
upstream_commit: a3f9c12
upstream_tag: v2.1.0
synced_at: 2026-04-11
```

---

## STEP 2. 개별 프로젝트 레포 생성

> GitHub 포크는 계정당 1개만 허용되므로, 각 프로젝트는 **독립 레포 + remote 연결** 방식으로 생성한다.

### 2-1. 새 레포 생성 및 초기 설정 (프로젝트마다 반복)

```bash
# GitHub에서 빈 레포 생성 (예: my/b-project)

# a-mirror를 클론해서 b-project 시작
git clone https://github.com/내계정/a-mirror  b-project
cd b-project

# remote 재설정
git remote rename origin base          # a-mirror를 base로
git remote add origin https://github.com/내계정/b-project

# 최초 푸시
git push -u origin main
```

### 2-2. 프로젝트 디렉토리 구조

```
b-project/
├── core/           # a-mirror/core에서 가져온 코드 (수정 금지)
│   ├── engine/
│   └── utils/
├── shared/         # a-mirror/shared에서 가져온 공통 자산 (수정 금지)
├── custom/         # b-project 고유 코드 (여기서만 개발)
│   ├── features/
│   └── overrides/  #   core 클래스 상속·오버라이드
├── config/         # 프로젝트별 설정
└── .upstream-version
```

---

## STEP 3. 브랜치 전략

```
main              ← a-mirror(base)와 동기화 유지. 직접 개발 금지.
  └── dev         ← 실제 커스텀 코드 개발 브랜치
        └── feature/xxx   ← 기능별 세부 브랜치
```

### 브랜치 운영 규칙

| 브랜치 | 역할 | 직접 커밋 |
|--------|------|----------|
| `main` | upstream 상태 유지 | ❌ 금지 |
| `dev` | 커스텀 코드 통합 | ⚠️ 머지만 |
| `feature/*` | 기능 단위 개발 | ✅ 허용 |

```bash
# 프로젝트 시작 시 브랜치 셋업
git checkout -b dev
git checkout -b feature/my-first-feature dev
```

---

## STEP 4. 코드 작성 원칙 — Core 수정 금지, 상속·임포트로 확장

`core/`의 코드를 **절대 직접 수정하지 않는다.**  
반드시 `custom/` 디렉토리에서 상속하거나 임포트해서 확장한다.

### Python 예시 (상속)
```python
# core/engine/processor.py  ← 건드리지 않음
class BaseProcessor:
    def process(self, data):
        return data

# custom/features/my_processor.py  ← 여기서만 개발
from core.engine.processor import BaseProcessor

class MyProcessor(BaseProcessor):
    def process(self, data):
        data = super().process(data)
        # b-project 고유 로직 추가
        return data
```

### Node.js 예시 (임포트 확장)
```javascript
// core/utils/logger.js  ← 건드리지 않음
// custom/overrides/logger.js  ← 여기서만 개발
const baseLogger = require('../../core/utils/logger');

module.exports = {
  ...baseLogger,
  log: (msg) => baseLogger.log(`[b-project] ${msg}`)
};
```

---

## STEP 5. Upstream 업데이트 싱크 절차

### Phase 1: `a-mirror`에서 먼저 검증

```bash
cd a-mirror

# 원작자 변경사항 확인
git fetch upstream
git log upstream/main --oneline -10   # 무엇이 바뀌었는지 확인

# a-mirror에 반영 (여기서 충돌 먼저 해결)
git merge upstream/main

# .upstream-version 업데이트
echo "upstream_commit: $(git rev-parse upstream/main | head -c 7)" > .upstream-version

git push origin main
```

### Phase 2: 각 프로젝트에 선택적 반영

```bash
cd b-project

# a-mirror 최신화 확인
git fetch base

# main 브랜치에 반영
git checkout main
git merge base/main

# dev 브랜치에 upstream 변경사항 흡수
git checkout dev
git merge main

# 충돌 해결 후 feature 브랜치 계속 개발
```

---

## 예상 문제와 해결책

### 문제 1: Merge Conflict (충돌)

**원인:** `core/`를 직접 수정했거나, `custom/`이 변경된 `core/` API에 의존하는 경우

**해결책:**
- `core/` 직접 수정 절대 금지 → 충돌 원천 차단
- `custom/`에서 API 시그니처가 바뀌었다면 `overrides/`만 수정

### 문제 2: 의존성 충돌

**원인:** 원작자가 라이브러리 버전을 올렸으나 내 코드가 구버전에 의존

**해결책:**
```bash
# a-mirror에서 먼저 의존성 테스트
cd a-mirror
pip install -r requirements.txt  # 또는 npm install
# 테스트 통과 확인 후 각 프로젝트에 반영
```

### 문제 3: 구조적 대규모 변경

**원인:** 원작자가 파일 위치·구조를 전면 개편

**해결책:**
- `a-mirror`의 `CHANGELOG` 또는 커밋 로그 먼저 분석
- `core/`를 통째로 교체한 뒤 `custom/`의 import 경로만 수정

---

## ❌ 절대 금지 — 덮어쓰기(Overwrite)

업데이트된 a를 다운로드해서 파일을 덮어쓰는 방식은 사용하지 않는다.

| 문제 | 이유 |
|------|------|
| 히스토리 단절 | Git의 변경 추적 기능 완전 포기 |
| 휴먼 에러 | 커스텀 코드가 소리 없이 삭제될 위험 |
| 롤백 불가 | 어떤 파일이 덮어씌워졌는지 파악 불가 |

**반드시 `git merge base/main`을 사용한다.**  
충돌이 발생해도 Git이 정확한 충돌 위치를 알려주므로 100배 안전하다.

---

## 전체 워크플로우 요약

| 단계 | 명령 / 작업 | 대상 레포 |
|------|------------|----------|
| Upstream 싱크 | `git fetch upstream` → `git merge` | `a-mirror` |
| 공통 자산 업데이트 | `shared/` 수정 후 push | `a-mirror` |
| 프로젝트 업데이트 | `git fetch base` → `git merge base/main` | `b-project` 등 |
| 기능 개발 | `feature/*` 브랜치에서 `custom/`만 수정 | 각 프로젝트 |
| 버전 추적 | `.upstream-version` 갱신 | 모든 레포 |

---

## 빠른 참조 — 자주 쓰는 명령어

```bash
# a-mirror: upstream 최신 상태 확인
git fetch upstream && git log upstream/main --oneline -5

# a-mirror: upstream 반영
git merge upstream/main && git push origin main

# 각 프로젝트: base(a-mirror) 반영
git fetch base && git checkout main && git merge base/main

# 현재 upstream 버전 확인
cat .upstream-version
```

---

*이 문서는 Claude와 Gemini의 상호 검토를 통해 도출한 최적안입니다.*  
*Claude Code 학습용 — 실제 구현 시 이 문서를 컨텍스트로 제공하십시오.*
