#!/usr/bin/env python3
"""cmux 위임 티켓 생성기 (cys javis_orchestra task-prompt의 cmux 대체 — 2026-07-10 체제 전환).

계약(cys판과 동일): ①위임 직전 대상 워커 생존을 결정론 확인(미발견/모호 = 티켓 미출력)
②절대 강조 4규칙(엔진 WORKER §3)을 모든 티켓에 자동 주입 ③보고 채널(--workspace+--surface
병기 + enter 필수)을 티켓에 명시. 수기 티켓 위임 금지의 집행 도구.

사용: cmux_task_prompt.py --to <역할|탭명> --task "<T>" --scope "<범위>" --success "<성공 기준>" [--source-sot <원천 SOT 경로>]
★원천 SOT 규율(2026-07-27 CEO): 위임티켓은 SOT가 아니다 — 원천(노션 기획·시리즈 스펙 등)에
  스코프 구조가 있으면 티켓에 없어도 원천이 이긴다. --source-sot로 원천 경로를 명시하고, 미지정 시
  티켓에 "착수 전 원천 선확인" 경고가 자동 주입된다. (codex sites 시리즈 스코프 사고 재발방지)
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

DIFF_ONLY_CLAUSE = """[★DIFF-ONLY 위임 — envscan R6 절차위반 재발방지 (2026-07-21 CEO 승인)]
이 위임은 "diff 산출"이 목적이다 — 라이브 파일 직접수정 금지.
①대상 파일을 스테이징 사본(예: 원본과 분리된 임시 디렉토리 또는 .bak-<timestamp>)으로 복사한 뒤
  그 사본에서만 작업한다. 원본은 위임 완료·CEO 확정 전까지 변경되지 않아야 한다.
②완료보고에 방식을 명시한다 — "방식=스테이징"(원본 불변) 또는 부득이 "방식=라이브직접수정"
  (원본이 실제로 바뀐 경우) 중 하나를 반드시 밝힌다. 은폐 금지 — 확실하지 않으면 즉시 질문한다.
③diff 산출물은 원본이 아니라 스테이징 결과와 원본의 비교여야 하며, 위임자가 최종 확정하기
  전까지 원본 파일이 실행 경로(cron 등)에서 살아있는 상태로 남아있지 않게 주의한다."""


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
    ap.add_argument("--diff-only", action="store_true",
                     help="위임이 diff 산출 전용임을 명시 — 라이브 파일 직접수정 금지 조항을 티켓에 주입")
    ap.add_argument("--source-sot", default="",
                     help="원천 SOT 경로(노션 기획·시리즈 스펙·리서치 정본 등). 미지정 시 착수 전 원천 선확인 경고를 티켓에 주입")
    a = ap.parse_args()

    addr = resolve(a.to)
    ws, sf = addr["workspace"], addr["surface"]

    diff_only_block = f"\n\n{DIFF_ONLY_CLAUSE}" if a.diff_only else ""

    if a.source_sot:
        sot_line = (f"원천 SOT(★위임티켓보다 우선 — 착수 전 필독): {a.source_sot}\n"
                    "  이 원천에 시리즈/부분/스코프 구조가 있으면 티켓 문구가 아니라 원천이 이긴다.")
    else:
        sot_line = ("원천 SOT: 미지정 — ★착수 전 원천(노션 기획·시리즈 스펙·리서치 정본 등) 존재 여부를 반드시 확인.\n"
                    "  ★위임티켓은 SOT가 아니다 — 원천에 스코프 구조가 있으면 티켓에 없어도 원천이 이긴다.\n"
                    "  원천 불명·해석 갈림 시 착수 전 발주자에 질의(티켓만 보고 백지 제작 금지). [2026-07-27 CEO 규율]")

    ticket = f"""[위임 티켓 → {a.to} ({ws} {sf})]
과업: {a.task}
범위(이 범위만 — 무관 파일·repo 배회 금지): {a.scope}
{sot_line}
성공 기준: {a.success}

{FOUR_RULES}{diff_only_block}

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
