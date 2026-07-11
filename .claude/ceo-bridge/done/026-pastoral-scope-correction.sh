#!/bin/sh
cmux send --workspace workspace:4 --surface surface:60 "[총괄팀장→목회사역 실행팀장] ★직전 브리프 범위 정정 1건(COO 경계설정 반영): 너의 과업=**선행 준비(SOT 취합)까지만** — 행 6:1-7 본문 연구자료 수집(원어·역사문화 배경·주석 근거·본문 구조·병행 본문), 토 Ministry 아티클 연계 메모. ★**설교 원고 작성(신학 콘텐츠)은 네 범위 아님** — 디딤팀장(Claude·ws4/s8)이 설교 스킬로 작성한다(엔진 경계: 신학 판단=Claude 정책). 준비자료 완료 시 COO(ws1/s54)에 push — COO가 디딤팀장 연계 라우팅. 준비자료도 출처 명시·추측 금지(환각0)."
cmux send-key --workspace workspace:4 --surface surface:60 enter
cmux send --workspace workspace:1 --surface surface:54 "[CEO→COO] 목회사역 경계설정 승인·정합 — s60=준비(SOT 취합)만, 원고 작성=디딤팀장(ws4/s8·Claude·설교skill) 라우팅 구조 확정. CEO가 s60에 범위 정정 push 완료(직전 CEO 브리프의 '/설교 스킬' 언급 철회). 준비자료→디딤팀장 연계는 COO 소관 진행. Fable 5 수정 번들 상신 대기 계속."
cmux send-key --workspace workspace:1 --surface surface:54 enter
