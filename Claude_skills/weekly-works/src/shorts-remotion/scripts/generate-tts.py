#!/usr/bin/env python3
"""
씬별 TTS 생성 → 정확한 타이밍 계산
각 씬의 나레이션을 개별 mp3로 생성 → 실제 길이 측정 → timing.json 생성
사용법: python3 generate-tts.py <script.json> <output_dir>
"""

import asyncio
import json
import os
import sys
import subprocess

try:
    import edge_tts
except ImportError:
    os.system("pip install edge-tts -q")
    import edge_tts

try:
    from mutagen.mp3 import MP3
except ImportError:
    os.system("pip install mutagen -q")
    from mutagen.mp3 import MP3

VOICE = "ko-KR-InJoonNeural"
FPS = 30


async def generate_scene_audio(text: str, output_path: str):
    """씬 하나의 나레이션을 mp3로 생성"""
    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate="-5%",
        pitch="-3Hz",
    )
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])

    duration = MP3(output_path).info.length
    return duration


async def generate(script_path: str, output_dir: str):
    with open(script_path, encoding="utf-8") as f:
        config = json.load(f)

    scenes = config["scenes"]
    scene_audio_dir = os.path.join(output_dir, "scene-audio")
    os.makedirs(scene_audio_dir, exist_ok=True)

    print(f"씬별 TTS 생성 중... ({VOICE})")
    timing_scenes = []
    frame_cursor = 0

    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "").strip()
        if not narration:
            # 나레이션 없는 씬 (CTA 등) — 고정 5초
            duration_sec = 5.0
            audio_file = None
        else:
            audio_file = os.path.join(scene_audio_dir, f"scene_{i:02d}_{scene['id']}.mp3")
            print(f"  [{i+1}/{len(scenes)}] {scene['id']}: 생성 중...")
            duration_sec = await generate_scene_audio(narration, audio_file)
            print(f"           → {duration_sec:.2f}초")

        frames = int(duration_sec * FPS)
        timing_scenes.append({
            "id": scene["id"],
            "label": scene.get("label", ""),
            "text": scene.get("text", ""),
            "color": scene.get("color", "#ffffff"),
            "fromFrame": frame_cursor,
            "durationInFrames": frames,
            "audioFile": f"scene-audio/scene_{i:02d}_{scene['id']}.mp3" if audio_file else None,
            "durationSec": duration_sec,
        })
        frame_cursor += frames

    # 씬별 오디오를 하나로 합치기 (ffmpeg 사용 가능 시)
    narration_path = os.path.join(output_dir, "narration.mp3")
    audio_files = [s["audioFile"] for s in timing_scenes if s["audioFile"]]

    if audio_files:
        _concat_audio(
            [os.path.join(output_dir, f) for f in audio_files],
            narration_path
        )

    # timing.json 저장
    timing_path = os.path.join(output_dir, "timing.json")
    timing_data = {
        "totalFrames": frame_cursor,
        "totalDurationSec": frame_cursor / FPS,
        "fps": FPS,
        "scenes": timing_scenes,
    }
    with open(timing_path, "w", encoding="utf-8") as f:
        json.dump(timing_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ narration.mp3 → {narration_path}")
    print(f"✅ timing.json  → {timing_path}")
    print(f"   총 길이: {frame_cursor/FPS:.1f}초 ({frame_cursor} 프레임)")


def _concat_audio(files: list, output: str):
    """씬별 오디오 파일을 순서대로 합치기"""
    try:
        # ffmpeg 방식
        list_file = output + ".list.txt"
        with open(list_file, "w") as f:
            for fp in files:
                f.write(f"file '{fp}'\n")
        result = subprocess.run(
            ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file,
             "-c", "copy", output, "-y", "-loglevel", "quiet"],
            capture_output=True
        )
        os.remove(list_file)
        if result.returncode == 0:
            print("   오디오 합치기 완료 (ffmpeg)")
            return
    except FileNotFoundError:
        pass

    # ffmpeg 없으면 pydub 시도
    try:
        from pydub import AudioSegment
        combined = AudioSegment.empty()
        for fp in files:
            combined += AudioSegment.from_mp3(fp)
        combined.export(output, format="mp3")
        print("   오디오 합치기 완료 (pydub)")
        return
    except ImportError:
        pass

    # 둘 다 없으면 첫 번째 파일만 복사 (fallback)
    import shutil
    shutil.copy(files[0], output)
    print("   ⚠️ ffmpeg/pydub 없음 — 첫 번째 씬 오디오만 사용")
    print("   → ffmpeg 설치 권장: brew install ffmpeg")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python3 generate-tts.py <script.json> <output_dir>")
        sys.exit(1)
    asyncio.run(generate(sys.argv[1], sys.argv[2]))
