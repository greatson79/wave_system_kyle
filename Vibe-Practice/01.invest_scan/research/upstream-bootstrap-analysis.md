# 업스트림 시스템 비코더 부트스트래핑 심층 분석

**분석 일자**: 2026-03-28
**대상 시스템**: EnvironmentScan v3.2.0 + GlobalNews Crawling & Analysis System
**목적**: InvestScan workflow.md 설계를 위한 업스트림 의존성 완전 이해

---

## 1. EnvScan 설치·실행 분석

### 1.1 설치 단계 (실제 명령어)

EnvScan은 **Python 스크립트 기반 Claude Code 에이전트 시스템**이다. 별도의 pip install 과정이 없다. 핵심 실행 방법은 다음과 같다.

**실제 실행 명령 (Claude Code CLI에서):**
```bash
# Claude Code가 열린 상태에서 — EnvironmentScan 디렉토리 기준
/env-scan:run          # 전체 4개 워크플로우 실행 (WF1+WF2+WF3+WF4+통합)
/env-scan:run-naver    # WF3 단독 실행
/env-scan:run-arxiv    # WF2 단독 실행
/env-scan:status       # 현재 진행 상태 확인
/env-scan:approve      # 최종 리포트 승인
```

**의존성 설치 (Python 스크립트가 사용되는 경우):**
```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/EnvironmentScan-system-main-v4-main
pip install -r requirements.txt   # node_modules + package.json(docx) 이미 설치됨
```

> 현재 `requirements.txt` 가 루트에 있음 (내용 확인 필요). `node_modules/docx` 패키지는 이미 설치되어 있음 (DOCX 리포트 생성용).

**설정 파일 구성:**
```
env-scanning/config/
├── sources.yaml              # WF1 소스 (Google Patents는 enabled: true, SERPAPI 선택적)
├── sources-arxiv.yaml        # WF2 arXiv (무료, API 키 불필요)
├── sources-naver.yaml        # WF3 Naver News (무료, 크롤링)
├── sources-multiglobal-news.yaml  # WF4 뉴스 (43개 사이트)
├── domains.yaml              # STEEPs 키워드
└── workflow-registry.yaml    # SOT
```

### 1.2 비코더 장벽 (어려운 단계)

| 장벽 | 난이도 | 설명 |
|------|--------|------|
| SERPAPI_KEY 발급 | 중간 | Google Scholar 검색용. WF1에서만 필요. 없으면 해당 소스 disabled로 설정 가능 |
| KIPRIS_API_KEY 발급 | 어려움 | 한국 특허 검색. 정부 API 등록 필요. WF1 옵션 소스 |
| 환경변수 설정 | 중간 | `export SERPAPI_KEY="..."` 를 터미널에 입력해야 함 |
| domains.yaml 키워드 조정 | 쉬움 | YAML 파일 편집 — 비코더도 가능 |
| `/env-scan:run` 실행 | 없음 | Claude Code CLI에서 슬래시 명령어 입력만 하면 됨 |

**중요 발견**: EnvScan은 이미 이 MacBook에서 **실제 실행된 적 있음**. 증거:
- `env-scanning/wf1-general/raw/`: `scan-2026-03-09.json`까지 존재 (최신 2026-03-09)
- `env-scanning/wf3-naver/reports/`: `report-statistics-2026-03-20.json`까지 존재 (최신 2026-03-20)
- `output/` 디렉토리에 `scan-report-2026-03-19.html`, `scan-report-2026-03-20.html` 존재
- `integrated/reports/`: `report-statistics-2026-03-12.json`까지 존재

**결론**: EnvScan은 이미 정상 운영 중이며 지속적으로 실행되고 있다.

### 1.3 Claude Code 자동화 가능성

**자동화 가능 범위: 90% (매우 높음)**

| 단계 | 자동화 가능 여부 | 방법 |
|------|----------------|------|
| 실행 트리거 | ✅ 완전 자동 | `claude --dangerously-skip-permissions -p "/env-scan:run"` |
| API 키 환경변수 설정 | ⚠️ 최초 1회 수동 | Claude Code가 `.zshrc` 편집 가능 |
| 결과 읽기 | ✅ 완전 자동 | Bash tool로 파일 읽기 |
| Human-in-the-Loop (9개 체크포인트) | ❌ 수동 필요 | Phase 2.5 분석 검토 + Phase 3.4 리포트 승인 |
| `domains.yaml` 키워드 조정 | ✅ 자동 가능 | Claude Code가 YAML 편집 |

