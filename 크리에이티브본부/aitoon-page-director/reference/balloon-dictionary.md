# 🎈 말풍선 사전 (page-director용) v0.2 — 대사 포함 분기에서 읽는다

> **시점:** 2026-06-28 / **기준 모델:** GPT(나노바나나는 Plan B) / **상태:** 살아있는 문서(갱신 전제)
> **맥락:** 페이지형 컷만화(트랙 A). 페이지는 컷 그리드라 **컷 안 / 컷 걸침** 위주. (세로 빈 띠 규칙은 세로 웹툰 전용 — 여기선 다루지 않음.)
> **이 파일은 대사 포함(말풍선) 분기에서만 읽는다.** 클린 원고 분기는 사용하지 않는다.
> **마스터:** 유지관리 허브 `_말풍선자료/말풍선사전_v0.2.md` = 진실의 원천. 여기 사본은 페이지 맥락 조정본.

---

## 0. 사용법 & 원칙

**누가 읽나 — 너(구름이)다. 너는 말풍선을 그리지 않는다.** 장면 감정 → 아래에서 **이름 고르기** → 그 **GPT 스니펫을 페이지 프롬프트의 해당 컷에 복붙.** 그림은 GPT가 그린다. 해석·번역하지 말고 스니펫을 그대로 가져다 쓴다(이름이 곧 작동 토큰).

- **검증 표기:** `✅` GPT 4판 검증(또는 ep11 실전) · `◐` 일부 보강 필요 · 빈칸 = 미검증.
- **★ 핵심 원칙:**
  - **이름이 형태를 강제** — 이름 속 형태 단어("Spike")는 프롬프트로 못 뺀다. 빼고 싶으면 그 단어 없는 이름을 쓴다.
  - **과분류 금지** — GPT는 비슷한 걸 큰 갈래로 수렴. 감정 라벨(Angry/Rage…)은 형태에 매핑, 따로 항목 안 만든다.
  - **열림 원칙** — 사전은 바닥선(보장)이지 천장(규격) 아님. GPT가 더 나으면 환영, 판단은 유저.
  - **점선구름 = 소심한 혼잣말 전용** / 생각 기본형은 Aura.
  - **클린 원고 역획득** — 완성본→말풍선 제거(원본 비율 유지·말풍선 자체 제거)로 수정 안전망(대사 포함 ↔ 클린 원고를 잇는 다리).

---

## 1. 코어 (범용 — 거의 모든 만화에 쓰임)

### 대사 / 생각
| 이름 | GPT 복붙 스니펫 | 언제 | 검증 |
|------|----------------|------|:---:|
| Normal Speech | `a normal speech balloon (smooth oval, small tail to mouth)` | 평범한 대사(기본) | ✅ |
| Conversational/Soft | `a soft conversational speech balloon (smooth rounded oval)` | 부드러운 대화 | ✅ |
| Hand-Drawn Rough | `a "Hand-Drawn Rough Outline" balloon (wobbly/sketchy uneven outline; TEXT clean sans-serif)` | 더듬·당황 (그 풍선만 거칠게, 전역 clean과 분리) | ✅ |
| Whisper | `a WHISPER balloon (dashed/dotted outline)` | 속삭임 | ✅ |
| Double/Split | `a DOUBLE/SPLIT balloon (one character's line in two linked bubbles, tail on the 2nd to mouth)` | 한 화자 끊어 말하기 | ✅ |
| **Wobble** ⭐ | `a "Wobble Balloon" (wavy/shaky trembling outline)` | 불안·떨리는 목소리 | ✅ |
| Fine Spike Aura | `a "Fine Spike Aura" balloon (oval with a fine thin spiky aura outline, NO tail)` | 미묘한 긴장·깨달음(생각 기본형) | ✅ |
| Fuzzy/Inner Shock | `a "Fuzzy/Inner Shock" balloon (oval with a thick fuzzy fur-like aura, NO tail)` | 강한 내면 충격 | ✅ |
| Soft Cloud Thought | `a soft cloud thought balloon (cloud shape, dotted edge, small bubble tail)` | 소심한 혼잣말 | ✅ |

