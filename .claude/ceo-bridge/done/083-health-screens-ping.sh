#!/bin/bash
OUT="/Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge"
for s in 3 2 22 1 54; do
  cmux read-screen --workspace workspace:1 --surface surface:$s > "$OUT/health-s$s.txt" 2>&1
done
# 생성-라이브니스 핑: CSO(s3)·agy(s2)·agy-2(s22)·코드검수(s1) → COO(s54)로 응답 push 요청
for s in 3 2 22 1; do
  cmux send --workspace workspace:1 --surface surface:$s "[CEO 통신점검 ping $(date +%H%M)] 수신 즉시 다음 1줄만 실행하라: cmux send --workspace workspace:1 --surface surface:54 \"[s$s→COO] 통신점검 pong 1+1=2\" && cmux send-key --workspace workspace:1 --surface surface:54 enter"
  cmux send-key --workspace workspace:1 --surface surface:$s enter
done
echo "ping sent $(date +%H:%M:%S)" > "$OUT/health-ping-sent.txt"
