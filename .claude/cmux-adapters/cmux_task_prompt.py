#!/usr/bin/env python3
"""cmux 위임 티켓 생성기 (cys javis_orchestra task-prompt의 cmux 대체 — 2026-07-10 체제 전환).

계약(cys판과 동일): ①위임 직전 대상 워커 생존을 결정론 확인(미발견/모호 = 티켓 미출력)
②절대 강조 4규칙(엔진 WORKER §3)을 모든 티켓에 자동 주입 ③보고 채널(--workspace+--surface
병기 + enter 필수)을 티켓에 명시. 수기 티켓 위임 금지의 집행 도구.

사용: cmux_task_prompt.py --to <역할|탭명> --task "<T>" --scope "<범위>" --success "<성공 기준>"
출력: 전송용 티켓 본문 + 전송 명령 2줄(send / send-key enter).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

CMUX = "/Applications/cmux.app/Contents/Resources/bin/cmux"
ADDR = Path(__file__).parent / "cmux_addr.py"

FOUR_RULES = """[절대 강조 4규칙 — 모든 작업 티켓 공통 (엔진 WORKER §3)]
a) 품질 절대우선: 조사의 깊이·폭·정확도가 절대 기준. 속도·토큰·편의는 이유가 될 수 없다.
b) 할루시네이션 방지: 출처·근거·논리오류 분석·팩트체크 필수 작업엔 전담 sub-skill
   (hallucination-guard)을 사용해 검증 엄밀성·환각 안전장치를 확보한다. 과장·거짓 확신 금지.
   Garbage-in 차단 — 토대가 오염되면 아무리 다듬어도 거짓만 정교해진다.
c) 의도 합의: 지시 의도 파악이 불충분하면 추측 진행 금지 — 합의에 이를 때까지 질문을 반복한다.
d) 요약·압축 절대 금지: 최종 결과물은 모든 분석·수치·표·단서를 하나도 빠뜨리지 않는다.
   전문용어만 쉬운 말로 풀고 길이는 원문 수준 유지.
게이트: b가 흔들리면 나머지 실행을 중단하고 보고한다. 완료·질문·충돌·막힘은 즉시 push 보고."""


def resolve(target):
    out = subprocess.run([sys.executable, str(ADDR), target, "--json"], capture_output=True, text=True)
    if out.returncode != 0:
        sys.stderr.write(out.stderr)
        sys.stderr.write("[task-prompt] 워커 생존 미확인 — 티켓을 출력하지 않는다. 워커 정상 작동 확인 후 재시도.\n")
        sys.exit(out.returncode)
    return json.loads(out.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--scope", required=True)
    ap.add_argument("--success", required=True)
    ap.add_argument("--reply-to", default="master")
    a = ap.parse_args()

    addr = resolve(a.to)
    ws, sf = addr["workspace"], addr["surface"]

    ticket = f"""[위임 티켓 → {a.to} ({ws} {sf})]
과업: {a.task}
범위(이 범위만 — 무관 파일·repo 배회 금지): {a.scope}
성공 기준: {a.success}

{FOUR_RULES}

보고 채널(주소 회전 대비 — 보고 직전 재해소): python3 {ADDR} "{a.reply_to}" 로 현재 주소를 얻어
  cmux send --workspace <ws> --surface <sf> "[{a.to}->{a.reply_to}] <보고>" 실행 후
  cmux send-key --workspace <ws> --surface <sf> enter  (enter 없으면 미실행)
todo: 받은 task를 즉시 md todo로 분해·디스크 영속(세션 재시작 복원용), 세부 완료마다 갱신."""

    print(ticket)
    print("\n--- 전송 명령 (생성 즉시 같은 턴에서 전송하라) ---")
    print(f'{CMUX} send --workspace {ws} --surface {sf} -- "$(cat <<\'TICKET_EOF\'\n{ticket}\nTICKET_EOF\n)"')
    print(f"{CMUX} send-key --workspace {ws} --surface {sf} enter")


if __name__ == "__main__":
    main()