### 외침 / 감정
| 이름 | GPT 복붙 스니펫 | 언제 | 검증 |
|------|----------------|------|:---:|
| Loud Shout/Scream | `a loud scream balloon (sharp spiky burst)` | 외침·비명 | ✅ |
| Surprised/Shocked | `a "Surprised/Shocked" balloon (jagged burst outline)` | 놀람·경악 | ✅ |
| Panic/Alarmed | `a "Panic/Alarmed" balloon (explosive jagged burst)` | 당황·다급 | ✅ |
| Held-Back Spike | `a "Held-Back Spike" balloon (angular polygon body; the single SPIKE points toward the mouth and serves AS the tail — one spike, no separate tail)` | 억눌린·참는 톤 | ✅ |
| Demonic/Menacing | `a "Demonic/Menacing" balloon (heavy black spiky/jagged outline)` | 불길·위협 | ✅ |
| **Crying** ⭐ | `a "Crying Balloon" (drooping outline with tear-like drops)` | 울며 말하기 | ✅ |
| **Broken Voice** ⭐ | `a "Broken Voice Balloon" (cracked outline)` | 감정 북받침·격해짐 | ✅ |
| **Dripping** ⭐ | `a "Dripping Balloon" (melting/dripping outline)` | 충격·허탈 | ✅ |
| **Dry Voice** ⭐ | `a "Dry Voice Balloon" (thin brittle angular outline)` | 시큰둥·비꼼(일상 코미디) | ✅ |

### 특수 / 매체(기본)
| 이름 | GPT 복붙 스니펫 | 언제 | 검증 |
|------|----------------|------|:---:|
| Narration Box | `a NARRATION BOX (rectangular caption box, no tail; "with a visible rectangular border" 넣으면 사각 테두리)` | 나레이션·자막 | ✅ |
| Telephone/Electronic | `a TELEPHONE/ELECTRONIC balloon (rectangular with a zig-zag electronic outline)` | 전화 너머 목소리 | ✅ |

---

## 2. 확장 (장르별 — 필요할 때 꺼내 씀) · 전부 GPT ✅

> ★ **매체는 GPT 기준 "실제 기기 아이콘"으로 나온다**(전화기·라디오·TV 모양). 이게 표준 형태.

### 디지털·전자
| 이름 | 스니펫 | 언제 |
|------|--------|------|
| Chat Message | `a chat message bubble (app-style rounded rectangle with tail)` | 메신저·문자 |
| Notification | `a notification bubble (small rounded rect with an alert mark)` | 앱 알림 |
| Glitch | `a "Glitch Balloon" (broken digital/glitch edges)` | 깨진 신호·오류 |
| Pixel | `a "Pixel Balloon" (blocky pixelated outline)` | 레트로 게임·디지털 |
| Hologram | `a "Hologram Balloon" (translucent layered, glowing outline)` | 홀로그램·투사 음성 |
| Static | `a "Static Balloon" (noisy broken outline)` | 잡음·신호 불량 |
| Recording Playback | `a recording-playback balloon (playback bar / waveform box)` | 녹음 재생 |
| Electric | `a "Electric Balloon" (lightning jagged burst)` | 전기·충격·에너지 |
| Spark | `a "Spark Balloon" (oval with small spark/star accents)` | 번뜩임·흥분 |

### 매체·음성 기기 (GPT = 기기 아이콘)
| 이름 | 스니펫 | 언제 |
|------|--------|------|
| Phone | `a phone balloon (rounded rect with a handset tail / phone device look)` | 전화 통화 |
| Radio | `a "Radio Balloon" (old radio-device shaped)` | 라디오 송출 |
| TV | `a "TV Balloon" (TV-screen shaped box)` | TV 음성 |
| Speaker/Megaphone | `a megaphone balloon (megaphone cone + balloon)` / `a speaker-device balloon` | 확성·방송 |
| Intercom | `a "Intercom Balloon" (intercom panel with UI marks)` | 인터폰·PA |
| Robot | `a "Robot Balloon" (angular mechanical frame)` | 로봇 음성 |
| AI Assistant | `a "AI Assistant Balloon" (clean rounded UI bubble + AI mark)` | AI·챗봇 |
| Synth Voice | `a "Synth Voice Balloon" (geometric waveform edge)` | 합성·기계 음성 |

### 환경 / 액션
| 이름 | 스니펫 | 언제 |
|------|--------|------|
| Underwater | `an "Underwater Balloon" (wavy bubbly outline)` | 물속·먹먹한 음성 |
| Echo | `an "Echo Balloon" (concentric repeated outlines)` | 메아리·울림 |
| Frozen | `a "Frozen Balloon" (icy angular frost edge)` | 차가움·얼어붙음 |
| Fire | `a "Fire Balloon" (flame-shaped outline)` | 분노·열정 |
| Wind | `a "Wind Balloon" (stretched flowing outline)` | 바람에 실린 음성 |
| Metal | `a "Metal Balloon" (hard beveled metal polygon)` | 금속·기계·냉정 |

