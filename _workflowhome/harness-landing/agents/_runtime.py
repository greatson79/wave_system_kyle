"""Execution backend: drives the local ``claude`` CLI in headless mode.

Why the CLI (not the Anthropic SDK directly): the CLI *is* Claude Code, so spawned
agents get the full file/Bash/git toolset, MCP servers (Playwright for the evaluator),
and the user's existing auth — no separate API key required for OAuth/subscription users.

The task prompt is passed on **stdin**, not as a positional arg, so it can never be
swallowed by a preceding variadic flag like ``--allowedTools a b c``.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from ._context import RunContext


def _log_result(ctx: RunContext, role: str, model: str, result: "AgentResult") -> None:
    """Append a one-line audit record per agent call. Without this, a failed/empty
    agent round leaves no trace (the process exits, stdout is gone) and the loop's
    no-op cause is unrecoverable — exactly the gap that cost a wasted run."""
    try:
        ctx.session_dir.mkdir(parents=True, exist_ok=True)
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "role": role, "model": model,
            "ok": result.ok, "returncode": result.returncode,
            "cost_usd": round(result.cost_usd, 4), "num_turns": result.num_turns,
            "text_head": (result.text or "")[:200],
        }
        with (ctx.session_dir / "agent_log.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # logging must never break a run
        pass


@dataclass
class AgentResult:
    ok: bool
    text: str
    cost_usd: float
    num_turns: int
    returncode: int
    raw: str


def _use_bare(ctx: RunContext) -> bool:
    mode = str(ctx.config.get("context", {}).get("bare_mode", "auto")).lower()
    if mode == "always":
        return True
    if mode == "never":
        return False
    # auto: --bare requires ANTHROPIC_API_KEY (it never reads OAuth/keychain), so only
    # enable it when a key is present — otherwise it would break subscription auth.
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def run_claude(
    ctx: RunContext,
    *,
    role: str,
    system_prompt: str,
    task_prompt: str,
    model: str,
    cwd: Path,
    allowed_tools: Sequence[str] = (),
    disallowed_tools: Sequence[str] = (),
    add_dirs: Sequence[Path] = (),
    mcp_config: Path | None = None,
    permission_mode: str = "acceptEdits",
) -> AgentResult:
    """Spawn one headless ``claude`` agent. Returns its result text + cost."""
    timeout = int(ctx.config.get("execution", {}).get("agent_timeout_seconds", 5400))
    out_format = ctx.config.get("execution", {}).get("output_format", "json")

    cmd: list[str] = [
        "claude",
        "-p",
        "--model",
        model,
        "--output-format",
        out_format,
        "--permission-mode",
        permission_mode,
        "--append-system-prompt",
        system_prompt,
    ]
    if _use_bare(ctx):
        cmd.append("--bare")
    if mcp_config is not None:
        cmd += ["--mcp-config", str(mcp_config)]
    for d in add_dirs:
        cmd += ["--add-dir", str(d)]
    if disallowed_tools:
        cmd += ["--disallowedTools", *disallowed_tools]
    # variadic flag goes last so nothing positional can be absorbed into it
    if allowed_tools:
        cmd += ["--allowedTools", *allowed_tools]

    cwd.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            input=task_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"[{role}] agent exceeded {timeout}s wall-clock limit. "
            f"Lower the sprint scope or raise execution.agent_timeout_seconds."
        ) from exc

    raw = proc.stdout or ""
    text, cost, turns = _parse_output(raw, out_format)
    ok = proc.returncode == 0
    if not ok and not text:
        text = (proc.stderr or "").strip()
    result = AgentResult(
        ok=ok, text=text, cost_usd=cost, num_turns=turns, returncode=proc.returncode, raw=raw
    )
    _log_result(ctx, role, model, result)
    return result


def run_claude_resilient(ctx: RunContext, *, role: str, **kwargs: Any) -> "AgentResult":
    """Run an agent, retrying ONCE if the process was killed by a signal (returncode < 0,
    e.g. -9 SIGKILL / -15 SIGTERM). The evaluator's live-browser QA spawns Chromium + a dev
    server for minutes and can be transiently killed by an OS memory spike — a single retry
    rides out the blip. Only signal-kills are retried (transient); normal non-zero exits and
    successes are returned as-is. Each attempt is logged, so retries are visible in the audit."""
    res = run_claude(ctx, role=role, **kwargs)
    if res.returncode < 0 and not res.ok:
        res = run_claude(ctx, role=f"{role}:retry", **kwargs)
    return res


def ensure_ok(result: "AgentResult", role: str) -> "AgentResult":
    """Raise loudly if an agent call hard-failed (non-zero exit, e.g. usage limit, auth
    error, crash). Without this the orchestrator would treat a failed call as a normal
    FAIL and keep looping over stale artifacts — burning money on dead rounds."""
    if not result.ok:
        raise RuntimeError(
            f"[{role}] agent call failed (rc={result.returncode}). This usually means a "
            f"usage limit, auth error, or crash — NOT a normal QA fail. Stopping the loop. "
            f"Agent output head: {result.text[:400]!r}"
        )
    return result


def _parse_output(raw: str, out_format: str) -> tuple[str, float, int]:
    if out_format != "json":
        return raw.strip(), 0.0, 0
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError:
        return raw.strip(), 0.0, 0
    if isinstance(data, dict):
        return (
            str(data.get("result", "")).strip(),
            float(data.get("total_cost_usd", 0.0) or 0.0),
            int(data.get("num_turns", 0) or 0),
        )
    return raw.strip(), 0.0, 0


def wiring_probe(ctx: RunContext) -> AgentResult:
    """Cheap real call to confirm the subprocess + flag wiring works end-to-end.

    Uses the configured probe model (haiku) and a trivial prompt. ~1 cent.
    """
    model = ctx.config.get("models", {}).get("dry_run_probe", "haiku")
    return run_claude(
        ctx,
        role="probe",
        system_prompt="You are a wiring probe. Obey the user literally.",
        task_prompt="Reply with exactly this token and nothing else: WIRING_OK",
        model=model,
        cwd=ctx.harness_dir,
        allowed_tools=(),  # no tools needed
        permission_mode="default",
    )


def wiring_probe_full_posture(ctx: RunContext) -> AgentResult:
    """Exercise the EXACT flag stack real agents use — the risky path nothing else hits.

    Variadic ``--allowedTools``, repeated ``--add-dir``, ``--disallowedTools``, and
    ``--permission-mode acceptEdits``, then confirm a scoped tool actually fires. If the
    variadic flag mis-parsed, the Glob call would be denied and stall — so a DONE here
    proves the production invocation parses and tools are reachable. ~1 cent.
    """
    model = ctx.config.get("models", {}).get("dry_run_probe", "haiku")
    return run_claude(
        ctx,
        role="probe-full",
        system_prompt="You are a wiring probe. Use tools as instructed, then answer.",
        task_prompt="Use the Glob tool with pattern '*.json' here, then reply with "
        "exactly: PROBE_DONE",
        model=model,
        cwd=ctx.schemas_dir,
        allowed_tools=["Read", "Glob"],
        disallowed_tools=["Edit"],
        add_dirs=[ctx.schemas_dir],
        permission_mode="acceptEdits",
    )
