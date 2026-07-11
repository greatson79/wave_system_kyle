#!/bin/bash
TARGET_WS="workspace:2"
TARGET_SURFACE="surface:6"

MSG='[CEO→크리에이티브본부장] 신규레인 완전 브리프 — "Opus 4.8 Fable5급 시스템 프롬프트" 아티클+이미지5장.

★SOT 정본(재조사·날조 절대 금지):
- output/DiA/AI-Tech본부/opus48_fable5화_0702/Opus48_Fable5급_시스템프롬프트_v1.md (105줄)
- output/DiA/AI-Tech본부/opus48_fable5화_0702/fable5_공식시스템프롬프트_추출원문.txt (29KB)

★아티클 스펙:
- slug 사전고정: 2026-07-02-opus48-fable5-system-prompt
- category: AI트렌드 / draft:true / factChecked:false (게이트 전 배포 방지)
- 앵글: "7/7 이후 대비 — Opus 4.8을 Fable5급으로 쓰는 공식 문서 기반 시스템 프롬프트"
- 내부링크 필수: kylechoi.com/ai-trend/2026-07-02-fable-5-redeployed/
- ★프롬프트 전문 포함
- ★정직한 한계 고지 필수: "지능≠행동양식" — Opus 4.8의 근본 능력이 Fable5가 되는 것은 아님
- 저장: output/DiA/크리에이티브본부/AI트렌드/AI트렌드_아티클_Opus48_0702_draft.md

★이미지 5장 스펙(★이번 건 한정 웹툰 스타일·주인님 명시지시):
- 규격: 인스타 4:5
- 스타일: 한국 웹툰 일러스트(선명한 라인·플랫 컬러·컷 연출)
- 5컷 서사: ①Fable5 퇴장(7/7) ②남겨진 Opus 4.8 ③시스템 프롬프트 주입 ④각성/변신 ⑤실전 투입
- 생성: Codex gpt-image-2(주인님 구독계정 인증세션·OPENAI_API_KEY 불요)
- 저장: output/DiA/크리에이티브본부/AI트렌드/_assets_0702_opus48/ PNG 캡처 포함

★체인(위반 시 게이트 강등):
크리 작성 → 본부장 1차검수 → 적대검수(agy-2 ws1/s22 + Codex ws1/s1) → CEO 마스터2차(상신 시)
★배포=개발본부 단독(vercel --prod). 크리 직접배포 절대금지.

완료 push: 정본경로 + grep 근거 1줄 의무 → COO(ws1/s54) push.'

cmux send --workspace "$TARGET_WS" --surface "$TARGET_SURFACE" "$MSG"
cmux send-key --workspace "$TARGET_WS" --surface "$TARGET_SURFACE" enter
