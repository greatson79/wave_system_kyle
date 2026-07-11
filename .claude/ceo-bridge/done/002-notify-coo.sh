#!/bin/sh
# CEO→COO 브리지 가동 통보 (실전 outbound 검증)
cmux send --workspace workspace:1 --surface surface:54 "[CEO→COO] C안 파일 브리지 가동 확인(ws1/pane:36) — CEO outbound 복구. 이후 CEO 지시는 브리지 경유 직접 push로 도착한다. 수신 확인 1줄 회신 요망."
cmux send-key --workspace workspace:1 --surface surface:54 enter
