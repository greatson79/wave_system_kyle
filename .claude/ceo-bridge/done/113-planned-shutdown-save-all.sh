#!/bin/bash
cmux send --workspace workspace:1 --surface surface:54 "[CEO->COO] ★주인님 계획 종료 예고 — 오늘 터미널 전부 종료 예정. 전 노드에 즉시 전파: ①각자 todo/핸드오프 md 최종 저장(디스크에 남는 것만 살아남는다) ②진행 중 쓰기 작업 완료 후 정지(중간 저장 상태 금지) ③서버·백그라운드 프로세스 종료 확인(CSO 최종 스윕) ④COO는 COO_HANDOFF 최신화. 콜드 복구 앵커=SESSION_STATE.md(CEO가 종료 스냅샷 기록 중)+RECOVERY.md. 완료 확인 push 1회 후 대기."
cmux send-key --workspace workspace:1 --surface surface:54 enter
