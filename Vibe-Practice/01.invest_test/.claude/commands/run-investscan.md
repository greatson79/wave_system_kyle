# /run-investscan — InvestScan Research Phase Execution

Trigger the Research Phase of InvestScan: spawn 3 Research SubAgents in parallel,
collect results, merge to `phase-research.yaml`, and update `state.yaml`.

## Execution Flow
1. Verify `.claude/state.yaml` exists and read `workflow.current_phase`
2. If `current_phase != "research"`, inform user and ask for confirmation to restart
3. Spawn 3 Research SubAgents in parallel (all English prompts — P5-A):

```python
# Orchestrator spawns these concurrently
envscan_agent = Agent(
    subagent_type="data-collector",
    prompt="""
    Perform EnvironmentScan database.json discovery for InvestScan.
    Tasks:
    1. Search paths: ~/Documents/EnvironmentScan/, ~/Desktop/Ai_works/, ~/
    2. Extract actual field names (STEEPs category, pSST score, summary fields)
    3. Determine pSST normalization scale (0-100 | 0-10 | 0-1)
    4. Write ALL findings to .claude/agent-workspace/envscan-agent.yaml
    5. Return JSON: {"found": bool, "path": str, "schema": {field_mappings}}
    Write only English to workspace files. Do not write to state.yaml directly.
    """,
    run_in_background=True
)

fred_agent = Agent(
    subagent_type="data-collector",
    prompt="""
    Check FRED API connectivity and 10 series_id availability for InvestScan.
    Tasks:
    1. Test FRED API key from Keychain (key: FRED_API_KEY)
    2. Verify these 10 series_ids are available: DFF, FEDFUNDS, UNRATE, CPIAUCSL,
       T10YIE, GS10, DTWEXBGS, VIXCLS, BAMLH0A0HYM2, CSUSHPISA
    3. Write results to .claude/agent-workspace/fred-agent.yaml
    4. Return JSON: {"fred_ready": bool, "connectivity": str, "available_series": list}
    Write only English. Do not write to state.yaml directly.
    """,
    run_in_background=True
)

gnews_agent = Agent(
    subagent_type="data-collector",
    prompt="""
    Search for GlobalNews signals.parquet file for InvestScan.
    Tasks:
    1. Search paths: ~/Documents/, ~/Desktop/Ai_works/, ~/
    2. If found: check pyarrow can parse it, extract confidence_field name
    3. Write findings to .claude/agent-workspace/gnews-agent.yaml
    4. Return JSON: {"found": bool, "path": str, "confidence_field": str}
    Write only English. Do not write to state.yaml directly.
    """,
    run_in_background=True
)
```

4. Wait for all 3 agents to complete (timeout: 5 minutes)
5. Merge results into `.claude/state/phase-research.yaml` (Research Lead)
6. Atomic write to `.claude/state.yaml`:
   - `workflow.current_phase = "planning"`
   - `workflow.current_step = 3`
   - `discovered_paths`, `discovered_schema` from merge
7. Set `runtime_mode`: "full" | "envscan_only" | "independent"

## Fallback (v3.1 — timeout or agent failure)
- Timeout 5 min → retry once → Sequential mode (spawn agents one at a time)
- Individual agent failure → use fallback data + log error to `state.yaml.errors`
- Inform user in Korean if manual intervention is required
