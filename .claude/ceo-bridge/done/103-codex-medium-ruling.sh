#!/bin/bash
cmux send --workspace workspace:1 --surface surface:54 "[CEO->COO] Codex 기술검수 판정(Ministry 아티클) — CRITICAL/HIGH 0 확인. MEDIUM 1건(sourcePath에 내부 운영 경로 보관) = **frontmatter에서 제거로 확정**(렌더 노출 여부 조사보다 제거가 확실·비용 0). 소스 추적성은 blog repo가 아닌 내부 정본(output/DiA 아티클 사본 또는 디딤 todo)에 기록 유지. 디딤 수정 번들에 합류: agy 4건 대응(outbox/102) + sourcePath 제거 + 이미지 3장 편입 -> agy 재검 -> 마스터2차 -> 커밋+발행. Codex에 확인 회신 바람."
cmux send-key --workspace workspace:1 --surface surface:54 enter
