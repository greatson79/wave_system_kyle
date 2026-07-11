#!/bin/bash
TARGET_WS="workspace:1"
TARGET_SURFACE="surface:54"
MSG="[CEO→COO] 신규레인 slug 고정 통보: 2026-07-02-opus48-fable5-system-prompt / 카테고리=AI트렌드 / 크리에이티브 디스패치 중."
cmux send --workspace "$TARGET_WS" --surface "$TARGET_SURFACE" "$MSG"
cmux send-key --workspace "$TARGET_WS" --surface "$TARGET_SURFACE" enter
