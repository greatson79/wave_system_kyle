---
description: "InvestScan 제품 실행 모드 — 스마트 라우터. '시작', 'start', '워크플로우를 시작하자' 등 시작 명령 시 자동 진입."
---

# InvestScan 제품 실행 모드 (Smart Router)

## 역할

이 커맨드는 **InvestScan 제품 실행(사용) 모드의 단일 진입점**이다.
빌드(Infrastructure Build)는 완료되었다. 이 모드는 **완성된 시스템을 실제로 사용**하기 위한 것이다.

> ⚠️ ABSOLUTE RULE: 이 커맨드가 실행되는 동안, 어떠한 경우에도
> "Infrastructure Build 재실행" 옵션을 사용자에게 제시하지 않는다.
> Infrastructure Build는 이미 완료된 단계이며, 제품 실행 모드와 분리된다.

---

## Step 1 — 시스템 상태 자동 진단

아래 Python 스크립트를 실행하여 현재 시스템 상태를 읽는다:

```python
import yaml, glob, os
from pathlib import Path
from datetime import date, datetime, timedelta

def read_sot():
    sot_path = Path(".claude/state.yaml")
    if not sot_path.exists():
        return None
    with open(sot_path) as f:
        return yaml.safe_load(f)

def get_status_badge(condition):
    return "✅" if condition else "⚠️"

sot = read_sot()
if sot is None:
    print("⚠️  state.yaml 없음 — 초기화 필요 (/install 실행)")
    exit(1)

# Milestone status
m05_ready = sot.get("packages", {}).get("m05_ready", False)
m1_gates  = sot.get("milestones", {}).get("m1", {})
m1_ready  = all(m1_gates.values()) if m1_gates else False

# Runtime mode
wf = sot.get("workflow", {})
runtime_mode = wf.get("runtime_mode", "unknown")
hitl2_choice = sot.get("hitl_2", {}).get("choice", "not_set")

# Latest report
reports = sorted(r for r in glob.glob("output/reports/weekly-report-*.md") if not r.endswith(".ko.md"))
latest_report = os.path.basename(reports[-1]).replace("weekly-report-", "").replace(".md", "") if reports else "없음"

# API key status
hitl1 = sot.get("hitl_1", {})
fred_ready     = hitl1.get("fred_api_key_registered", False)
dart_ready     = hitl1.get("dart_api_key_registered", False)
telegram_ready = hitl1.get("telegram_bot_token_registered", False)

# Last run time
last_run_file = Path("logs/last_successful_run.txt")
if last_run_file.exists():
    raw = last_run_file.read_text().strip()
    try:
        last_run_dt = datetime.fromisoformat(raw)
        delta = datetime.now() - last_run_dt
        if delta.total_seconds() < 3600:
            ago = f"{int(delta.total_seconds()/60)}분 전"
        elif delta.total_seconds() < 86400:
            ago = f"{int(delta.total_seconds()/3600)}시간 전"
        else:
            ago = f"{delta.days}일 전"
        last_run_str = f"{last_run_dt.strftime('%Y-%m-%d %H:%M')} ({ago})"
    except Exception:
        last_run_str = raw
else:
    last_run_str = "기록 없음"

# Next scheduled run (every Sunday 20:00 via launchd)
today = date.today()
days_ahead = (6 - today.weekday()) % 7
if days_ahead == 0 and datetime.now().hour >= 20:
    days_ahead = 7
next_sunday = today + timedelta(days=days_ahead)
if days_ahead == 0:
    next_run_str = f"오늘 20:00 (D-0)"
else:
    next_run_str = f"{next_sunday} 20:00 (D-{days_ahead})"

mode_label = {
    "full":           "전체 파이프라인 (FRED + EnvScan + DART)",
    "envscan_only":   "EnvScan 전용 (FRED fixture 사용)",
    "independent":    "독립 모드 (fixture 전용, API 없음)",
}.get(hitl2_choice, hitl2_choice)

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀  InvestScan — 제품 실행 모드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  시스템 상태
  ├─ M0.5 마일스톤  {get_status_badge(m05_ready)} {'PASS' if m05_ready else 'FAIL — /install 실행 필요'}
  ├─ M1 마일스톤    {get_status_badge(m1_ready)} {'PASS' if m1_ready else 'FAIL — run_m1.py --dry-run 실행 필요'}
  ├─ 런타임 모드    📡 {mode_label}
  ├─ 마지막 리포트  📅 {latest_report}
  ├─ 마지막 실행    🕐 {last_run_str}
  ├─ 다음 자동 실행  ⏰ {next_run_str}
  └─ API 연결 상태  FRED {get_status_badge(fred_ready)} | DART {get_status_badge(dart_ready)} | Telegram {get_status_badge(telegram_ready)}
""")
```

---

## Step 2 — 실행 모드 선택 UI 표시

