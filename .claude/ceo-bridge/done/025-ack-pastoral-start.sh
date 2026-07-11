#!/bin/sh
cmux send --workspace workspace:4 --surface surface:60 "[총괄팀장→목회사역 실행팀장] 직접명령 보고 ACK(프로토콜 정합) — 착수 승인. 과업 범위: ①내일(금) 설교 원고 확정 선행 준비 — 본문 **사도행전 6:1-7**, /설교 스킬(sermon SKILL·Mode 판단은 본문 구조 분석 후)+개혁주의 강해 원칙·theological-reasoning 검증 필수 ②토 Ministry 아티클 연계 구조 미리 고려(금 확정 원고→토 아티클 재작성 체인). 가드: 신학적 정확성 최우선·환각0·출처(주석·원어) 근거 명시·주인님(담임목사) 확정 게이트=금요일. 산출물 위치=output/DiA/목회사역-디딤/ 하위+SESSION_STATE 표시. 완료·질문은 COO(ws1/s54) 취합·중요 게이트만 CEO push. WORKER_DIRECTIVE 1(서버 최소화)·3(품질)·4(실측) 준수."
cmux send-key --workspace workspace:4 --surface surface:60 enter
cmux send --workspace workspace:1 --surface surface:54 "[CEO→COO] 목회사역 s60 과업 확정 통보: 주인님 직접명령=금 설교(행 6:1-7) 선행 준비+토 Ministry 연계. CEO 착수 승인·브리프 발령 완료. 운영 취합 큐에 포함 바람."
cmux send-key --workspace workspace:1 --surface surface:54 enter
