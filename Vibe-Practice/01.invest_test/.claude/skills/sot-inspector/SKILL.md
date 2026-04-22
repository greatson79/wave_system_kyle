---
name: sot-inspector
description: InvestScan SOT state inspector skill. Reads all SOT layers and produces Korean dashboard output for /check-sot command.
---

# SOT Inspector Skill

Read the full InvestScan SOT hierarchy and render a Korean status dashboard.
Output language: Korean (user-facing query result — P5 허용 채널).

## Data Sources to Read
```python
sources = {
    "global_sot": ".claude/state.yaml",
    "research_sot": ".claude/state/phase-research.yaml",
    "planning_sot": ".claude/state/phase-planning.yaml",
    "impl_sot": ".claude/state/phase-impl.yaml",
    "workspaces": list(Path(".claude/agent-workspace").glob("*.yaml")),
    "pacs_logs": list(Path("pacs-logs").glob("*.md")),
}
```

## pACS Score Extraction
```python
import re
from pathlib import Path

def get_pacs_score(step: int) -> tuple[int | None, str | None]:
    """Extract pACS score and grade from pacs-logs file."""
    log_path = Path(f"pacs-logs/step-{step}-translation-pacs.md")
    if not log_path.exists():
        return None, None
    content = log_path.read_text()
    m = re.search(r"Translation\s+pACS\s*=\s*(\d+)\s*→\s*(\w+)", content)
    if m:
        return int(m.group(1)), m.group(2)
    return None, None
```

## Status Symbol Mapping
```python
def status_symbol(status: str, pacs: int | None = None) -> str:
    if pacs is not None:
        if pacs >= 70: return "✓"
        if pacs >= 50: return "⚠"
        return "✗"
    symbols = {
        "passing": "✓", "completed": "✓", "done": "✓",
        "failing": "✗", "failed": "✗",
        "pending": "○", "idle": "○",
        "running": "⟳", "translating": "⟳",
    }
    return symbols.get(status, "○")
```

## Dashboard Render (Korean output)
```
InvestScan 상태 — {datetime}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase: {phase} | Step: {step}/15 | Mode: {runtime_mode}
언어 정책: English-First (P5) | HITL: H1=[✓/✗] H2=[✓/✗] H3=[✓/✗]

TDD 상태:
  P1 Critical (95%+):
    [{sym}] compliance_filter
    [{sym}] synthesize_macro
    [{sym}] steeps_classifier
    [{sym}] stock_selector
  핵심 파이프라인 (90%+):
    [{sym}] normalizers
    [{sym}] intelligence_engine
    [{sym}] report_generator
    [{sym}] weekly_orchestrator
    [{sym}] validate_report_quality
    [{sym}] citation_validator
  표준 (85%+):
    [{sym}] config / schema / dedup / signal_bridge / ...

번역 상태:
  [{sym}] Step 2  (schema-mapping.ko.md)           pACS={N/--}
  [{sym}] Step 4  (completion-definition.ko.md)    pACS={N/--}
  [{sym}] Step 5  (blueprint.ko.md)                pACS={N/--}
  [{sym}] Step 11 (narrative_{date}.ko.json)       pACS={N/--}
  [{sym}] Step 12 (weekly-report-{date}.ko.md)     pACS={N/--} Fd={N/--}
  [{sym}] Step 15 (watchlist-{date}.ko.md)         pACS={N/--}

포트폴리오: {보유 종목 수}개 | 마지막 갱신: {date}
라이브러리 가용률: FDR={rate/--} | pykrx={rate/--} | dart-fss={rate/--}
오류: {len(state.errors)}개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
범례: ✓=통과 ✗=실패 ⚠=경고(YELLOW) ○=대기/미실행 ⟳=진행중 --=데이터없음
```
