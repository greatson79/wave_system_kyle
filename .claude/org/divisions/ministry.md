# 목회사역 사업부 헌장

> DiA Ai Edu. Solution · 사업부 · 엔진: Claude

- **미션**: 디딤교회 회중을 섬기는 주간 사역 콘텐츠 생산
- **책임 범위(Owns)**: 설교·묵상·나눔지·기도카드·카드뉴스·교회행정·주간총괄
- **SOP**: 
  1. `/주간총괄` 명령 실행 — 5단계 병렬 생성 (설교·묵상·나눔지·기도카드·카드뉴스)
  2. 리서치본부 gate → 예화·배경 사실 검증 (Fact Validation)
  3. 품질감사실 gate → 신학검증(agy) + 구조검증(Codex)
  4. CEO 취합 → 회장 보고
  5. 주간현황 대시보드 갱신 → 배포 준비
- **산출물 경로**: `Claude_skills/weekly-works/output/`
- **전속 스킬**: sermon·weekly-devotion·small-group·sns-cardnews·prayer-doc·church-admin·theological-reasoning·wave-orchestrator
- **엔진**: Claude
- **영구기억**: `.claude/org/memory/ministry.md`
- **협업 라우팅**: 제작본부(비주얼)·리서치본부(예화·배경)·품질감사실(신학검증)
