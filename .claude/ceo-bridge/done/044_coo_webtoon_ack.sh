#!/bin/sh
# COO(ws1/s54)에 크리에이티브 착수 보고
MSG="[크리에이티브본부장→COO] Opus48 인스타툰 v2 착수 확인: ①폴더 신설 완료(인스타툰_Opus48_v2_0702/) ②캐릭터 파일 실존 확인(메인캐릭터_3D최종학.png 456KB) ③SNS캡션 패키지 v2 작성 완료(인스타+페북+첫댓글+카톡·URL ai-trend 정합) ④gpt-image-2 생성 스크립트(generate_cuts.py) 준비 ⑤Codex 생성 디스패치(outbox/043) 등록. 야간 bridge 생존 시 자동 실행·미생존 시 내일 아침 Codex 재디스패치. SOT 대사 5컷 전항 확인·캐릭터 일관성 프롬프트 반영. 이미지 완료→한글 OCR 검증→1차 자체→agy-2 적대→마스터2차 체인 진행."

cmux send --workspace 1 --surface 54 "$MSG"
cmux send-key --workspace 1 --surface 54 enter
echo "[044] COO 보고 완료"
