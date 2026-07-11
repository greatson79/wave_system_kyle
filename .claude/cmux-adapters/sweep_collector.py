#!/usr/bin/env python3
"""Create one atomic, read-only SweepSnapshot from cmux and process observations."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


DEFAULT_THRESHOLDS = {
    "screen_unchanged_seconds": 300,
    "context_threshold_percent": 60,
    "proc_count_high": 20,
    "working_interval_seconds": 30,
    "idle_interval_seconds": 300,
    "due_early_tolerance_seconds": 5,
    "claude_usage_gate_percent": 92,
}
DEFAULT_CMUX_BIN = "/Applications/cmux.app/Contents/Resources/bin/cmux"
CTX_RE = re.compile(r"\bCtx\s*[:=]?\s*(\d{1,3})%", re.IGNORECASE)
HEALTH_RE = re.compile(r"\b(login|log in|sign in|authentication|error|failed)\b", re.IGNORECASE)
TODO_RE = re.compile(r"^\s*-\s*\[ \]\s+(.+?)\s*$", re.MULTILINE)
CLAUDE_MODEL_RE = re.compile(r"\bModel:\s*([A-Za-z][A-Za-z0-9 ._-]*?)(?=\s{2,}|\s*[·|(,]|\s*$)", re.MULTILINE)
CODEX_MODEL_RE = re.compile(r"\bgpt-[A-Za-z0-9.-]+\b")
VM_PAGE_SIZE_RE = re.compile(r"page size of (\d+) bytes")
VM_PAGES_FREE_RE = re.compile(r"Pages free:\s+(\d+)")
LOAD_AVERAGES_RE = re.compile(r"load averages?:\s*([\d.]+),?\s+([\d.]+),?\s+([\d.]+)")
ALERT_HISTORY_LIMIT = 10
# C-ENGINE-1: 모델 배지는 화면 하단 상태줄 영역에서만 인정 — 대화 본문 스크롤백 오귀속 차단.
STATUS_LINE_WINDOW = 5
GEMMA_STAGING_SUBDIRS = ("sources", "entities", "concepts")
OLLAMA_PS_URL = "http://127.0.0.1:11434/api/ps"
# Probe failures degrade to null values; anything else (e.g. programming errors) must surface.
PROBE_ERRORS = (RuntimeError, OSError, ValueError)
CLAUDE_USAGE_NOTE = "정확 측정 불가 — 세션 로그 기반 근사 방법 확정 전까지 미제공"


@dataclass(frozen=True)
class CollectorPaths:
    root: Path
    roster_path: Path
    thresholds_path: Path
    todo_map_path: Path
    overlay_path: Path
    snapshot_path: Path
    state_path: Path
    lock_path: Path

    @classmethod
    def for_root(cls, root: Path) -> "CollectorPaths":
        root = root.resolve()
        adapter_dir = root / ".claude" / "cmux-adapters"
        round_dir = root / "output" / "DiA" / "경영본부" / "_round"
        return cls(
            root=root,
            roster_path=adapter_dir / "tower_roster.json",
            thresholds_path=adapter_dir / "collector_thresholds.json",
            todo_map_path=adapter_dir / "todo_fallback_map.json",
            overlay_path=round_dir / "CSO_스윕원장.overlay.json",
            snapshot_path=round_dir / "SweepSnapshot.json",
            state_path=round_dir / "SweepSnapshot.state.json",
            lock_path=round_dir / "SweepSnapshot.tick.lock",
        )


class CollectorBusyError(RuntimeError):
    """Raised when launchd starts a tick while another tick still owns the lock."""


@contextmanager
def tick_lock(paths: CollectorPaths) -> Iterable[None]:
    """Acquire the one-tick-at-a-time lock required by the launchd execution model."""
    paths.lock_path.parent.mkdir(parents=True, exist_ok=True)
    with paths.lock_path.open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise CollectorBusyError("collector tick already running") from error
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        temporary_path = Path(handle.name)
    os.replace(temporary_path, path)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload


def _load_mapping(path: Path) -> dict[str, str]:
    payload = _load_json(path, {})
    if not isinstance(payload, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in payload.items()
    ):
        raise ValueError(f"invalid string mapping: {path}")
    return payload


def _load_roster(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Accept v1 role→surface strings and the v2 {"surface", "engine"} extension side by side."""
    payload = _load_json(path, {})
    if not isinstance(payload, dict):
        raise ValueError(f"invalid roster file: {path}")
    surface_by_role: dict[str, str] = {}
    engine_by_role: dict[str, str] = {}
    for role, value in payload.items():
        if not isinstance(role, str):
            raise ValueError(f"invalid roster key: {role!r}")
        if isinstance(value, str):
            surface_by_role[role] = value
            continue
        if isinstance(value, dict) and isinstance(value.get("surface"), str):
            surface_by_role[role] = value["surface"]
            if isinstance(value.get("engine"), str):
                engine_by_role[role] = value["engine"]
            continue
        raise ValueError(f"invalid roster entry for {role!r}: {value!r}")
    return surface_by_role, engine_by_role


