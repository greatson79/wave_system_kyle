"""Shared run context, paths, signal tokens, schema validation, and workspace git.

Everything the three agents and the orchestrator need to coordinate via files lives
here, so the inter-agent protocol stays in one auditable place.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema

HARNESS_DIR = Path(__file__).resolve().parent.parent  # harness/

# ── Signal tokens (appended to artifact files to signal state changes) ──────────
READY_FOR_CONTRACT_REVIEW = "READY_FOR_CONTRACT_REVIEW"
CONTRACT_APPROVED = "CONTRACT_APPROVED"
READY_FOR_QA = "READY_FOR_QA"
QA_COMPLETE = "QA_COMPLETE"
SPRINT_PASSED = "SPRINT_PASSED"
SPRINT_FAILED = "SPRINT_FAILED"
HARNESS_COMPLETE = "HARNESS_COMPLETE"

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_len: int = 40) -> str:
    slug = _SLUG_RE.sub("-", text.lower()).strip("-")
    return (slug[:max_len].rstrip("-")) or "app"


@dataclass
class RunContext:
    """Everything one harness run needs to find its files and workspace."""

    user_prompt: str
    config: dict[str, Any]
    run_id: str
    dry_run: bool = False
    harness_dir: Path = field(default=HARNESS_DIR)
    costs: list[float] = field(default_factory=list)

    def record_cost(self, usd: float) -> None:
        if usd:
            self.costs.append(float(usd))

    @property
    def total_cost(self) -> float:
        return sum(self.costs)

    @property
    def artifacts_dir(self) -> Path:
        return self.harness_dir / self.config["communication"]["artifacts_dir"]

    @property
    def plan_dir(self) -> Path:
        return self.artifacts_dir / "plan"

    @property
    def sprints_dir(self) -> Path:
        return self.artifacts_dir / "sprints"

    @property
    def session_dir(self) -> Path:
        return self.artifacts_dir / "session"

    @property
    def workspace_dir(self) -> Path:
        return self.harness_dir / self.config["safety"]["workspace_root"] / self.run_id

    @property
    def schemas_dir(self) -> Path:
        return self.harness_dir / "schemas"

    # ── artifact paths ─────────────────────────────────────────────────────────
    @property
    def product_spec_md(self) -> Path:
        return self.plan_dir / "PRODUCT_SPEC.md"

    @property
    def sprints_json(self) -> Path:
        return self.plan_dir / "sprints.json"

    def contract_md(self, sprint: int) -> Path:
        return self.sprints_dir / f"sprint_{sprint}_contract.md"

    def contract_json(self, sprint: int) -> Path:
        return self.sprints_dir / f"sprint_{sprint}_contract.json"

    def qa_md(self, sprint: int) -> Path:
        return self.sprints_dir / f"sprint_{sprint}_qa_report.md"

    def qa_json(self, sprint: int) -> Path:
        return self.sprints_dir / f"sprint_{sprint}_qa_report.json"

    @property
    def handoff_md(self) -> Path:
        return self.session_dir / "handoff.md"

    def ensure_dirs(self) -> None:
        for d in (self.plan_dir, self.sprints_dir, self.session_dir, self.workspace_dir):
            d.mkdir(parents=True, exist_ok=True)


# ── signal helpers ─────────────────────────────────────────────────────────────
def append_signal(path: Path, token: str) -> None:
    """Append a signal token on its own final line (idempotent-ish, append-only)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    sep = "" if existing.endswith("\n") or not existing else "\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{sep}\n{token}\n")


def has_signal(path: Path, token: str) -> bool:
    if not path.exists():
        return False
    return any(line.strip() == token for line in path.read_text(encoding="utf-8").splitlines())


# ── schema validation ──────────────────────────────────────────────────────────
def load_schema(ctx: RunContext, name: str) -> dict[str, Any]:
    return json.loads((ctx.schemas_dir / name).read_text(encoding="utf-8"))


def validate_json_file(ctx: RunContext, json_path: Path, schema_name: str) -> dict[str, Any]:
    """Load a JSON artifact and validate it. Raises a clear error on failure."""
    if not json_path.exists():
        raise FileNotFoundError(f"Expected artifact not produced: {json_path}")
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{json_path.name} is not valid JSON: {exc}") from exc
    schema = load_schema(ctx, schema_name)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as exc:
        loc = "/".join(str(p) for p in exc.absolute_path) or "<root>"
        raise ValueError(
            f"{json_path.name} fails {schema_name} at {loc}: {exc.message}"
        ) from exc
    return data


def load_sprints(ctx: RunContext) -> list[dict[str, Any]]:
    data = validate_json_file(ctx, ctx.sprints_json, "product_spec.schema.json")
    return sorted(data["sprints"], key=lambda s: s["number"])


# ── workspace git (isolated from the parent monorepo) ──────────────────────────
def _git(ctx: RunContext, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ctx.workspace_dir,
        capture_output=True,
        text=True,
    )


def init_workspace_git(ctx: RunContext) -> None:
    """git init the workspace as its OWN repo — never the parent monorepo."""
    ctx.workspace_dir.mkdir(parents=True, exist_ok=True)
    if (ctx.workspace_dir / ".git").exists():
        return
    _git(ctx, "init", "-q")
    _git(ctx, "config", "user.email", "harness@wave.ai")
    _git(ctx, "config", "user.name", "Harness Generator")
    # baseline commit so per-sprint rollback always has a target
    (ctx.workspace_dir / ".gitignore").write_text(
        "node_modules/\n.venv/\n__pycache__/\n*.db\ndist/\nbuild/\n.env\n",
        encoding="utf-8",
    )
    _git(ctx, "add", "-A")
    _git(ctx, "commit", "-q", "-m", "chore: workspace baseline (harness)")


def git_commit(ctx: RunContext, message: str) -> str | None:
    _git(ctx, "add", "-A")
    res = _git(ctx, "commit", "-q", "-m", message)
    if res.returncode != 0 and "nothing to commit" in (res.stdout + res.stderr).lower():
        return None
    head = _git(ctx, "rev-parse", "--short", "HEAD")
    return head.stdout.strip() or None


def git_is_dirty(ctx: RunContext) -> bool:
    res = _git(ctx, "status", "--porcelain")
    return bool(res.stdout.strip())


def git_revert_working_tree(ctx: RunContext) -> None:
    """Discard uncommitted changes — used to undo any edits the read-only evaluator made."""
    _git(ctx, "checkout", "--", ".")
    _git(ctx, "clean", "-fd", "-e", "node_modules", "-e", ".venv")


def git_head(ctx: RunContext) -> str | None:
    res = _git(ctx, "rev-parse", "--short", "HEAD")
    return res.stdout.strip() or None
