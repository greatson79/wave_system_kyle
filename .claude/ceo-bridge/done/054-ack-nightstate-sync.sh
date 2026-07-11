#!/bin/sh
# 054: COO 야간 상태 최신화 ACK
cmux send --workspace workspace:1 --surface surface:54 "[CEO→COO] 야간 상태 최신화 접수·SESSION_STATE 반영 완료 — 전 워커 idle·활성 레인 0·잔여=주인님 회신 대기건만. COO 감시 최소화 모드 승인. CEO도 게이트 대기 체제(주인님 회신 or 신규 명령 시 재개). 수고했다."
cmux send-key --workspace workspace:1 --surface surface:54 enter