def _load_thresholds(path: Path) -> dict[str, int]:
    payload = _load_json(path, {})
    if not isinstance(payload, dict):
        raise ValueError(f"invalid thresholds file: {path}")
    thresholds = dict(DEFAULT_THRESHOLDS)
    for name in DEFAULT_THRESHOLDS:
        if name in payload:
            value = payload[name]
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"invalid threshold {name}: {value!r}")
            thresholds[name] = value
    return thresholds


def _default_run_command(argv: list[str]) -> str:
    completed = subprocess.run(argv, capture_output=True, text=True)
    if completed.returncode not in (0, 1):
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(argv)}: {detail}")
    return completed.stdout


def resolve_cmux_bin(environ: dict[str, str] | None = None) -> str:
    """Resolve cmux without depending on a launchd PATH search."""
    environ = os.environ if environ is None else environ
    candidate = Path(environ.get("CMUX_BIN", DEFAULT_CMUX_BIN)).expanduser()
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        raise RuntimeError(
            "cmux executable unavailable: "
            f"{candidate}; set CMUX_BIN to an executable absolute path"
        )
    return str(candidate)


def _iter_terminal_surfaces(tree: dict[str, Any]) -> Iterable[tuple[str, str, dict[str, Any]]]:
    for window in tree.get("windows", []):
        for workspace in window.get("workspaces", []):
            workspace_ref = workspace.get("ref")
            if not isinstance(workspace_ref, str):
                continue
            workspace_name = workspace.get("title") if isinstance(workspace.get("title"), str) else workspace_ref
            for pane in workspace.get("panes", []):
                for surface in pane.get("surfaces", []):
                    if surface.get("type") == "terminal" and isinstance(surface.get("ref"), str):
                        yield workspace_ref, workspace_name, surface


def _owner_for_tty(run_command: Callable[[list[str]], str], tty: Any) -> tuple[int | None, int | None, int]:
    if not isinstance(tty, str) or not tty:
        return None, None, 0
    rows = run_command(["ps", "-t", tty, "-o", "pid=,pgid="]).strip().splitlines()
    if not rows:
        return None, None, 0
    parts = rows[0].split()
    if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return None, None, 0
    pid, pgid = int(parts[0]), int(parts[1])
    child_lines = [line for line in run_command(["pgrep", "-P", str(pid)]).splitlines() if line.strip()]
    return pid, pgid, len(child_lines)


def _overlay_for(overlay: dict[str, Any], workspace_ref: str, surface_ref: str) -> dict[str, Any]:
    panes = overlay.get("panes") if isinstance(overlay, dict) else None
    if not isinstance(panes, dict):
        return {}
    candidate = panes.get(f"{workspace_ref}/{surface_ref}")
    return candidate if isinstance(candidate, dict) else {}


def _todo_fallback(todo_map: dict[str, str], role: str | None) -> tuple[str | None, str | None]:
    if not role or role not in todo_map:
        return None, None
    path = Path(todo_map[role])
    if not path.is_absolute() or not path.is_file():
        return None, None
    match = TODO_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        return None, None
    observed_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    return match.group(1), observed_at


def _health_alert(screen: str) -> bool:
    return "\ufffd" in screen or bool(HEALTH_RE.search(screen))


def _iso(now: datetime) -> str:
    return now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _status_line_region(screen: str) -> str:
    """Bounded final slice of the captured buffer — the only region model parsing may see."""
    return "\n".join(screen.splitlines()[-STATUS_LINE_WINDOW:])


def _parse_engine_model(status_line_region: str) -> str | None:
    """Extract only the badge string from the bounded status-line region (never the full buffer)."""
    claude_match = CLAUDE_MODEL_RE.search(status_line_region)
    if claude_match:
        return claude_match.group(1).strip()
    codex_match = CODEX_MODEL_RE.search(status_line_region)
    if codex_match:
        return codex_match.group(0)
    return None


