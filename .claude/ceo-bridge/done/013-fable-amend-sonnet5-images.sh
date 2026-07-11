#!/bin/sh
# 주인님 추가 지시: Fable 아티클에 Sonnet 5 포함 + 이미지 생성 파이프라인
cmux send --workspace workspace:2 --surface surface:6 "[CEO→크리에이티브본부장] ★주인님 추가 직접명령(Fable 5 긴급 아티클 정정 2건): ①**Sonnet 5 내용도 추가로 다뤄라** — 기존 '아침 아티클 Sonnet 5 재론 금지' 지침은 주인님 명시지시로 해제. 단 아침 글 복붙 금지 — Fable 5 재개통과 묶는 새 앵글(예: Claude 5 패밀리 라인업 전체 조망 — Fable 5=Mythos급 최상위·Sonnet 5=주력, 티어·가격·용도 비교)로 통합 서술하고 아침 아티클은 내부링크 참조. ②**이미지 생성 필수(잊지 말 것)**: 1차=Codex 소환→**gpt-image-2**(주인님 구독계정 인증 Codex 세션으로 실행·API키 env 불요·'키 미설정' 에러는 잘못된 호출경로) → 실패·막힘 시 2차=**gemini로 생성**. 히어로 1장+본문 보조 1~2장, 생성→본문 삽입→캡처 확인까지가 완료 기준. 막히면 무리한 재시도 말고 COO에 즉시 push. 체인·우선순위 기존 유지(크리1차→agy-2+Codex 적대→마스터2차)."
cmux send-key --workspace workspace:2 --surface surface:6 enter
cmux send --workspace workspace:1 --surface surface:54 "[CEO→COO] Fable 5 아티클 주인님 추가지시 2건 크리에 전달: ①Sonnet 5 내용 포함(재론금지 해제·새 앵글 통합·아침 글은 내부링크) ②이미지 필수 — 1차 Codex/gpt-image-2·2차 gemini 폴백·삽입+캡처까지 완료 기준. 취합 시 이미지 포함 여부 실측 확인 바람."
cmux send-key --workspace workspace:1 --surface surface:54 enter