**Autopilot Mode 존재**: README에 명시된 Autopilot 모드 사용 시 HITL 체크포인트도 자동 승인 가능. 단, 품질 리뷰 없이 진행되는 트레이드오프 존재.

---

## 2. GlobalNews 설치·실행 분석

### 2.1 설치 단계

```bash
# Step 1: 디렉토리 이동
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow

# Step 2: 가상환경 생성 (필수 — 44+ 패키지, Python 3.12 필요)
python3 -m venv .venv
source .venv/bin/activate

# Step 3: 의존성 설치 (44+ 패키지, 약 2-5GB 디스크 사용)
pip install -r requirements.txt

# Step 4: NLP 모델 다운로드 (추가 약 500MB-1GB)
python3 -m spacy download en_core_web_sm
playwright install chromium

# Step 5: 사전 검증
python3 scripts/preflight_check.py --project-dir . --mode full

# Step 6: 실행
python3 main.py --mode crawl --date 2026-03-28
python3 main.py --mode full --date 2026-03-28
```

**주요 CLI 옵션:**
```bash
python3 main.py --mode full --date YYYY-MM-DD    # 크롤링 + 8단계 분석
python3 main.py --mode crawl --date YYYY-MM-DD   # 크롤링만
python3 main.py --mode analyze --all-stages      # 분석만 (기존 데이터 필요)
python3 main.py --mode status                    # 상태 확인
python3 main.py --mode full --dry-run            # 설정 검증 (네트워크 없음)
```

### 2.2 비코더 장벽

| 장벽 | 난이도 | 설명 |
|------|--------|------|
| 가상환경 생성 | 중간 | `python3 -m venv .venv` + `source .venv/bin/activate` 2줄 명령어 |
| 의존성 설치 시간 | 중간 | 44+ 패키지 + ML 모델 다운로드 30분-1시간 예상 |
| spaCy 모델 다운로드 | 쉬움 | 1줄 명령어 |
| playwright 브라우저 설치 | 쉬움 | 1줄 명령어 |
| Python 버전 확인 | 없음 | Python 3.12.2 이미 설치됨 (시스템에서 확인) |
| API 키 | 없음 | **API 키 불필요** (C1 하드 제약: Claude API = $0, 전체 로컬 실행) |
| 환경변수 설정 | 없음 | 불필요 |

**핵심 발견**: GlobalNews는 외부 API 키가 전혀 없다. 100% 로컬 실행.

### 2.3 Claude Code 자동화 가능성

**자동화 가능 범위: 95% (거의 완전 자동)**

Claude Code가 Bash tool을 통해 다음을 모두 실행할 수 있다:

```bash
# Claude Code가 실행하는 전체 시퀀스
cd /path/to/GlobalNews && source .venv/bin/activate
python3 main.py --mode full --date $(date +%Y-%m-%d)
# 결과 확인
python3 -c "import json; d=json.load(open('data/output/run_metadata.json')); print(d)"
ls data/output/$(date +%Y-%m-%d)/
```

**GlobalNews에는 Claude Commands 없음**: `.claude/commands/run.md` 등이 있지만 이는 Claude Code 워크플로우 빌드용이다. 운영 실행은 `python3 main.py`로 직접 호출한다.

**Human-in-the-Loop 없음**: InvestScan의 구체적 분석 단계와 달리, GlobalNews는 완전 자동 파이프라인이다. 실행 후 결과(`data/output/YYYY-MM-DD/`)만 확인하면 된다.

### 2.4 현재 설치 상태 (실행된 적 있는가?)

**GlobalNews는 이 MacBook에서 실제 실행됨. 증거:**

| 증거 | 내용 |
|------|------|
| `data/raw/2026-03-16/all_articles.jsonl` | 5.5MB, 크롤링 원시 데이터 실존 |
| `data/raw/2026-03-18/all_articles.jsonl` | 1.9MB, 402건 기사 수집 |
| `data/raw/2026-03-18/crawl_report.json` | 10개 사이트 100% 성공률, 1,218초 실행 |
| `data/output/run_metadata.json` | 2026-03-25 전체 파이프라인 실행 기록 (exit_code: 0) |
| `data/dedup.sqlite` + `data/dedup.sqlite-shm` + `data/dedup.sqlite-wal` | SQLite 중복 제거 DB 실존 |
| `data/logs/daily/crawl-2026-03-16.log` | 실행 로그 존재 |