상태 진단 결과를 보여준 후, 아래 형식으로 **제품 실행 모드 선택 메뉴**를 한국어로 출력한다.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  실행 모드를 선택하세요
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [1]  📊  주간 리포트 생성  ────────────────── 권장
       FRED 데이터 수집 → 매크로 분석 → 종목 선택
       → 내러티브 생성 → 번역 → Telegram 발송
       실행: python3 -m investscan.weekly_orchestrator --mode full-auto

  [2]  🧪  Dry-Run 시뮬레이션  ──────────────── 테스트
       실제 API 없이 fixture 데이터로 전체 파이프라인 검증
       외부 비용 없음. 언제든 안전하게 실행 가능.
       실행: python3 -m investscan.weekly_orchestrator --mode dry-run

  [3]  📡  데이터 수집만  ────────────────────── 데이터
       FRED + EnvScan 데이터 수집만. 내러티브 생성 없음.
       실행: python3 -m investscan.weekly_orchestrator --mode data-only

  [4]  🔍  특정 종목 단독 분석  ──────────────── 개별
       종목 코드와 이름 입력 → 해당 종목만 리포트 생성
       실행: python3 -m investscan.weekly_orchestrator --stock [코드] --name [이름]

  [5]  ⚡  파이프라인 게이트 전체 검증  ────── 진단
       16개 Done Gate(M0.5 + M1)를 dry-run으로 전체 재검증
       실행: python3 run_m05.py --dry-run && python3 run_m1.py --dry-run

  [6]  📋  현재 상태 확인  ──────────────────── 조회
       SOT state.yaml, 에러 로그, 마일스톤 게이트 현황
       실행: /check-sot

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  번호, 이름, 또는 자연어로 선택하세요.
  예) "1번 실행해줘" / "dry-run 해보자" / "3번" / "상태 확인"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 3 — 선택 처리 라우팅

사용자 입력을 파싱하여 아래 매핑에 따라 실행한다.

| 입력 패턴 | 실행 대상 |
|-----------|-----------|
| `1`, `주간`, `리포트`, `full`, `전체` | `weekly_orchestrator --mode full-auto` |
| `2`, `dry`, `드라이런`, `시뮬`, `테스트` | `weekly_orchestrator --mode dry-run` |
| `3`, `데이터`, `수집`, `data` | `weekly_orchestrator --mode data-only` |
| `4`, `종목`, `개별`, `stock` + 코드/이름 | `weekly_orchestrator --stock CODE --name NAME` |
| `5`, `게이트`, `검증`, `gate`, `진단` | `run_m05.py --dry-run && run_m1.py --dry-run` |
| `6`, `상태`, `확인`, `sot`, `check` | `/check-sot` 실행 |

### 선택 [1] 주간 리포트 생성 실행 흐름

```
1. state.yaml에서 runtime_mode 확인
   - envscan_only → EnvScan fixture + FRED fixture 사용
   - full → 실제 FRED API + DART API 사용 (API 키 필요)
   - independent → 전체 fixture 사용

2. python3 -m investscan.weekly_orchestrator --mode full-auto 실행

3. 완료 후 — 실행 결과 요약 자동 출력:
   python3 -m investscan.run_summary
   → 종목 / 신호 방향 / YoY 실적 / pACS 품질 점수 3줄 요약

4. 리포트 미리보기 (선택):
   python3 -m investscan.preview_report
   → Executive Summary + Financial Snapshot + Macro 인라인 출력

5. HITL-3 승인 안내:
   python3 -m investscan.approve_hitl
   → 3줄 요약 + "Telegram 발송하시겠습니까? [Y/N]" 프롬프트
```

### 선택 [4] 특정 종목 분석 흐름

```
1. 사용자에게 질문:
   "분석할 종목 코드를 입력하세요. (예: 005930):"
   "종목 이름을 입력하세요. (예: 삼성전자):"
   "카테고리를 선택하세요. [A] 재무 실적 기반 / [B] 테마 기반:"

2. 입력 검증:
   - 종목 코드: 6자리 숫자 (KRX 코드)
   - 이름: 비어있지 않음
   - 카테고리: A 또는 B

3. 실행:
   python3 -m investscan.weekly_orchestrator \
     --mode dry-run \
     --stock [코드] \
     --name [이름] \
     --category [A|B]
```

---

## PROHIBITED OPTIONS (절대 금지)

이 커맨드가 실행되는 동안 다음 옵션은 **절대로 사용자에게 제시하지 않는다**:

```
❌  Infrastructure Build 재실행
❌  Phase B 재실행
❌  빌드 초기화
❌  워크플로우 빌드 시작
❌  시스템 재구축
```

이 항목들은 개발/빌드 단계 전용이다. 제품 실행 모드에서는 존재하지 않는다.
만약 사용자가 "빌드를 다시 하고 싶다"고 요청하면, 다음과 같이 안내한다:

```
빌드(Infrastructure Build)는 이미 완료되었습니다.
제품 실행 모드에서는 빌드 재실행을 지원하지 않습니다.
빌드 관련 작업이 필요하다면, 개발자 모드에서 직접 실행하세요:
  - python3 run_m05.py --dry-run  (M0.5 게이트 재검증)
  - python3 run_m1.py --dry-run   (M1 게이트 재검증)
```
