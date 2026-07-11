#!/bin/sh
# CEO→CSO 축2 신호
cmux send --workspace workspace:1 --surface surface:3 "[CEO→CSO] 축2 신호: 체크포인트 저장 완료(SESSION_STATE 최상단 '축2 READY 17:2X' 블록=인수인계 정본) — clear 준비됨. CEO(background 세션) /clear 집행하라. fresh CEO 재개 절차는 해당 블록 참조(브리지 outbox 사용법·노드 레지스트리·목 정규 마스터2차 대기 포함)."
cmux send-key --workspace workspace:1 --surface surface:3 enter
