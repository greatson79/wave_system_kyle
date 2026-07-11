#!/bin/sh
# 주인님 제공 공식공지 스크린샷 전달 → 크리에이티브
cmux send --workspace workspace:2 --surface surface:6 "[CEO→크리에이티브본부장] ★주인님 자료 제공(Fable 5 아티클용): Anthropic 공식 공지 '\''Fable 5가 돌아왔습니다'\'' 스크린샷(1590x1066 PNG) — 경로 output/DiA/크리에이티브본부/AI트렌드/_assets_0702_fable5/fable5_공식공지_스크린샷_주인님제공.png. ①이 이미지를 아티클에 사용하라(주인님 지시 — 공식 공지 스크린샷 인용 프레임·출처 Anthropic 표기. gpt-image-2 생성 이미지와 병행: 스크린샷=공지 인용용, 생성 이미지=히어로 등 나머지) ②스크린샷 안 사실관계=1차 출처로 활용: 7/7까지 플랜 주간 사용한도 최대 50%를 Fable 5에 사용 가능·한도 도달 시 사용 크레딧으로 계속 이용·Fable 5는 Opus 4.8보다 사용량 더 빠르게 소모·'\''더 적은 중간 확인으로 가장 어려운 과제 해결'\''. 아티클 본문에 이 조건들(기간 한정·소모율) 정확 반영하라 — 실무 독자에게 핵심 정보다."
cmux send-key --workspace workspace:2 --surface surface:6 enter