**그러나**: `data/output/`에 날짜별 Parquet 파일 없음. 이유:
- `run_metadata.json`의 `elapsed_seconds: 0.1` → 2026-03-25 실행은 즉시 종료 (dry-run 또는 에러)
- `data/output/` 하위에 날짜별 디렉토리 없음 (2026-03-16, 2026-03-18, 2026-03-25 날짜가 raw에만 존재)
- **가상환경 없음**: `.venv` 디렉토리가 없으므로 분석 단계(ML 모델 필요)는 실행 불가
- 크롤링(raw 단계)은 성공했으나 분석 파이프라인(PyTorch, spaCy, BERTopic 필요)은 미설치로 실행 안 됨

**결론**: GlobalNews 크롤링 모듈은 정상 실행됨 (pip 전역 설치 또는 시스템 Python으로). 8단계 NLP 분석 파이프라인은 ML 패키지(torch, spaCy, sentence-transformers 등) 미설치로 미실행.

---

## 3. 비코더 부트스트래핑 전략

### 3.1 권장 접근: Claude Code 자동 설치 가능 vs 수동 필요 판단

```
┌─────────────────────────────────────────────────────┐
│           부트스트래핑 단계 분류                      │
├─────────────────────┬───────────────────────────────┤
│ Claude Code 자동     │ 수동 필요 (1회만)               │
├─────────────────────┼───────────────────────────────┤
│ EnvScan:            │ EnvScan:                        │
│ ✅ /env-scan:run    │ ⚠️ SERPAPI_KEY 발급 (선택)      │
│ ✅ 설정 파일 편집   │ ⚠️ KIPRIS_API_KEY 발급 (선택)   │
│ ✅ 결과 파일 읽기   │                                │
│                     │                                │
│ GlobalNews:         │ GlobalNews:                    │
│ ✅ 가상환경 생성    │ ⚠️ 없음 (API 키 불필요)         │
│ ✅ pip install      │                                │
│ ✅ spaCy 모델 다운  │                                │
│ ✅ playwright 설치  │                                │
│ ✅ python3 main.py  │                                │
│ ✅ 결과 파일 읽기   │                                │
└─────────────────────┴───────────────────────────────┘
```

**최우선 권고**: InvestScan workflow.md에서 Step 0(초기화 단계)를 만들어 Claude Code가 GlobalNews 의존성을 자동 설치하도록 한다.

```bash
# workflow.md Step 0에 포함될 Claude Code 자동 실행 명령
cd /path/to/GlobalNews && python3 -m venv .venv
source .venv/bin/activate && pip install -r requirements.txt
python3 -m spacy download en_core_web_sm && playwright install chromium
python3 main.py --mode full --dry-run   # 설치 검증
```

### 3.2 workflow.md에서 업스트림 초기화 처리 방법

**권장 구조 (InvestScan workflow.md):**

```markdown
## Phase 0: Upstream Systems Bootstrap (최초 1회만)

### Step 0.1: GlobalNews 환경 검증
- Bash tool: python3 -c "import pyarrow, torch, spacy" → 성공/실패 확인
- 실패 시 → Step 0.2로 이동
- 성공 시 → Step 0.3으로 건너뜀

### Step 0.2: GlobalNews 의존성 자동 설치 (Claude Code 실행)
- Bash tool: cd GlobalNews && python3 -m venv .venv
- Bash tool: .venv/bin/pip install -r requirements.txt
- Bash tool: .venv/bin/python -m spacy download en_core_web_sm
- Bash tool: playwright install chromium

### Step 0.3: EnvScan 상태 확인
- Bash tool: ls EnvironmentScan/env-scanning/wf1-general/raw/ | tail -3
- 최신 실행일 확인 → 오늘 날짜면 캐시 사용, 아니면 실행

## Phase 1: Data Collection (매일 실행)

### Step 1.1: GlobalNews 크롤링 실행
- Bash tool: cd GlobalNews && source .venv/bin/activate
  && python3 main.py --mode crawl --date {today}
- 출력: data/raw/{today}/all_articles.jsonl
- 실패 조건: exit_code != 0 → 사용자 알림

### Step 1.2: GlobalNews 분석 파이프라인 실행
- Bash tool: python3 main.py --mode analyze --all-stages
- 출력: data/output/{today}/analysis.parquet
- 예상 소요: 30-60분

### Step 1.3: EnvScan 실행
- Claude Code CLI: /env-scan:run
- 출력: integrated/reports/daily/{today}/
- 예상 소요: 2-4시간 (HITL 포함)
```

