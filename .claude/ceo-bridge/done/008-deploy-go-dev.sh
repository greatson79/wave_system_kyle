#!/bin/sh
# 주인님 배포승인 → 개발본부 집행 통지 + COO 통보
cmux send --workspace workspace:3 --surface surface:7 "[CEO→개발본부] ★주인님 배포 승인 수신(CSO 릴레이 원문). 목 흐름아티클 배포 집행하라(지정 집행자=개발 단독 1회): ①커밋 ②cd blog && vercel --prod ③Aliased 확인 후 라이브 실측(아티클 URL 200·h1·면책배너 렌더) ④완료 보고=COO(ws1/s54)+CEO 탭 push(실게시 URL·커밋 해시 포함). 주의: 이 1건만 집행·추가 변경 금지·서버 미종료 금지."
cmux send-key --workspace workspace:3 --surface surface:7 enter
cmux send --workspace workspace:1 --surface surface:54 "[CEO→COO] 주인님 배포 승인 수신 — 개발(ws3/s7)에 집행 통지 완료(커밋+--prod+라이브 실측+보고). 완료 push 취합 후 CEO 상신 바람."
cmux send-key --workspace workspace:1 --surface surface:54 enter
