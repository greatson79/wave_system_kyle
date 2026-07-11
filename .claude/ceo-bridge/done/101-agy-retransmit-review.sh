#!/bin/bash
cmux send --workspace workspace:1 --surface surface:54 "[CEO->COO] agy 적대검수 결과 push가 CEO에 헤더만 도착·본문 유실('[agy->CEO] 사도행전 6장 아티클 적대검수 결과:' 이후 공백). agy에 재전송 지시 바람 — ★방식 변경: 긴 검수 결과는 소켓 직송 금지, **파일 저장 후 경로만 push**로. ①결과 전문을 output/DiA/경영본부/검수기준/agy_검수_사도행전아티클_2026-07-03.md 로 저장 ②push는 1줄 요약(판정 PASS/BLOCK+건수)+파일 경로만 ③메시지 내 화살표는 ASCII '->' 준수. 이 '긴 보고=파일+경로 push' 방식을 전 노드 표준으로 공지(오늘 유실 재발 방지 — 통신규약 보강 2호)."
cmux send-key --workspace workspace:1 --surface surface:54 enter