### 3.3 PRD.md "Day 0 설치" 섹션에 반드시 포함될 내용

**필수 포함 항목:**

1. **Python 버전 확인**: 현재 Python 3.12.2 설치됨 → GlobalNews 호환 (3.12 필요)
2. **GlobalNews 가상환경**: `.venv` 없음 → Day 0에 생성 필수
3. **ML 모델 디스크 공간**: 최소 5GB 여유 공간 필요 (requirements.txt 명시)
4. **첫 실행 예상 시간**: 의존성 설치 30-60분 + 첫 크롤링 20-30분 + 첫 분석 30-60분
5. **API 키**: GlobalNews 없음. EnvScan SERPAPI 선택 (없으면 Google Scholar만 disabled)
6. **EnvScan 상태**: 이미 운영 중. Day 0에서는 확인만 필요
7. **GlobalNews 크롤링 검증**: `data/raw/2026-03-18/crawl_report.json` 으로 크롤링 자체는 검증됨

---

## 4. 통합 실행 오케스트레이션 필요 사항

### 4.1 두 시스템 호출 방법

**두 시스템의 실행 인터페이스:**

| 시스템 | 실행 방법 | 출력 위치 | 소요 시간 |
|--------|---------|---------|---------|
| EnvScan | `claude --dangerously-skip-permissions -p "/env-scan:run"` 또는 Claude Code 내 슬래시 명령 | `env-scanning/integrated/reports/daily/` + `output/` | 2-4시간 |
| GlobalNews | `python3 main.py --mode full --date {date}` (venv 활성화 후) | `data/output/{date}/analysis.parquet` | 20-40분 (크롤링만) / 60-90분 (전체) |

**InvestScan workflow.md에서 호출 패턴:**
```markdown
## Step A: GlobalNews 실행 (Python 직접 호출)
Bash tool:
  cd {GLOBALNEWS_PATH}
  source .venv/bin/activate
  python3 main.py --mode full --date {today}

## Step B: EnvScan 실행 (Claude Code 슬래시 명령)
NOTE: Claude Code 세션 변경 필요 (다른 프로젝트 디렉토리)
  cd {ENVSCAN_PATH} && claude code → /env-scan:run
  OR: SubAgent 방식으로 별도 Claude Code 인스턴스 실행
```

**중요한 아키텍처 제약**: EnvScan은 Claude Code 에이전트 시스템이므로, InvestScan의 Claude Code 세션에서 직접 호출이 불가능하다. 두 가지 해결책:
1. **순차 실행**: EnvScan → GlobalNews → InvestScan을 별도 세션에서 순서대로 실행
2. **산출물 의존**: InvestScan workflow.md에서 두 시스템의 출력 파일을 읽는 방식으로 통합 (이미 실행된 결과 활용)

### 4.2 두 시스템은 독립적으로 실행 가능한가?

**완전히 독립적이다.** 두 시스템 간 직접 데이터 의존성 없음.

| 항목 | EnvScan | GlobalNews |
|------|---------|------------|
| 필요 입력 | 인터넷 연결 | 인터넷 연결 |
| 서로 의존 | 없음 | 없음 |
| InvestScan에서 읽는 파일 | `env-scanning/integrated/reports/daily/{date}-integrated*.md` | `data/output/{date}/analysis.parquet`, `signals.parquet` |

### 4.3 실패 시 사용자 알림 방법

**GlobalNews 실패 감지:**
```python
# run_metadata.json 확인
import json
meta = json.load(open('data/output/run_metadata.json'))
if meta['exit_code'] != 0:
    print(f"ERROR: GlobalNews failed with exit_code={meta['exit_code']}")
    # InvestScan이 사용자에게 알림 메시지 출력
```

**EnvScan 실패 감지:**
```bash
# workflow-status.json 확인
cat env-scanning/logs/workflow-status.json
# 또는 reports 디렉토리의 오늘 날짜 파일 존재 확인
ls env-scanning/wf1-general/reports/ | grep $(date +%Y-%m-%d)
```