### 장식 / 판타지
| 이름 | 스니펫 | 언제 |
|------|--------|------|
| Ornate | `an "Ornate Balloon" (decorative ornate border)` | 우아·연극적 |
| Scroll | `a "Scroll Balloon" (parchment scroll shape)` | 사극·고풍·판타지 |
| Glass | `a "Glass Balloon" (thin sharp cracked-glass outline)` | 깨질 듯·연약 |
| Poison | `a "Poison Balloon" (bubbling uneven toxic outline)` | 독설·사악 |
| Magic | `a "Magic Balloon" (ornate sparkly outline)` | 마법·주문 |
| Star | `a "Star Balloon" (star-shaped body)` | 밝은 흥분 |
| Gem | `a "Gem Balloon" (faceted jewel shape)` | 화려·마법 |
| Flower | `a "Flower Balloon" (floral petal edge)` | 사랑스러움·로맨스 |
| Calligraphy | `a "Calligraphy Balloon" (brush-calligraphic frame)` | 시적·역사극 |
| Void | `a "Void Balloon" (black-filled body, white text)` | 공허·냉랭·불길 (GPT 안정) |

---

## 3. 꼬리 규칙 & 위치 거동 — ★ 페이지 맥락

- **꼬리:** 있으면 화자 입 쪽. 한 컷 여러 풍선이면 각자 입 쪽. **꼬리 없는 타입:** 생각(Aura·구름), 전자/전화, 나레이션 박스. **예외:** Held-Back Spike는 스파이크가 곧 꼬리(별도 꼬리 금지).
- **위치 거동(페이지는 컷 그리드):**
  - 컷 안 고정(contained) — `keep this balloon inside the panel`
  - 컷 경계 걸침(panel-spanning) ✅ — 큰 외침이 이웃 두 컷 거터를 넘김. `draw it LARGE so it crosses the gutter and spans both panels`
  - 오버플로우 — `oversized so it clearly BREAKS OUT past the panel border into the white gutter` (약하면 GPT가 가둠 → 명령형으로 세게)
  - 한 컷 2풍선(주고받기) — 읽기 순서 명시(`A upper-left FIRST, B lower-right SECOND`), 각자 꼬리 입쪽.
- > **세로 빈 띠 규칙은 세로 웹툰(vertical-director) 전용**이라 여기선 다루지 않는다. 페이지형은 거터(흰 칸 사이)로 걸침·삐짐을 통제한다.

---

## 4. 부록 — 수렴 / 제외 / 약함

- **수렴(별도 항목 안 만듦, 대표로 흡수):** Cave Echo → Echo · Smoke·Dream → Soft Cloud · Slime → Dripping.
- **제외:** **Speed**(풍선 형태 아님, 화살표/속도선으로 빠짐 — 클린 효과로 처리).
- **약함→매체로 흡수:** Radio·Notification(단독 가치 낮으나 GPT에선 명확 → 확장에 포함).
- **검증 출처:** Nano v1·v2 / GPT v1·v2 4판. **GPT ✅면 채택**(Nano도 ✅면 더 든든). Void는 GPT 안정으로 살림.

---

## 사용 패턴 (페이지 프롬프트에 박는 법)

각 컷의 장면 묘사 아래에 `💬`로 **[사전 영어 스니펫] + 위치 한 줄 + 한국어 대사**를 적는다. 그리고 페이지 프롬프트 맨 끝의 클린 원고 경고문을 **"지정된 💬 말풍선만 그리고 그 외 텍스트는 금지"**로 바꾼다.

```
- 패널4 (세로중컷 — 전폭):
  지우가 폰을 보고 흠칫 놀라는 상반신.
  💬 "Surprised/Shocked" balloon (jagged burst outline), tail to her mouth — 지우 머리 위, "헉, 엄마?!"
```

폰트는 **깔끔한 산세리프**(손글씨 금지 — 손글씨는 효과음에만). 생각·전화·나레이션·Held-Back은 꼬리 없음.

---

## 갱신 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| v0.1 (page 사본) | 2026-06-28 | 마스터 v0.1 복제 → 페이지 맥락 조정(컷 안/걸침, 세로 빈 띠 제외). |
| v0.2 (page 사본) | 2026-06-28 | 마스터 v0.2 반영 — 코어 +5(Wobble·Crying·Broken Voice·Dripping·Dry Voice), 확장 대거(디지털·매체기기·환경·판타지), 표 구조·GPT 4판 검증 기준. 페이지 맥락 유지(세로 빈 띠 제외). |

> **마스터:** 사전 내용은 허브 `_말풍선자료/말풍선사전_v0.x.md`에서 먼저 고치고 이 사본에 반영한다(페이지 맥락 유지).
