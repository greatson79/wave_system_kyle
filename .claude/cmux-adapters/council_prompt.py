#!/usr/bin/env python3
"""3엔진 협의 배치 티켓 생성기 (MASTER_DIRECTIVE §7 "3엔진 협의 배치" 집행 도구 · 2026-07-10).

중량급 작업의 본부장·실행 모델 배치를 Codex·Claude·제미나이 협의로 정할 때, 각 엔진에
보낼 협의 티켓을 생성한다. 교차 평가 강제 + 성과 대장 참조 + CEO 결재 안내를 자동 주입.

사용: council_prompt.py --task "<작업 설명>" --candidates "<후보 나열>" [--ledger <대장 경로>]
출력: 3엔진 공용 협의 티켓 본문 (각 엔진 pane에 전송용)
"""
import argparse
from pathlib import Path

DEFAULT_LEDGER = "/Users/kylechoi/Desktop/Ai_works/output/DiA/경영본부/_round/엔진성과대장.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, help="배치를 정할 중량급 작업 설명")
    ap.add_argument("--candidates", required=True, help="후보 엔진·모델 나열 (예: 'Sonnet5, Opus4.8, codex, agy')")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    a = ap.parse_args()

    ledger = Path(a.ledger)
    ledger_note = f"성과 대장({a.ledger})을 읽고 근거로 삼아라" if ledger.exists() else "성과 대장 부재 — 근거는 공개된 능력 프로파일로 한정하고 추정임을 명시하라"

    print(f"""[3엔진 협의 — 본부장·실행 모델 배치 자문] (MASTER_DIRECTIVE §7 프로토콜)
작업: {a.task}
후보: {a.candidates}

너의 임무: 이 작업의 본부장(지휘)·실행 모델 배치를 추천하라.
규칙(위반 금지):
1. ★교차 평가 강제: 후보 전원을 평가하라 — 자기 벤더(계열) 후보만 추천하는 것 금지.
   자기 계열의 약점도 정직하게 기재하라(정직 라벨링).
2. 근거 결정론화: {ledger_note}. 근거 없는 인상 추천 금지.
3. 출력 형식: {{추천 본부장: <엔진·모델>, 추천 실행: <엔진·모델>, 근거: <대장 행 또는 사실 3줄 이내>,
   자기 계열 약점: <1줄>, 확신도: High/Med/Low}}
4. 이것은 자문이다 — 결정·책임은 CEO 결재. 불일치 시 1라운드 상호 반박 후 CEO가 결착한다
   (다수결 아님). 회신은 의뢰 티켓에 명시된 주소로 push하라.""")


if __name__ == "__main__":
    main()
