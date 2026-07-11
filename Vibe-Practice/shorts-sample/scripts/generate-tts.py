#!/usr/bin/env python3
"""
숏츠 TTS 생성 스크립트
sermon-context.md → 숏츠 스크립트 → edge-tts 음성 파일
"""

import asyncio
import json
import os
import sys

# edge-tts
try:
    import edge_tts
except ImportError:
    print("edge-tts가 설치되지 않았습니다: pip install edge-tts")
    sys.exit(1)

# ── 숏츠 스크립트 (17주차 설교 기반) ──────────────────────
SHORTS_SCRIPT = """
충분히 해냈다는 느낌, 당신은 받아본 적 있습니까?

우리는 끊임없이 무언가를 쌓습니다.
직장에서, 가정에서, 교회에서.
그 목록이 든든할수록 더 안전하다고 느낍니다.

바울도 완벽한 이력서를 가진 사람이었습니다.
그런데 그는 그것을 배설물이라고 불렀습니다.
더 나은 것을 발견했기 때문입니다.

복음은 더 열심히 쌓으라는 말이 아닙니다.
출처가 바뀌었다는 선언입니다.

내가 충분히 해냈는지 증명하지 않아도 되는 사람으로
이미 받아들여졌습니다.

오늘 마음속 이력서를 내려놓으십시오.
강요가 아닙니다. 초청입니다.

디딤교회에서 함께 만나요.
"""

VOICE = "ko-KR-InJoonNeural"
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "public", "narration.mp3"
)
TIMING_PATH = os.path.join(
    os.path.dirname(__file__), "..", "public", "timing.json"
)


async def generate_tts():
    print(f"음성 생성 중... ({VOICE})")

    communicate = edge_tts.Communicate(
        SHORTS_SCRIPT.strip(),
        VOICE,
        rate="-5%",   # 설교 톤에 맞게 약간 느리게
        pitch="-3Hz", # 차분한 톤
    )

    # 자막 타이밍 수집
    timings = []
    with open(OUTPUT_PATH, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                timings.append({
                    "word": chunk["text"],
                    "offset_ms": chunk["offset"] / 10000,  # 100ns → ms
                    "duration_ms": chunk["duration"] / 10000,
                })

    # 타이밍 저장
    with open(TIMING_PATH, "w", encoding="utf-8") as f:
        json.dump(timings, f, ensure_ascii=False, indent=2)

    print(f"✅ 음성 저장: {OUTPUT_PATH}")
    print(f"✅ 타이밍 저장: {TIMING_PATH}")
    print(f"   단어 수: {len(timings)}")

    # 총 길이 계산
    if timings:
        last = timings[-1]
        total_ms = last["offset_ms"] + last["duration_ms"]
        print(f"   총 길이: {total_ms/1000:.1f}초")
        return total_ms / 1000
    return 60.0


if __name__ == "__main__":
    duration = asyncio.run(generate_tts())
    print(f"\n→ Remotion durationInFrames: {int(duration * 30)} (30fps 기준)")