**권장 실패 처리 전략 (InvestScan workflow.md에서):**
1. GlobalNews 실패 → 마지막 성공 날짜 데이터로 fallback 실행 (3일 이내)
2. EnvScan 미실행 → "EnvScan 데이터 없음, InvestScan을 EnvScan 실행 후 재시작하세요" 사용자 메시지
3. 두 시스템 모두 실패 → InvestScan 실행 중단, 사용자 알림

---

## 5. PRD.md 반영 권고

### 5.1 즉시 반영 필요 (Critical)

**시스템 상태 정정:**
- GlobalNews: 크롤링은 운영 중, **NLP 분석 파이프라인은 미설치** (venv + ML 패키지 필요)
- EnvScan: **완전 운영 중** (최신 실행 2026-03-20)

**Day 0 설치 항목 (GlobalNews만):**
```
1. cd GlobalNews && python3 -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt   ← 30-60분, 2-5GB
4. python3 -m spacy download en_core_web_sm
5. playwright install chromium
6. python3 main.py --mode full --dry-run  ← 검증
```

### 5.2 아키텍처 결정 (InvestScan 설계에 영향)

**결정 1: 데이터 접근 방식**
- GlobalNews 출력: `data/output/{date}/analysis.parquet` (Parquet 직접 읽기)
- EnvScan 출력: `env-scanning/integrated/reports/daily/` (Markdown 파일 읽기)
- InvestScan은 두 파일을 읽어 투자 분석 로직 적용

**결정 2: 실행 순서 권고**
```
[매일 실행 순서]
06:00 - GlobalNews 전체 파이프라인 (1시간)
07:00 - EnvScan 전체 실행 (2-4시간, HITL 포함)
11:00 - InvestScan 데이터 수집 단계 시작
```

**결정 3: InvestScan의 GlobalNews 통합 쿼리**
```python
# InvestScan에서 GlobalNews 데이터 읽기 예시
import pandas as pd
df = pd.read_parquet(f'../GlobalNews.../data/output/{today}/signals.parquet')
# 5-Layer 신호 중 L4(Long-term, 6개월+) / L5(Singularity) 필터링 → 투자 관련성
signals = df[df['signal_layer'].isin(['L4', 'L5'])]
```

**결정 4: EnvScan HITL 체크포인트 처리**
- InvestScan workflow.md에서 EnvScan HITL를 명시적으로 표시
- "EnvScan Phase 2.5 분석 검토 완료 후 InvestScan Step N 진행" 방식으로 의존성 명시

### 5.3 리스크 항목

| 리스크 | 확률 | 대응 |
|--------|------|------|
| GlobalNews ML 설치 실패 (호환성) | 중간 | Python 3.12 확인됨, M5 Max ARM64 호환 패키지 대부분 지원 |
| GlobalNews 크롤링 실패 (사이트 차단) | 낮음 | Never-Abandon 루프 내장, 4-Level 90회 재시도 |
| EnvScan HITL 체크포인트 지연 | 높음 | 사용자가 하루 2회(Phase 2.5, Phase 3.4) 검토 필요 |
| GlobalNews 분석 OOM | 낮음 | M5 Max 64GB RAM으로 충분 (시스템 명세: M2 Pro 16GB에서도 동작) |
| 두 시스템 동시 실행 충돌 | 없음 | 독립적, 충돌 없음 |

---

## 요약 (최종 판단)

| 항목 | 결론 |
|------|------|
| EnvScan 설치 완료 여부 | ✅ 완전 설치 및 운영 중 |
| EnvScan Claude Code 자동화 가능성 | 90% (HITL 체크포인트 제외) |
| GlobalNews 크롤링 상태 | ✅ 운영 중 (10개 사이트 성공) |
| GlobalNews 분석 파이프라인 상태 | ❌ ML 패키지 미설치 (Day 0 필요) |
| GlobalNews Claude Code 자동 설치 | ✅ 완전 자동화 가능 |
| 두 시스템 상호 의존 | 없음 (완전 독립) |
| API 키 필요 여부 | EnvScan: SERPAPI 선택적 / GlobalNews: 없음 |
| InvestScan 통합 방식 | 파일 기반 (Parquet + Markdown 읽기) |