def _probe_system_resources(run_command: Callable[[list[str]], str]) -> dict[str, Any]:
    """Local low-cost probes; each value fails closed to null instead of guessing."""
    mem_free_mb: int | None = None
    try:
        vm_stat_output = run_command(["vm_stat"])
        page_size_match = VM_PAGE_SIZE_RE.search(vm_stat_output)
        pages_free_match = VM_PAGES_FREE_RE.search(vm_stat_output)
        if page_size_match and pages_free_match:
            mem_free_mb = int(pages_free_match.group(1)) * int(page_size_match.group(1)) // (1024 * 1024)
    except PROBE_ERRORS:
        pass
    load_1m = load_5m = load_15m = None
    try:
        load_match = LOAD_AVERAGES_RE.search(run_command(["uptime"]))
        if load_match:
            load_1m, load_5m, load_15m = (float(load_match.group(index)) for index in (1, 2, 3))
    except PROBE_ERRORS:
        pass
    ollama_loaded_models: list[str] | None = None
    try:
        payload = json.loads(run_command(["curl", "-s", "--max-time", "2", OLLAMA_PS_URL]))
        models = payload.get("models") if isinstance(payload, dict) else None
        if isinstance(models, list):
            ollama_loaded_models = [
                model["name"] for model in models if isinstance(model, dict) and isinstance(model.get("name"), str)
            ]
    except PROBE_ERRORS:
        pass
    return {
        "mem_free_mb": mem_free_mb,
        "load_1m": load_1m,
        "load_5m": load_5m,
        "load_15m": load_15m,
        "ollama_loaded_models": ollama_loaded_models,
    }


def _claude_usage_status(thresholds: dict[str, int]) -> dict[str, Any]:
    """No trusted local approximation exists yet — report honest unavailability, never fake precision."""
    return {
        "approx_pct": None,
        "basis": "unavailable",
        "gate_percent": thresholds["claude_usage_gate_percent"],
        "note": CLAUDE_USAGE_NOTE,
    }


def _gemma_triage_status(gemma_dir: Path) -> dict[str, Any]:
    staging_dir = gemma_dir / "staging"
    staged_count: int | None = None
    if staging_dir.is_dir():
        staged_count = sum(
            len(list((staging_dir / subdir).glob("*.md")))
            for subdir in GEMMA_STAGING_SUBDIRS
            if (staging_dir / subdir).is_dir()
        )
    last_run_at: str | None = None
    last_run_ok: bool | None = None
    heartbeat_path = gemma_dir / "heartbeat.json"
    if heartbeat_path.is_file():
        try:
            heartbeat = json.loads(heartbeat_path.read_text(encoding="utf-8"))
            if isinstance(heartbeat, dict):
                if isinstance(heartbeat.get("last_run"), str):
                    last_run_at = heartbeat["last_run"]
                if isinstance(heartbeat.get("exit_code"), int):
                    last_run_ok = heartbeat["exit_code"] == 0
        except (OSError, ValueError):
            pass
    return {"staged_count": staged_count, "last_run_at": last_run_at, "last_run_ok": last_run_ok}


def _collect_system_status(
    run_command: Callable[[list[str]], str], thresholds: dict[str, int], gemma_dir: Path
) -> dict[str, Any]:
    return {
        "system_resources": _probe_system_resources(run_command),
        "claude_usage": _claude_usage_status(thresholds),
        "gemma_triage": _gemma_triage_status(gemma_dir),
    }


def _next_alert_history(previous: dict[str, Any], alerts: list[str], now_iso: str) -> list[dict[str, Any]]:
    """Ring buffer of recent alert events; old entries are dropped, never accumulated forever."""
    history = previous.get("alert_history")
    events = [
        event
        for event in (history if isinstance(history, list) else [])
        if isinstance(event, dict) and isinstance(event.get("condition"), str)
    ]
    events.extend({"condition": alert, "observed_at": now_iso} for alert in alerts)
    return events[-ALERT_HISTORY_LIMIT:]


