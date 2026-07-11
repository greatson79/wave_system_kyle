#!/usr/bin/env python3
"""Read-only localhost situation-room dashboard backed only by SweepSnapshot."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Sequence


STALE_GRACE_SECONDS = 35


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _activity_for(pane: dict[str, Any], stale: bool) -> tuple[str, str, str]:
    if stale:
        return "unknown", "미상", "snapshot_stale"
    state = pane.get("state")
    if state == "working":
        return "working", "가동중", "snapshot_fresh"
    if state == "idle":
        return "idle", "대기", "snapshot_fresh"
    if state == "blocked":
        return "unknown", "미상", "snapshot_blocked"
    return "unknown", "미상", "snapshot_format_error"


def _default_system_status() -> dict[str, Any]:
    """Fail-closed strip data for v1 snapshots that carry no system_status."""
    return {
        "system_resources": {
            "mem_free_mb": None,
            "load_1m": None,
            "load_5m": None,
            "load_15m": None,
            "ollama_loaded_models": None,
        },
        "claude_usage": {
            "approx_pct": None,
            "basis": "unavailable",
            "gate_percent": None,
            "note": "수집기 스냅샷에 사용량 정보 없음",
        },
        "gemma_triage": {"staged_count": None, "last_run_at": None, "last_run_ok": None},
    }


def build_world(snapshot: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Normalize a valid snapshot into the dashboard's three-state view model."""
    now = now or datetime.now(timezone.utc)
    generated_at = _parse_time(snapshot.get("generated_at"))
    due_at = _parse_time((snapshot.get("collector_meta") or {}).get("next_due_at"))
    stale = generated_at is None or due_at is None or now > due_at + timedelta(seconds=STALE_GRACE_SECONDS)
    panes = snapshot.get("panes")
    if not isinstance(panes, list):
        raise ValueError("snapshot panes must be a list")

    departments_by_ref: dict[str, dict[str, Any]] = {}
    for pane in panes:
        if not isinstance(pane, dict):
            continue
        workspace_ref = pane.get("workspace_ref")
        surface_ref = pane.get("surface_ref")
        if not isinstance(workspace_ref, str) or not isinstance(surface_ref, str):
            continue
        department = departments_by_ref.setdefault(
            workspace_ref,
            {
                "workspace_ref": workspace_ref,
                "name": pane.get("workspace_name") if isinstance(pane.get("workspace_name"), str) else workspace_ref,
                "workers": [],
            },
        )
        activity, activity_label, basis = _activity_for(pane, stale)
        department["workers"].append(
            {
                "surface_ref": surface_ref,
                "role": pane.get("role") if isinstance(pane.get("role"), str) else "미배정 surface",
                "activity": activity,
                "activity_label": activity_label,
                "basis": basis,
                "observed_at": pane.get("observed_at"),
                "current_task": pane.get("current_task"),
                "current_task_basis": pane.get("current_task_basis"),
                "current_task_observed_at": pane.get("current_task_observed_at"),
                "alerts": pane.get("alerts") if isinstance(pane.get("alerts"), list) else [],
                "last_io_at": pane.get("last_io_at"),
                "owner_pid": pane.get("owner_pid"),
                "owner_pgid": pane.get("owner_pgid"),
                "todo_latest_item": pane.get("todo_latest_item"),
                "todo_latest_item_observed_at": pane.get("todo_latest_item_observed_at"),
                "alert_history": pane.get("alert_history") if isinstance(pane.get("alert_history"), list) else [],
                "engine_model": pane.get("engine_model") if isinstance(pane.get("engine_model"), str) else None,
                "engine_model_basis": (
                    pane.get("engine_model_basis")
                    if isinstance(pane.get("engine_model_basis"), str)
                    else "unknown"
                ),
            }
        )
    departments = list(departments_by_ref.values())
    for department in departments:
        total = len(department["workers"])
        department["snapshot_coverage"] = {"recorded": total, "total": total}
    system_status = snapshot.get("system_status")
    return {
        "state": "ok",
        "generation_id": snapshot.get("generation_id"),
        "generated_at": snapshot.get("generated_at"),
        "tree_observed_at": snapshot.get("tree_observed_at"),
        "snapshot_stale": stale,
        "system_status": system_status if isinstance(system_status, dict) else _default_system_status(),
        "departments": departments,
        "alerts_summary": snapshot.get("alerts_summary") if isinstance(snapshot.get("alerts_summary"), list) else [],
    }


def load_world(snapshot_path: Path, *, now: datetime | None = None) -> dict[str, Any]:
    """Load the collector artifact; parse failures become an explicit unknown state."""
    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        if not isinstance(snapshot, dict):
            raise ValueError("snapshot root must be an object")
        return build_world(snapshot, now=now)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "state": "snapshot_error",
            "snapshot_stale": True,
            "error": str(error),
            "departments": [],
            "alerts_summary": [],
        }


