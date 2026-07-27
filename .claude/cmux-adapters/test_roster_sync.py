#!/usr/bin/env python3
"""roster_sync.py 회귀 테스트 — reviewer-codex BLOCK(2026-07-25) 지정 케이스 전량 커버.

codex 요구: `COO`/`COO-보조`(부분일치 fail-open), 동명, tree 실패, tty 없음, 동시 writer.
여기에 CSO가 사고 재현(DRIFT)·죽은 셸(MCP 자식만 있는 tty)·원자성 케이스를 추가한다.

실행: python3 test_roster_sync.py   (종료코드 0 = 전량 통과)
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
MOD_PATH = HERE / "roster_sync.py"

PASS, FAIL = [], []


def load_module(roster_path):
    """ROSTER_PATH seam으로 임시 로스터를 물린 모듈 인스턴스를 새로 적재."""
    os.environ["ROSTER_PATH"] = str(roster_path)
    spec = importlib.util.spec_from_file_location(f"rs_{roster_path.name}", MOD_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tree(surfaces):
    """surfaces = [(ref, title, tty)] -> cmux tree --all --json 형태."""
    return {"windows": [{"workspaces": [{"ref": "workspace:1", "title": "경영본부", "panes": [
        {"surfaces": [{"ref": r, "title": t, "tty": y, "type": "terminal"} for r, t, y in surfaces]}]}]}]}


def write(tmp, name, obj):
    p = tmp / name
    p.write_text(json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj)
    return p


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else '★FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def states(findings):
    return {f[0]: f[3] for f in findings}


PS_CLAUDE = "ttys008 /Users/kylechoi/.local/bin/claude --settings {}\n"
PS_MCP_ONLY = ("ttys008 npm exec @upstash/context7-mcp\n"
               "ttys008 /Users/kylechoi/.local/bin/uv tool uvx --from serena-agent serena start-mcp-server\n"
               "ttys008 node /Users/kylechoi/.npm/_npx/abc/node_modules/.bin/notebooklm-mcp\n")
PS_CODEX = "ttys009 node /Users/kylechoi/.local/state/fnm_multishells/94148_1/bin/codex resume 019f91c1 -c x\n"
PS_CODEX_VENDOR_ONLY = ("ttys009 /Users/kylechoi/.local/share/fnm/node-versions/v24.14.0/installation/lib/"
                        "node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-x\n")


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)

        # ---------- 1. codex 지정: 부분일치 fail-open 차단 (COO vs COO-보조) ----------
        print("1. 부분일치 fail-open 차단 (codex 반례: COO / COO-보조)")
        rp = tmp / "r1.json"
        rp.write_text(json.dumps({"COO": "surface:9"}, ensure_ascii=False))
        m = load_module(rp)
        t = write(tmp, "t1.json", tree([("surface:1", "COO-보조", "ttys008")]))
        f = m.audit(m.read_tree(str(t)), m.read_live_ttys(str(write(tmp, "p1.txt", PS_CLAUDE))))
        check("COO는 'COO-보조'로 자동확정되지 않는다(AMBIGUOUS)", states(f).get("COO") == "AMBIGUOUS", states(f))
        check("--fix 대상(DRIFT)이 아니다", not [x for x in f if x[3] == "DRIFT"])
        check("로스터가 변경되지 않았다", json.loads(rp.read_text())["COO"] == "surface:9")

        # ---------- 2. codex 지정: 동명(완전일치 2건) ----------
        print("2. 동명 탭 2건")
        rp = tmp / "r2.json"
        rp.write_text(json.dumps({"COO": "surface:1"}, ensure_ascii=False))
        m = load_module(rp)
        t = write(tmp, "t2.json", tree([("surface:1", "COO", "ttys008"), ("surface:7", "COO", "ttys009")]))
        f = m.audit(m.read_tree(str(t)), {"ttys008", "ttys009"})
        check("동명은 AMBIGUOUS", states(f).get("COO") == "AMBIGUOUS", states(f))

        # ---------- 3. codex 지정: tree 실패 ----------
        print("3. tree 실패 계열 -> ToolError(exit 2)")
        m = load_module(tmp / "r3.json")
        (tmp / "r3.json").write_text("{}")
        for label, content in [("잘못된 JSON", "{not json"), ("빈 surface 목록", json.dumps(tree([])))]:
            p = write(tmp, f"t3_{label[:3]}.json", content)
            try:
                m.read_tree(str(p))
                check(f"{label} -> 예외", False, "예외가 발생하지 않음")
            except m.ToolError:
                check(f"{label} -> ToolError", True)
        r = subprocess.run([sys.executable, str(MOD_PATH), "--check", "--tree-json", str(tmp / "nonexistent.json")],
                           capture_output=True, text=True, env={**os.environ, "ROSTER_PATH": str(tmp / "r3.json")})
        check("존재하지 않는 tree 파일 -> exit 2(정상 통과 금지)", r.returncode == 2, f"rc={r.returncode}")

        # ---------- 4. codex 지정: tty 없음 / ps 실패 -> UNKNOWN ----------
        print("4. 생존 판별 불가 -> UNKNOWN (OK로 통과시키지 않는다)")
        rp = tmp / "r4.json"
        rp.write_text(json.dumps({"COO": "surface:1"}, ensure_ascii=False))
        m = load_module(rp)
        t_notty = write(tmp, "t4.json", tree([("surface:1", "COO", "")]))
        f = m.audit(m.read_tree(str(t_notty)), {"ttys008"})
        check("surface에 tty 없음 -> UNKNOWN", states(f).get("COO") == "UNKNOWN", states(f))
        t_ok = write(tmp, "t4b.json", tree([("surface:1", "COO", "ttys008")]))
        f = m.audit(m.read_tree(str(t_ok)), None)   # ps 실패 = None
        check("ps 실측 불가 -> UNKNOWN", states(f).get("COO") == "UNKNOWN", states(f))
        check("UNKNOWN은 이상으로 집계(exit 1 근거)", all(x[3] != "OK" for x in f))

        # ---------- 5. 죽은 셸 (엄격 매처가 MCP 자식에 속지 않는다) ----------
        print("5. DEAD_SHELL 판별 — MCP 자식/codex vendor 헬퍼는 에이전트가 아니다")
        rp = tmp / "r5.json"
        rp.write_text(json.dumps({"COO": "surface:1"}, ensure_ascii=False))
        m = load_module(rp)
        t = write(tmp, "t5.json", tree([("surface:1", "COO", "ttys008")]))
        f = m.audit(m.read_tree(str(t)), m.read_live_ttys(str(write(tmp, "p5.txt", PS_MCP_ONLY))))
        check("MCP 자식만 있는 tty -> UNKNOWN(사망 확정 금지·2026-07-25 강등)", states(f).get("COO") == "UNKNOWN", states(f))
        f = m.audit(m.read_tree(str(t)), m.read_live_ttys(str(write(tmp, "p5b.txt", PS_CLAUDE))))
        check("실제 claude 있으면 OK", states(f).get("COO") == "OK", states(f))
        rp.write_text(json.dumps({"reviewer-codex": "surface:1"}, ensure_ascii=False))
        t = write(tmp, "t5c.json", tree([("surface:1", "reviewer-codex", "ttys009")]))
        f = m.audit(m.read_tree(str(t)), m.read_live_ttys(str(write(tmp, "p5c.txt", PS_CODEX))))
        check("codex 엔트리포인트 인식 -> OK", states(f).get("reviewer-codex") == "OK", states(f))
        f = m.audit(m.read_tree(str(t)), m.read_live_ttys(str(write(tmp, "p5d.txt", PS_CODEX_VENDOR_ONLY))))
        check("codex vendor 헬퍼만 -> UNKNOWN(과탐 아님·사망 확정은 안 함)", states(f).get("reviewer-codex") == "UNKNOWN", states(f))

        # ---------- 6. 사고 재현: DRIFT 검출 + --fix ----------
        print("6. 사고 시그니처(개발본부장 s7이 타 노드 점유) 검출·교정")
        rp = tmp / "r6.json"
        rp.write_text(json.dumps({"개발본부장": "surface:7"}, ensure_ascii=False))
        m = load_module(rp)
        t = write(tmp, "t6.json", tree([("surface:6", "개발본부장", "ttys008"),
                                        ("surface:7", "홈페이지·이메일협력기관-Claude", "ttys036")]))
        rows = m.read_tree(str(t))
        f = m.audit(rows, {"ttys008"})
        check("DRIFT 검출", states(f).get("개발본부장") == "DRIFT", states(f))
        check("오배송 위험 문구 포함", "오배송 위험" in [x[4] for x in f][0])
        m.fix(f)
        check("--fix가 s6으로 교정", json.loads(rp.read_text())["개발본부장"] == "surface:6")
        check("교정 후 재감사 OK", states(m.audit(rows, {"ttys008"})).get("개발본부장") == "OK")

        # ---------- 7. codex 지정: 동시 writer (lost update / 절단 JSON) ----------
        print("7. 동시 writer — lock + 원자 publish")
        rp = tmp / "r7.json"
        rp.write_text(json.dumps({"seed": "surface:1", "_note": "보존되어야 함"}, ensure_ascii=False))
        env = {**os.environ, "ROSTER_PATH": str(rp)}
        procs = [subprocess.Popen([sys.executable, str(MOD_PATH), "--set", f"role{i}", f"surface:{20+i}"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
                 for i in range(8)]
        rcs = [p.wait() for p in procs]
        check("동시 --set 8건 전부 성공", all(r == 0 for r in rcs), rcs)
        d = json.loads(rp.read_text())          # 파싱 성공 자체가 절단 JSON 부재 증명
        check("lost update 없음(8건 전량 반영)", all(d.get(f"role{i}") == f"surface:{20+i}" for i in range(8)),
              {k: v for k, v in d.items() if k.startswith("role")})
        check("기존 키 보존", d.get("seed") == "surface:1" and d.get("_note") == "보존되어야 함")
        check("임시파일 잔재 없음", not list(rp.parent.glob(".roster.*.tmp")))

        # ---------- 8. ref 형식 검증(bare 숫자 금지) ----------
        print("8. --set ref 형식 강제")
        r = subprocess.run([sys.executable, str(MOD_PATH), "--set", "role9", "3"],
                           capture_output=True, text=True, env=env)
        check("bare 숫자 거부(exit 2)", r.returncode == 2, f"rc={r.returncode}")
        check("거부 시 로스터 무변경", "role9" not in json.loads(rp.read_text()))

        # ---------- 9. --resolve 계약(boot_tower가 의존하는 단일 matcher) ----------
        print("9. --resolve 종료코드 계약")
        rp = tmp / "r9.json"; rp.write_text("{}")
        env9 = {**os.environ, "ROSTER_PATH": str(rp)}
        t_ok = write(tmp, "t9a.json", tree([("surface:2", "COO", "ttys002")]))
        t_amb = write(tmp, "t9b.json", tree([("surface:2", "COO-보조", "ttys002")]))
        t_abs = write(tmp, "t9c.json", tree([("surface:9", "무관탭", "ttys099")]))
        r = subprocess.run([sys.executable, str(MOD_PATH), "--resolve", "COO", "--tree-json", str(t_ok)],
                           capture_output=True, text=True, env=env9)
        check("확정 -> rc0 + ref 출력", r.returncode == 0 and r.stdout.strip() == "surface:2", f"rc={r.returncode} out={r.stdout!r}")
        r = subprocess.run([sys.executable, str(MOD_PATH), "--resolve", "COO", "--tree-json", str(t_amb)],
                           capture_output=True, text=True, env=env9)
        check("부분일치 -> rc3(AMBIGUOUS)·주소 미출력", r.returncode == 3 and not r.stdout.strip(), f"rc={r.returncode} out={r.stdout!r}")
        r = subprocess.run([sys.executable, str(MOD_PATH), "--resolve", "COO", "--tree-json", str(t_abs)],
                           capture_output=True, text=True, env=env9)
        check("부재 -> rc4(소환 허용)", r.returncode == 4 and not r.stdout.strip(), f"rc={r.returncode}")
        r = subprocess.run([sys.executable, str(MOD_PATH), "--resolve", "COO", "--tree-json", str(tmp / "nope.json")],
                           capture_output=True, text=True, env=env9)
        check("tree 실패 -> rc2(내부오류)", r.returncode == 2, f"rc={r.returncode}")

    print(f"\n결과: PASS {len(PASS)} / FAIL {len(FAIL)}")
    if FAIL:
        print("실패 항목: " + ", ".join(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
