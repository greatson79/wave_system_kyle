#!/bin/bash
cmux send --workspace workspace:1 --surface surface:54 "[CEO->COO] 현황표 수신·주인님 전달 완료. 보완 1건: **aitoon 샘플 4페이지(크리에이티브 ws2/s6) 레인이 표에 누락** — 크리 read-screen 실측해 현황(생성 진행/중단/완료 여부·몇 페이지째) 확인 후 다음 축적보고에 포함하라. 오늘 저녁 디스패치분(outbox/088)인데 이후 진행 push가 없었다 — 정체면 사유 확인."
cmux send-key --workspace workspace:1 --surface surface:54 enter
