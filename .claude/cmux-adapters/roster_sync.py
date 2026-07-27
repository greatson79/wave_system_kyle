#!/usr/bin/env python3
"""roster_sync.py — tower_roster.json <-> cmux tree 실측 정합 감사·동기화 (CSO 소유 가드)

배경(2026-07-25 오배송 사고): cmux 재기동으로 surface 번호가 전면 회전했으나 로스터는 구값으로
남아, 이를 신뢰한 CEO 각성 push가 4종 전부 오배송됐다. 근인은 boot_tower.sh의 멱등 경로가
roster_set()을 우회하는 구조적 결함이다. 이 도구는 그 결함과 무관하게 "명부 != 실측"을 상시
검출하는 독립 방어선이며, 동시에 **로스터의 유일한 writer**다(공통 lock + 원자 publish).

★R2 개정(reviewer-codex BLOCK 반영 · 2026-07-25)
  - A/B-1 부분일치 fail-open 제거: 자동 확정은 **정규화 완전일치 또는 명시 alias 완전일치**만.
    부분일치는 후보 수와 무관하게 AMBIGUOUS로 보고만 한다(가드가 틀린 주소를 정답으로 확정하는
    치명 경로 차단 — 실증 반례: 역할 'COO' vs 유일 제목 'COO-보조').
  - A/B-2 원자 publish: lock(flock) + tmp + fsync + os.replace. 모든 writer가 이 경로를 쓴다
    (boot_tower.sh의 roster_set은 `--set`으로 위임 — 사본 writer 금지).
  - A/B-3 오류 전파: 실패를 성공으로 전환하지 않는다. exit 0=정상 / 1=이상 잔존 / 2=내부오류.
  - B-3 죽은 셸 판정 fail-closed: ps 실패·tty 부재는 OK가 아니라 UNKNOWN. 에이전트 판별은
    광범위 휴리스틱이 아니라 **엔트리포인트 실측 패턴**(claude / .../bin/codex / agy)만 인정한다.

상태 계약
  OK          명부 = 실측(완전일치) + 에이전트 프로세스 생존
  DRIFT       역할은 완전일치로 특정됐으나 명부 주소가 다름 -> --fix 자동교정 대상(유일)
  AMBIGUOUS   완전일치 0 또는 2+ (부분일치 후보 존재 포함) -> 자동수정 금지·수동 판단
  NODE_ABSENT 실측에 해당 역할 탭 없음 -> stale 소거 후보(수동)
  DEAD_SHELL  탭은 있으나 에이전트 프로세스 부재 -> 발송해도 무응답(이번 사고 기전)
  UNKNOWN     생존 판별 불가(ps 실패·surface에 tty 없음) -> 정상으로 통과시키지 않는다

사용
  roster_sync.py --check                 감사만(이상 잔존 시 exit 1) — 세션시작 점검 고정항목
  roster_sync.py --fix                   DRIFT만 교정(그 외 이상 잔존 시 exit 1)
  roster_sync.py --set <역할> <surface:N> 단일 항목 원자 기록(boot_tower 전용 위임 경로)
  --tree-json <파일> / --ps-file <파일>   테스트용 주입(실측 대체) — 회귀 테스트가 이 경로를 쓴다
"""
import argparse
import fcntl
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime

CMUX = "/Applications/cmux.app/Contents/Resources/bin/cmux"
# ROSTER_PATH 환경변수는 **회귀 테스트 전용 seam**이다(운영에서는 설정하지 않는다).
ROSTER = pathlib.Path(os.environ.get(
    "ROSTER_PATH", "/Users/kylechoi/Desktop/Ai_works/.claude/cmux-adapters/tower_roster.json"))
LOCK = ROSTER.with_name(ROSTER.name + ".lock")
LOCK_TIMEOUT = 15.0

