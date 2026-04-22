---
name: data-collector
description: InvestScan data collection skill. Use when fetching data from FRED API, EnvironmentScan database, GlobalNews signals, or Korea market data (pykrx/FDR).
---

# Data Collector Skill

Collect and normalize data from InvestScan data sources. English-First (P5-A).

## Protocol

### Step 1: Keychain Check (English commands)
```bash
# Load API keys from macOS Keychain — do NOT hardcode
security find-generic-password -a "$USER" -s "FRED_API_KEY" -w
security find-generic-password -a "$USER" -s "DART_API_KEY" -w
security find-generic-password -a "$USER" -s "TELEGRAM_BOT_TOKEN" -w
```

### Step 2: Fetch Data (timeout + retry — English logs)
```python
import requests, time

def fetch_with_retry(url: str, params: dict, timeout: int = 30, max_retries: int = 3) -> dict:
    """Fetch data with exponential backoff retry. Returns empty dict on all failures."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == max_retries - 1:
                # Log error in English
                print(f"[ERROR] Fetch failed after {max_retries} attempts: {e}")
                return {}
            time.sleep(2 ** attempt)  # exponential backoff
    return {}
```

### Step 3: Normalize to UnifiedSignal (English field names)
```python
# Read discovered_schema from state.yaml — use actual field names, not assumed ones
state = yaml.safe_load(Path(".claude/state.yaml").read_text())
schema = state.get("discovered_schema", {}).get("envscan_wf1", {})
steeps_field = schema.get("steeps_field", "steeps_category")  # fallback to common name
psst_field = schema.get("psst_field", "pSST")

# Normalize to UnifiedSignal (all English keys)
unified_signal = {
    "source": "envscan",          # data source identifier
    "steeps_category": row[steeps_field],
    "psst_score": normalize_psst(row[psst_field], schema.get("score_scale", "0-100")),
    "summary": row.get(schema.get("summary_field", "summary"), ""),
    "collected_at": datetime.now().isoformat(),
}
```

### Step 4: Fallback Hierarchy (per source)
```
FRED:       live API → 7-day cache → minimum 5 series → runtime_mode = "independent"
DART:       DART API → pykrx → FDR → None (log data_freshness_note)
EnvScan:    discovered path → not found → {"found": false} → Orchestrator sets mode
GlobalNews: discovered path → not found → {"found": false} → graceful skip
```

### Step 5: Write Workspace (all English)
```python
result = {
    "agent_id": "{assigned-id}",
    "status": "completed",   # completed | failed
    "data": {...},           # normalized data — all English keys
    "error": None,
    "collected_at": datetime.now().isoformat(),
}
Path(".claude/agent-workspace/{id}.yaml").write_text(yaml.dump(result))
```

## Library Availability Tracking (v3.6 I-6)
After each FDR/pykrx/dart-fss call, update `state.yaml.library_availability`:
```python
# Via Orchestrator (not directly — report to workspace first)
result["library_stats"] = {
    "fdr_success": bool,
    "pykrx_success": bool,
    "dart_fss_success": bool,
}
```

## SOT Protection (D1)
Write ONLY to assigned `.claude/agent-workspace/[id].yaml`.
NEVER write to `state.yaml` or `phase-*.yaml`.
