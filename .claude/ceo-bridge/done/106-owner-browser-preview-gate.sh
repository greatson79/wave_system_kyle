#!/bin/bash
cmux send --workspace workspace:1 --surface surface:54 "[CEO->COO] ★주인님 지시 — 개발본부에 전달: **Ministry 아티클은 프로덕션 발행 전 주인님 브라우저 확인 게이트 추가**. 집행 방식: ①검수 체인(목회사역본부장->agy재검->마스터2차) 통과 후 커밋하되 **vercel --prod 금지** ②대신 **프리뷰 배포**(vercel 프리뷰 URL — noindex·비색인 확인) 또는 로컬 프리뷰 서버(사용 후 반드시 kill·서버 생명주기 규칙) 중 개발 판단으로 준비 ③프리뷰 URL을 주인님께 보고(CEO 경유) -> **주인님 브라우저 확인·GO 회신 후에만 vercel --prod 집행** ④이 게이트는 이번 아티클에 즉시 적용, 상설 여부는 주인님 후속 지시 대기. 기존 '적대검수 통과=커밋+발행 준비' 지시는 '커밋+프리뷰 준비'로 갱신."
cmux send-key --workspace workspace:1 --surface surface:54 enter
