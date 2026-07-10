#!/usr/bin/env python3
"""cmux 주소 해소 어댑터 (cys 역할주소의 cmux 대체 — 2026-07-10 체제 전환).

역할/탭명 → workspace:N surface:N 결정론 해소. 회전 ID 하드코딩 금지 원칙의 집행 도구.
매칭 우선순위: surface title 정확일치 > surface title 부분일치 > workspace title 일치(그 ws의
selected surface). 다중 매칭 = 모호 오류(exit 2 · 후보 출력). 미발견 = exit 1.

사용: cmux_addr.py <역할|탭명> [--json]
출력(기본): "<workspace_ref> <surface_ref>\t<title>"
"""
import json
import subprocess
import sys

CMUX = "/Applications/cmux.app/Contents/Resources/bin/cmux"


def tree():
    out = subprocess.run([CMUX, "tree", "--all", "--json"], capture_output=True, text=True, timeout=10)
    if out.returncode != 0:
        sys.stderr.write(f"[cmux_addr] tree 실패: {out.stderr.strip()}\n")
        sys.exit(3)
    return json.loads(out.stdout)


def surfaces(d):
    for w in d.get("windows", []):
        for ws in w.get("workspaces", []):
            for p in ws.get("panes", []):
                for s in p.get("surfaces", []):
                    yield ws, s


def clean(title):
    # 스피너·상태 프리픽스(⠐⠂✶ 등) 제거 후 비교
    return "".join(ch for ch in (title or "") if ch.isascii() or ord(ch) > 0x3000 or ch.isalnum() or ch in " -_·").strip()


def resolve(query, data):
    q = query.strip().lower()
    exact, partial, ws_hits = [], [], []
    for ws, s in surfaces(data):
        t = clean(s.get("title") or "").lower()
        if t == q:
            exact.append((ws, s))
        elif q in t:
            partial.append((ws, s))
    if not exact and not partial:
        for w in data.get("windows", []):
            for ws in w.get("workspaces", []):
                if q in (ws.get("title") or "").lower():
                    sel = ws.get("panes", [{}])[0].get("selected_surface_ref")
                    for ws2, s in surfaces(data):
                        if ws2["ref"] == ws["ref"] and s["ref"] == sel:
                            ws_hits.append((ws2, s))
    hits = exact or partial or ws_hits
    return hits


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    if not args:
        sys.stderr.write("사용: cmux_addr.py <역할|탭명> [--json]\n")
        sys.exit(2)
    data = tree()
    hits = resolve(args[0], data)
    if not hits:
        sys.stderr.write(f"[cmux_addr] 미발견: '{args[0]}' — 추측 주소 사용 금지, 소환/타이틀 확인\n")
        sys.exit(1)
    if len(hits) > 1:
        sys.stderr.write(f"[cmux_addr] 모호({len(hits)}건) — 후보:\n")
        for ws, s in hits:
            sys.stderr.write(f"  {ws['ref']} {s['ref']}\t{s.get('title')}\n")
        sys.exit(2)
    ws, s = hits[0]
    if as_json:
        print(json.dumps({"workspace": ws["ref"], "surface": s["ref"], "title": s.get("title"),
                          "tty": s.get("tty"), "workspace_title": ws.get("title")}, ensure_ascii=False))
    else:
        print(f"{ws['ref']} {s['ref']}\t{s.get('title')}")


if __name__ == "__main__":
    main()
