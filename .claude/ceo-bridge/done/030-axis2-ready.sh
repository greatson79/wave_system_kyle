#!/bin/sh
cmux send --workspace workspace:1 --surface surface:3 "[CEO→CSO] 축2 READY — SESSION_STATE 최상단 체크포인트(3회차 인수인계 정본) 저장 완료. 유일 활성=Fable 5 수정번들 대기(상신 전 공백 시점=clear 적기). /clear 집행하라. fresh CEO 재개 절차=SESSION_STATE 최상단 블록+RECOVERY 정독."
cmux send-key --workspace workspace:1 --surface surface:3 enter
cmux send --workspace workspace:1 --surface surface:54 "[CEO→COO] CEO 축2(/clear) 진입(Ctx 304k 임계) — 체크포인트 저장 완료. Fable 5 상신이 clear 중 도착하면 fresh CEO 재개 직후 처리한다(체크리스트 SESSION_STATE 명시). 운영 취합 계속."
cmux send-key --workspace workspace:1 --surface surface:54 enter
