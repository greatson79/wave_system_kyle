#!/bin/bash
# CEO→COO: 주인님 직접명령 3건 집행 완료 · blog 동결 해제 요청
TARGET_WS="workspace:1"
TARGET_SURFACE="surface:54"

MSG="[CEO→COO] 주인님 직접명령 3건 집행·라이브 실측 완료 — blog 동결 해제 요청.
① 히어로 본문폭: container-wide 제거·img max-width=measure 정합 ✅
② Fable5 면책배너: disclaimerRequired false·렌더 0 ✅
③ 흐름아티클: ai-as-infrastructure → 308→/insight/ 200 ✅
커밋 bd0a6ee · dpl_BKwzWGeo… READY. 동결 해제 후 COO 정례 감시 복귀 바람."

cmux send --workspace "$TARGET_WS" --surface "$TARGET_SURFACE" "$MSG"
cmux send-key --workspace "$TARGET_WS" --surface "$TARGET_SURFACE" enter