# 역할키 -> 탭명이 자명하지 않은 항목의 **명시** alias. 완전일치로만 쓰인다(추측 금지).
ALIAS = {
    "CEO 관제타워": "CEO",
    "카카오톡워커-Codex(HOLD)": "카카오톡·Codex(HOLD)",
}

# 에이전트 엔트리포인트(2026-07-25 ps 실측 근거). MCP 자식(npm exec·serena·notebooklm·
# mcp-server-*·node_repl·codex vendor 헬퍼)은 어느 패턴에도 걸리지 않는다.
AGENT_PATTERNS = [
    re.compile(r"(^|/)claude(\s|$)"),   # /Users/.../bin/claude --settings … · claude --dangerously…
    re.compile(r"(^|/)codex(\s|$)"),    # node /…/bin/codex resume <uuid> … · codex --dangerously…
    re.compile(r"(^|/)agy(\s|$)"),      # agy --dangerously-skip-permissions
]


class ToolError(RuntimeError):
    """내부 오류 — 정상 판정으로 강등하지 않고 exit 2로 전파한다."""


# ---------------------------------------------------------------- 실측 수집

def read_tree(tree_json=None):
    """cmux 실측 -> [{ref,title,tty,ws,ws_title}]. 실패는 예외(조용한 통과 경로 없음)."""
    if tree_json:
        # ★내부오류(rc=2)와 "이상 잔존"(rc=1)이 구별돼야 한다 — 미처리 예외는 rc=1로 떨어져
        #   호출자가 정상 감사 결과로 오인한다(회귀 테스트 3-3이 잡아낸 구멍).
        try:
            raw = pathlib.Path(tree_json).read_text()
        except OSError as e:
            raise ToolError(f"tree 스냅샷 파일 읽기 실패: {e}") from e
    else:
        try:
            r = subprocess.run([CMUX, "tree", "--all", "--json"],
                               capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as e:
            raise ToolError(f"cmux tree 실행 실패: {e}") from e
        if r.returncode != 0:
            raise ToolError(f"cmux tree 비정상 종료(rc={r.returncode}): {r.stderr.strip()[:200]}")
        raw = r.stdout
    try:
        d = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ToolError(f"cmux tree JSON 파싱 실패: {e}") from e
    rows = []
    for w in d.get("windows", []):
        for ws in w.get("workspaces", []):
            for p in ws.get("panes", []):
                for s in p.get("surfaces", []):
                    if s.get("type") == "browser":
                        continue
                    rows.append({"ref": s.get("ref", ""), "title": (s.get("title") or "").strip(),
                                 "tty": s.get("tty") or "", "ws": ws.get("ref", ""),
                                 "ws_title": ws.get("title") or ""})
    if not rows:
        raise ToolError("cmux tree에 터미널 surface가 0건 — 실측 불가로 간주(정상 통과 금지)")
    return rows


def read_live_ttys(ps_file=None):
    """에이전트가 실제로 물려 있는 tty 집합. 판별 불가 시 None(=UNKNOWN 전파)."""
    if ps_file:
        try:
            text = pathlib.Path(ps_file).read_text()
        except OSError as e:
            raise ToolError(f"ps 스냅샷 파일 읽기 실패: {e}") from e
    else:
        try:
            r = subprocess.run(["ps", "-Ao", "tty,command"], capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            return None
        if r.returncode != 0 or not r.stdout.strip():
            return None
        text = r.stdout
    ttys = set()
    for line in text.splitlines():
        if not line.startswith("ttys"):
            continue
        tty, _, cmd = line.partition(" ")
        cmd = cmd.strip()
        if any(p.search(cmd) for p in AGENT_PATTERNS):
            ttys.add(tty.strip())
    return ttys


# ---------------------------------------------------------------- 매칭(root of trust)

def norm(s):
    return re.sub(r"[\s·\-_()\[\]]", "", (s or "").lower())


def resolve(role, rows):
    """역할 -> 실측 surface. ★자동 확정은 완전일치만. 부분일치는 절대 확정하지 않는다."""
    target = norm(ALIAS.get(role, role))
    exact = [r for r in rows if norm(r["title"]) == target]
    if len(exact) == 1:
        return "EXACT", exact
    if len(exact) > 1:
        return "AMBIGUOUS", exact
    partial = [r for r in rows if target and (target in norm(r["title"]) or norm(r["title"]) in target)]
    if partial:
        # 후보가 1건이어도 확정하지 않는다(fail-open 차단 — 'COO' vs 'COO-보조').
        return "AMBIGUOUS", partial
    return "ABSENT", []


def audit(rows, live):
    roster = load_roster()
    by_ref = {r["ref"]: r for r in rows}
    findings = []
    for role, ref in roster.items():
        if role.startswith("_") or not isinstance(ref, str) or not ref.startswith("surface:"):
            continue
        state, cand = resolve(role, rows)
        if state == "AMBIGUOUS":
            desc = ", ".join(f"{c['ref']}\"{c['title']}\"" for c in cand[:4])
            findings.append((role, ref, None, "AMBIGUOUS",
                             f"완전일치 미확정(후보 {len(cand)}: {desc}) — 자동수정 금지"))
            continue
        if state == "ABSENT":
            occ = by_ref.get(ref)
            note = f"명부 주소 {ref}는 현재 '{occ['title']}' 점유" if occ else f"명부 주소 {ref} 자체가 tree 부재"
            findings.append((role, ref, None, "NODE_ABSENT", f"실측 탭 없음(stale 소거 후보) — {note}"))
            continue
        actual = cand[0]
        if actual["ref"] != ref:
            occ = by_ref.get(ref)
            risk = f"★구주소 {ref}는 현재 '{occ['title']}' = 오배송 위험" if occ else f"구주소 {ref}는 tree 부재"
            findings.append((role, ref, actual["ref"], "DRIFT",
                             f"{risk} / 실측={actual['ref']}({actual['ws']} {actual['ws_title']})"))
        elif live is None:
            findings.append((role, ref, ref, "UNKNOWN", "ps 실측 불가 — 생존 미확인(정상 통과 금지)"))
        elif not actual["tty"]:
            findings.append((role, ref, ref, "UNKNOWN", f"surface에 tty 없음({actual['ws']}) — 생존 미확인"))
        elif actual["tty"] not in live:
            # ★2026-07-25 생산 오탐 확인 후 강등(DEAD_SHELL -> UNKNOWN). cmux tree의 tty 필드는
            #   앱 재기동+surface auto-resume 뒤 실제 pty와 어긋난다(실증: CSO 자신의 pane=surface:5인데
            #   tree tty=ttys001, 실제 pty=ttys003). 이 기반으로 개발본부장·크리에이티브본부장(둘 다 생존)이
            #   DEAD_SHELL로 오판됐다. "발송해도 무응답"이라는 거짓 확신은 ★불필요한 재소환(=중복 노드)을
            #   유발하므로, 확정 판정 대신 UNKNOWN으로 낮춘다. 확정 생존판정은 read-screen 화면 시그니처가
            #   필요하며, 그 설계는 codex 검수(B-3) 결과를 받아 반영한다.
            findings.append((role, ref, ref, "UNKNOWN",
                             f"tty 대조 불일치({actual['tty']}) — ★tree tty 필드 stale 가능성이 있어 "
                             f"사망 확정 금지. read-screen 화면 시그니처로 직접 확인 필요"))
        else:
            findings.append((role, ref, ref, "OK", f"{actual['ws']} {actual['ws_title']} / {actual['tty']}"))
    return findings


# ---------------------------------------------------------------- 로스터 writer (유일 경로)

class _Lock:
    def __enter__(self):
        self.fh = open(LOCK, "a+")
        deadline = time.time() + LOCK_TIMEOUT
        while True:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except BlockingIOError:
                if time.time() >= deadline:
                    self.fh.close()
                    raise ToolError(f"로스터 lock 획득 실패({LOCK_TIMEOUT}s) — 동시 writer 의심")
                time.sleep(0.1)

    def __exit__(self, *a):
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()
        return False


def load_roster():
    try:
        return json.loads(ROSTER.read_text())
    except (OSError, json.JSONDecodeError) as e:
        raise ToolError(f"로스터 읽기 실패: {e}") from e


def publish(data):
    """tmp + fsync + os.replace 원자 교체. 부분 기록/절단 JSON을 만들지 않는다."""
    payload = json.dumps(data, ensure_ascii=False, indent=1)
    fd, tmp = tempfile.mkstemp(dir=str(ROSTER.parent), prefix=".roster.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ROSTER)
    except BaseException:
        pathlib.Path(tmp).unlink(missing_ok=True)
        raise
    dirfd = os.open(str(ROSTER.parent), os.O_RDONLY)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)


def set_entry(role, ref):
    """단일 항목 기록(read-modify-write 전체를 lock 안에서 — lost update 방지)."""
    if not re.fullmatch(r"surface:\d+", ref):
        raise ToolError(f"ref 형식 위반: {ref!r} (surface:N 만 허용 — bare 숫자 금지)")
    with _Lock():
        d = load_roster()
        old = d.get(role)
        d[role] = ref
        publish(d)
    return old


def fix(findings):
    targets = [f for f in findings if f[3] == "DRIFT"]
    if not targets:
        return []
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with _Lock():
        d = load_roster()
        (ROSTER.with_name(ROSTER.name + f".bak-sync-{stamp}")).write_text(
            json.dumps(d, ensure_ascii=False, indent=1))
        for role, _old, new, _s, _n in targets:
            d[role] = new
        publish(d)
    return targets


# ---------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--set", nargs=2, metavar=("역할", "surface:N"))
    ap.add_argument("--resolve", metavar="역할",
                    help="역할->surface 단일 해소. rc 0=확정(stdout=ref) / 3=AMBIGUOUS / 4=ABSENT / 2=내부오류")
    ap.add_argument("--tree-json")
    ap.add_argument("--ps-file")
    a = ap.parse_args()

    try:
        if a.resolve:
            # ★matcher 단일화: boot_tower.sh의 tab_exists가 이 경로를 호출한다.
            #   bash/python 이중 구현은 그 자체가 이번 사고 계열(구현 drift)이므로 금지.
            state, cand = resolve(a.resolve, read_tree(a.tree_json))
            if state == "EXACT":
                print(cand[0]["ref"])
                return 0
            if state == "AMBIGUOUS":
                print(f"[AMBIGUOUS] {a.resolve}: 완전일치 미확정 — 후보 "
                      + ", ".join(f"{c['ref']}\"{c['title']}\"" for c in cand[:4]), file=sys.stderr)
                return 3
            return 4

        if a.set:
            old = set_entry(a.set[0], a.set[1])
            print(f"[set] {a.set[0]}: {old} -> {a.set[1]}")
            return 0

        rows = read_tree(a.tree_json)
        live = read_live_ttys(a.ps_file)
        findings = audit(rows, live)

        if a.fix:
            for role, old, new, _s, _n in fix(findings):
                print(f"[fix] {role}: {old} -> {new}")
            findings = audit(read_tree(a.tree_json), live)  # 교정 후 재감사(잔존 판정 근거)

        width = max((len(f[0]) for f in findings), default=10)
        for role, old, new, state, note in findings:
            print(f"[{state:11}] {role:<{width}} {old:>12} -> {str(new or '-'):>12}  {note}")

        bad = [f for f in findings if f[3] != "OK"]
        if bad:
            print("\n★이상 잔존 " + str(len(bad)) + "건: " + ", ".join(f"{f[0]}({f[3]})" for f in bad), file=sys.stderr)
        print(f"\n요약: 총 {len(findings)}건 / 정상 {len(findings)-len(bad)} / 이상 {len(bad)}")
        return 1 if bad else 0

    except ToolError as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