def dashboard_html() -> str:
    """Static shell; dynamic values are fetched only from GET /api/world (system_status included)."""
    return """<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>상황실 대시보드</title><style>
:root{color-scheme:dark;font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;background:#10131a;color:#edf1f7}
body{margin:0;background:#10131a}.shell{max-width:1320px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;gap:18px;align-items:baseline}.top h1{margin:0;font-size:26px}.muted{color:#9da9bc;font-size:14px}.banner{margin:18px 0;padding:12px 14px;border-radius:10px;background:#3c2f12;color:#ffe4a3}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:16px}.card{border:1px solid #2a3241;border-radius:14px;background:#171c26;overflow:hidden}.head{padding:16px;border-bottom:1px solid #2a3241}.head h2{margin:0 0 6px;font-size:18px}.row{padding:14px 16px;border-bottom:1px solid #242c3a;cursor:pointer}.row:last-child{border:0}.row:hover{background:#1b2230}.worker{display:flex;justify-content:space-between;gap:10px;align-items:baseline}.badge{font-weight:700;white-space:nowrap}.working{color:#75e0a5}.idle{color:#a9b9d4}.unknown{color:#ffc66d}.task{margin:7px 0 0;color:#c9d2e2;font-size:14px;line-height:1.45}.basis{margin-top:5px;color:#8591a8;font-size:12px}.empty{padding:30px;color:#9da9bc;text-align:center}
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin:18px 0}.scard{border:1px solid #2a3241;border-radius:12px;background:#171c26;padding:14px 16px}.scard h3{margin:0 0 8px;font-size:13px;color:#9da9bc;font-weight:600;letter-spacing:.02em}.sval{font-size:15px;line-height:1.6;color:#dbe3f0}.swarn{color:#ffc66d}.gate{margin-top:6px;font-size:12px;color:#8591a8}
.engine{display:inline-block;margin-left:8px;padding:1px 8px;border:1px solid #35507a;border-radius:999px;background:#1a2740;color:#9cc0f5;font-size:11px;font-weight:600;white-space:nowrap;vertical-align:middle}.engine.unknown-engine{border-color:#3a4356;background:#1c2230;color:#8591a8}
.drilldown{display:none;margin-top:10px;padding:12px;border:1px solid #2a3241;border-radius:10px;background:#131824;font-size:13px}.row.open .drilldown{display:block}.drilldown dl{margin:0;display:grid;grid-template-columns:120px 1fr;gap:5px 12px}.drilldown dt{color:#8591a8}.drilldown dd{margin:0;color:#c9d2e2;word-break:break-all}.ah{margin:4px 0 0;padding-left:16px}.ah li{color:#e0a86a;font-size:12px}
.preview-banner{margin:0 0 14px;padding:10px 14px;border:1px solid #7a4a1f;border-radius:10px;background:#4a2c0e;color:#ffcf8a;font-weight:700;text-align:center;letter-spacing:.01em}
@media(max-width:600px){.shell{padding:18px}.top{display:block}.top .muted{display:block;margin-top:8px}.drilldown dl{grid-template-columns:1fr}}
</style></head><body><main class="shell"><div class="preview-banner">⚠ 미검수 프리뷰(codex 코드검수 전) — 블루그린 프리뷰 인스턴스, 정식 인수 전</div><div class="top"><h1>상황실 대시보드</h1><span class="muted" id="meta">스냅샷 로딩 중</span></div><div id="banner"></div><section class="strip" id="strip"></section><section class="grid" id="app"></section></main>
<script>
const esc=v=>String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const NA='<span class="swarn">측정 불가</span>';
const openRows=new Set();
const num=(v,unit='')=>typeof v==='number'?`${v}${unit}`:null;
function renderStrip(status){const strip=document.querySelector('#strip');if(!status){strip.innerHTML='';return;}const r=status.system_resources||{},u=status.claude_usage||{},g=status.gemma_triage||{};
const mem=num(r.mem_free_mb,' MB')?`free ${r.mem_free_mb.toLocaleString()} MB`:NA;
const load=[r.load_1m,r.load_5m,r.load_15m].every(v=>typeof v==='number')?`${r.load_1m} / ${r.load_5m} / ${r.load_15m}`:NA;
const ollama=Array.isArray(r.ollama_loaded_models)?(r.ollama_loaded_models.length?r.ollama_loaded_models.map(esc).join(', '):'로드된 모델 없음'):NA;
const usage=typeof u.approx_pct==='number'?`${u.approx_pct}% <span class="muted">(근사 · ${esc(u.basis)})</span>`:`${NA} <span class="muted">(basis: ${esc(u.basis||'unavailable')})</span>`;
const gate=typeof u.gate_percent==='number'?`<div class="gate">게이팅 임계 ${u.gate_percent}%${typeof u.approx_pct==='number'&&u.approx_pct>=u.gate_percent?' — <span class="swarn">임계 초과</span>':''}</div>`:'';
const note=u.note?`<div class="gate">${esc(u.note)}</div>`:'';
const staged=typeof g.staged_count==='number'?`스테이징 ${g.staged_count}건`:`스테이징 ${NA}`;
const lastRun=g.last_run_at?`최근 실행 ${esc(g.last_run_at)} · ${g.last_run_ok===true?'정상':g.last_run_ok===false?'<span class="swarn">실패</span>':'결과 미상'}`:'실행 이력 없음(파이프라인 미가동)';
strip.innerHTML=`<div class="scard"><h3>시스템 자원</h3><div class="sval">메모리 ${mem}<br>load ${load}<br>ollama: ${ollama}</div></div><div class="scard"><h3>Claude 사용량</h3><div class="sval">${usage}</div>${gate}${note}</div><div class="scard"><h3>젬마 트리아지</h3><div class="sval">${staged}<br>${lastRun}</div></div>`;}
function engineBadge(w){return w.engine_model?`<span class="engine" title="basis: ${esc(w.engine_model_basis)}">${esc(w.engine_model)}</span>`:'<span class="engine unknown-engine">엔진 미상</span>';}
function drilldown(w){const ah=(w.alert_history||[]).length?`<ul class="ah">${w.alert_history.map(e=>`<li>${esc(e.condition)} · ${esc(e.observed_at)}</li>`).join('')}</ul>`:'없음';
return `<div class="drilldown"><dl><dt>current_task 전문</dt><dd>${w.current_task?esc(w.current_task):'미상'} <span class="muted">(${esc(w.current_task_basis||'none')})</span></dd><dt>최근 활동 시각</dt><dd>${esc(w.last_io_at||'미상')}</dd><dt>TODO 최신 미완</dt><dd>${w.todo_latest_item?esc(w.todo_latest_item):'없음/미상'}</dd><dt>소유 프로세스</dt><dd>pid ${esc(w.owner_pid??'미상')} · pgid ${esc(w.owner_pgid??'미상')}</dd><dt>엔진·모델</dt><dd>${w.engine_model?esc(w.engine_model):'미상'} <span class="muted">(${esc(w.engine_model_basis||'unknown')})</span></dd><dt>최근 경보 이력</dt><dd>${ah}</dd></dl></div>`;}
function render(world){const app=document.querySelector('#app'),banner=document.querySelector('#banner'),meta=document.querySelector('#meta');meta.textContent=world.generated_at?`스냅샷: ${world.generated_at}`:'스냅샷 오류';banner.innerHTML=world.snapshot_stale?'<div class="banner">⚠ 수집기 응답 지연 — 모든 활동 상태를 미상으로 표시합니다.</div>':'';renderStrip(world.system_status);if(!world.departments?.length){app.innerHTML='<div class="card empty">관측 가능한 워커가 없습니다.</div>';return;}app.innerHTML=world.departments.map(d=>`<article class="card"><div class="head"><h2>${esc(d.name)}</h2><div class="muted">${esc(d.workspace_ref)} · 스냅샷 커버리지 ${d.snapshot_coverage.recorded}/${d.snapshot_coverage.total}</div></div>${d.workers.map(w=>{const key=`${d.workspace_ref}/${w.surface_ref}`;return `<div class="row${openRows.has(key)?' open':''}" data-key="${esc(key)}"><div class="worker"><strong>${esc(w.role)}${engineBadge(w)}</strong><span class="badge ${esc(w.activity)}">${esc(w.activity_label)}</span></div><div class="task">${w.current_task?esc(w.current_task):'작업 내용 미상'}</div><div class="basis">${esc(w.basis)} · ${esc(w.observed_at||'관측 시각 미상')}</div>${drilldown(w)}</div>`;}).join('')}</article>`).join('');}
document.querySelector('#app').addEventListener('click',event=>{const row=event.target.closest('.row');if(!row||!row.dataset.key)return;const key=row.dataset.key;openRows.has(key)?openRows.delete(key):openRows.add(key);row.classList.toggle('open');});
async function refresh(){try{const response=await fetch('/api/world',{cache:'no-store'});render(await response.json());}catch(error){render({snapshot_stale:true,departments:[]});}}
refresh();setInterval(refresh,5000);
</script></body></html>"""


def make_handler(snapshot_path: Path, now_factory: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/world":
                body = json.dumps(load_world(snapshot_path, now=now_factory()), ensure_ascii=False).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path == "/":
                body = dashboard_html().encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return DashboardHandler


def _default_snapshot_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "output" / "DiA" / "경영본부" / "_round" / "SweepSnapshot.json"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=_default_snapshot_path())
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(args.snapshot))
    print(f"situation-dashboard listening on http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