def collect_once(
    paths: CollectorPaths,
    *,
    run_command: Callable[[list[str]], str] = _default_run_command,
    now: datetime | None = None,
    cmux_bin: str | None = None,
    gemma_dir: Path | None = None,
) -> dict[str, Any]:
    """Observe once, persist only derived values, then atomically publish the snapshot."""
    started = time.monotonic()
    now = now or datetime.now(timezone.utc)
    now_iso = _iso(now)
    cmux_bin = cmux_bin or resolve_cmux_bin()
    gemma_dir = gemma_dir or Path.home() / "wave-gemma-triage"
    surface_by_role, engine_by_role = _load_roster(paths.roster_path)
    role_by_surface = {surface_ref: role for role, surface_ref in surface_by_role.items()}
    thresholds = _load_thresholds(paths.thresholds_path)
    todo_map = _load_mapping(paths.todo_map_path)
    overlay_payload = _load_json(paths.overlay_path, {})
    overlay = overlay_payload if isinstance(overlay_payload, dict) else {}
    previous_payload = _load_json(paths.state_path, {"panes": {}, "sequence": 0})
    previous_panes = previous_payload.get("panes", {}) if isinstance(previous_payload, dict) else {}
    if not isinstance(previous_panes, dict):
        previous_panes = {}
    sequence = previous_payload.get("sequence", 0) if isinstance(previous_payload, dict) else 0
    sequence = sequence + 1 if isinstance(sequence, int) else 1

    tree = json.loads(run_command([cmux_bin, "tree", "--all", "--json"]))
    if not isinstance(tree, dict):
        raise ValueError("cmux tree output is not a JSON object")
    panes: list[dict[str, Any]] = []
    next_state: dict[str, Any] = {}
    alerts_summary: list[dict[str, Any]] = []

    for workspace_ref, workspace_name, surface in _iter_terminal_surfaces(tree):
        surface_ref = surface["ref"]
        pane_key = f"{workspace_ref}/{surface_ref}"
        previous = previous_panes.get(pane_key, {})
        if not isinstance(previous, dict):
            previous = {}
        role = role_by_surface.get(surface_ref)
        title = surface.get("title") if isinstance(surface.get("title"), str) else None
        entry_overlay = _overlay_for(overlay, workspace_ref, surface_ref)
        capture_screen = (
            not previous
            or previous.get("state") == "working"
            or bool(entry_overlay.get("next_expected_event"))
            or (role is not None and title is not None and title != role)
        )
        screen = ""
        screen_hash = previous.get("screen_hash")
        if capture_screen:
            screen = run_command([cmux_bin, "read-screen", "--workspace", workspace_ref, "--surface", surface_ref])
            screen_hash = hashlib.sha256(screen.encode("utf-8")).hexdigest()
        previous_hash = previous.get("screen_hash")
        hash_changed = bool(screen_hash and screen_hash != previous_hash)
        last_io_at = now_iso if hash_changed or not previous.get("last_io_at") else previous["last_io_at"]
        owner_pid, owner_pgid, child_count = _owner_for_tty(run_command, surface.get("tty"))

        alerts: list[str] = []
        ctx_match = CTX_RE.search(screen)
        if ctx_match and int(ctx_match.group(1)) >= thresholds["context_threshold_percent"]:
            alerts.append("context.threshold")
        if screen and _health_alert(screen):
            alerts.append("health.alert")
        if child_count >= thresholds["proc_count_high"]:
            alerts.append("proc_count_high")
        if previous_hash and screen_hash == previous_hash:
            alerts.append("pane.idle")
            unchanged_since = previous.get("last_io_at")
            if isinstance(unchanged_since, str):
                try:
                    age = now - datetime.fromisoformat(unchanged_since.replace("Z", "+00:00"))
                    if age >= timedelta(seconds=thresholds["screen_unchanged_seconds"]):
                        alerts.append("read_screen_escalation")
                except ValueError:
                    alerts.append("read_screen_escalation")
        if entry_overlay.get("next_expected_event") and entry_overlay.get("due_at"):
            try:
                due_at = datetime.fromisoformat(str(entry_overlay["due_at"]).replace("Z", "+00:00"))
                if due_at <= now:
                    alerts.append("read_screen_escalation")
            except ValueError:
                alerts.append("read_screen_escalation")

        todo_latest_item, todo_latest_item_observed_at = _todo_fallback(todo_map, role)
        if role and title and title != role:
            current_task = title
            task_basis = "pane_title"
            task_observed_at = now_iso
        elif isinstance(entry_overlay.get("current_task"), str):
            current_task = entry_overlay["current_task"]
            task_basis = "cso_overlay"
            task_observed_at = entry_overlay.get("observed_at") if isinstance(entry_overlay.get("observed_at"), str) else now_iso
        else:
            current_task, task_observed_at = todo_latest_item, todo_latest_item_observed_at
            task_basis = "todo_fallback" if current_task is not None else "none"

        # C-ENGINE-1: 이번 tick에 상태줄 영역에서 직접 파싱된 값만 인정 — 이전 tick 값 재사용 금지.
        if role is not None and role in engine_by_role:
            engine_model: str | None = engine_by_role[role]
            engine_model_basis = "roster_static"
        else:
            engine_model = _parse_engine_model(_status_line_region(screen)) if screen else None
            engine_model_basis = "status_line_parse" if engine_model is not None else "unknown"
        alert_history = _next_alert_history(previous, alerts, now_iso)

        if "health.alert" in alerts:
            state = "blocked"
        elif hash_changed or task_basis in {"pane_title", "cso_overlay"}:
            state = "working"
        else:
            state = "idle"
        entry = {
            "workspace_ref": workspace_ref,
            "workspace_name": workspace_name,
            "surface_ref": surface_ref,
            "role": role,
            "observed_at": now_iso,
            "last_io_at": last_io_at,
            "state": state,
            "owner_pid": owner_pid,
            "owner_pgid": owner_pgid,
            "next_expected_event": entry_overlay.get("next_expected_event"),
            "hash_changed_since_last": hash_changed,
            "alerts": alerts,
            "current_task": current_task,
            "current_task_basis": task_basis,
            "current_task_observed_at": task_observed_at,
            "todo_latest_item": todo_latest_item,
            "todo_latest_item_observed_at": todo_latest_item_observed_at,
            "alert_history": alert_history,
            "engine_model": engine_model,
            "engine_model_basis": engine_model_basis,
        }
        panes.append(entry)
        next_state[pane_key] = {
            "screen_hash": screen_hash,
            "last_io_at": last_io_at,
            "state": state,
            "alert_history": alert_history,
        }
        for alert in alerts:
            alerts_summary.append({"condition": alert, "workspace_ref": workspace_ref, "surface_ref": surface_ref})

    next_due_seconds = (
        thresholds["working_interval_seconds"]
        if any(pane["state"] == "working" for pane in panes)
        else thresholds["idle_interval_seconds"]
    )
    snapshot = {
        "generation_id": f"{now.strftime('%Y%m%dT%H%M%SZ')}-{sequence}",
        "generated_at": now_iso,
        "tree_observed_at": now_iso,
        "system_status": _collect_system_status(run_command, thresholds, gemma_dir),
        "panes": panes,
        "alerts_summary": alerts_summary,
        "collector_meta": {
            "run_ok": True,
            "duration_ms": int((time.monotonic() - started) * 1000),
            "next_due_at": _iso(now + timedelta(seconds=next_due_seconds)),
        },
    }
    _atomic_json_write(paths.snapshot_path, snapshot)
    _atomic_json_write(
        paths.state_path,
        {"sequence": sequence, "panes": next_state, "next_due_at": snapshot["collector_meta"]["next_due_at"]},
    )
    return snapshot


