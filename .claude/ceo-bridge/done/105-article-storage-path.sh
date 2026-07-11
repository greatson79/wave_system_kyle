#!/bin/bash
cmux send --workspace workspace:1 --surface surface:54 "[CEO->COO] ★주인님 지시 — 사도행전 Ministry 아티클 레인 산출물 정본 저장경로 = **output/DiA/목회사역-디딤/주간콘텐츠팀/** (폴더 기존재 확인). 디딤에 전달: ①아티클 md 정본 사본(blog repo 커밋과 별개로 내부 정본 1부) ②style6 이미지 3장 원본 ③검수 기록(agy 4건 대응표·목회사역본부장 검수 소견·Codex 결과 요약) ④발행 기록(커밋 해시·라이브 URL) 전부 이 폴더에. 기존 산출물 중 타 위치 저장분(예: 경영본부/검수기준의 agy 검수 파일)은 원본 유지+이 폴더에 사본 배치(레인 완결 시 한 폴더에서 전모 파악 가능하게). 향후 주간 콘텐츠 계열 아티클 산출물도 동일 경로 원칙."
cmux send-key --workspace workspace:1 --surface surface:54 enter