def run_tick(
    paths: CollectorPaths,
    *,
    run_command: Callable[[list[str]], str] = _default_run_command,
    now: datetime | None = None,
    cmux_bin: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Run one launchd tick, skipping observation until the persisted due time."""
    now = now or datetime.now(timezone.utc)
    with tick_lock(paths):
        state = _load_json(paths.state_path, {})
        next_due_at = _parse_due_at(state.get("next_due_at") if isinstance(state, dict) else None)
        thresholds = _load_thresholds(paths.thresholds_path)
        if not force and should_defer_tick(
            state,
            next_due_at=next_due_at,
            now=now,
            early_tolerance_seconds=thresholds["due_early_tolerance_seconds"],
        ):
            return {"status": "skipped", "next_due_at": _iso(next_due_at)}
        snapshot = collect_once(paths, run_command=run_command, now=now, cmux_bin=cmux_bin)
        return {
            "status": "collected",
            "generation_id": snapshot["generation_id"],
            "next_due_at": snapshot["collector_meta"]["next_due_at"],
        }


def _parse_due_at(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def is_tick_due(next_due_at: datetime, *, now: datetime, early_tolerance_seconds: int) -> bool:
    """Treat a scheduler tick narrowly before its due instant as due, not as a full-cycle skip."""
    return now + timedelta(seconds=early_tolerance_seconds) >= next_due_at


def should_defer_tick(
    state: Any,
    *,
    next_due_at: datetime | None,
    now: datetime,
    early_tolerance_seconds: int,
) -> bool:
    """Apply 30-second launchd polling while work exists; back off only when all panes are non-working."""
    panes = state.get("panes", {}) if isinstance(state, dict) else {}
    has_working_pane = isinstance(panes, dict) and any(
        isinstance(pane, dict) and pane.get("state") == "working" for pane in panes.values()
    )
    return not has_working_pane and next_due_at is not None and not is_tick_due(
        next_due_at, now=now, early_tolerance_seconds=early_tolerance_seconds
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="perform one observation and exit")
    parser.add_argument("--force", action="store_true", help="ignore next_due_at for an operator-requested tick")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    if not args.once:
        parser.error("--once is required; this collector never runs as a long-lived daemon")
    try:
        result = run_tick(CollectorPaths.for_root(args.root), force=args.force)
    except CollectorBusyError:
        print(json.dumps({"status": "busy"}, ensure_ascii=False))
        return 0
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL collector tick: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
