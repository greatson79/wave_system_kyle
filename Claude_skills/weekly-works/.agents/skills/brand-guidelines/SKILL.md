---
name: brand-guidelines
description: Applies 디딤교회's official brand colors and typography to any artifact — HTML, PDF, PPTX, cards, posters. Use whenever brand colors, style guidelines, visual formatting, or church design standards apply.
license: Complete terms in LICENSE.txt
---

# 디딤교회 Brand Guidelines

## Overview

디딤교회의 공식 브랜드 아이덴티티와 스타일 가이드를 적용하는 스킬.
컬러 팔레트는 두 가지로 구성된다:
1. **로고 컬러** — 픽셀 십자가 로고에서 직접 추출한 색상
2. **확장 브랜드 5색** — 콘텐츠 전반에 걸쳐 사용하는 공식 브랜드 컬러

**Keywords**: 브랜드, 브랜드 가이드, 디딤교회, 컬러 팔레트, 타이포그래피, 카드뉴스, 설교, 시각 디자인, brand colors, typography, church identity, visual formatting

---

## 1. 로고 컬러 (Logo Colors)

픽셀 십자가 로고(`didim-logo.png`)에서 직접 추출한 색상.
로고 재현, 로고 주변 디자인, 로고와 함께 사용하는 배경·테두리에 우선 적용.

| 이름 | HEX | 용도 |
|------|-----|------|
| **Dark Slate** (다크 슬레이트) | `#385050` | 십자가 주 색상, 어두운 배경, 강한 제목 |
| **Yellow Olive** (옐로우 올리브) | `#A8B010` | 픽셀 사각형 포인트, 강조 요소 |
| **Yellow Green** (옐로우 그린) | `#E0C820` | 픽셀 사각형 포인트, 밝은 강조 |
| **Lime Green** (라임 그린) | `#80B828` | 픽셀 사각형 보조, 내추럴 포인트 |

---

## 2. 확장 브랜드 5색 (Extended Brand Colors)

카드뉴스, SNS 콘텐츠, 포스터, HTML 등 모든 디지털 콘텐츠에 사용하는 공식 브랜드 컬러.

| 이름 | HEX | RGB | 용도 |
|------|-----|-----|------|
| **Purple** (퍼플) | `#942192` | 148, 33, 146 | 주요 강조, 표지 배경, 제목 포인트 |
| **Blue** (블루) | `#0433FF` | 4, 51, 255 | 링크, 인터랙티브, 보조 강조 |
| **Teal** (틸) | `#009193` | 0, 145, 147 | 성인 묵상 테마, 핵심 메시지 배경 |
| **Gold** (골드) | `#E1B44F` | 225, 180, 79 | 장식선, 아이콘, 인용구 포인트 |
| **Rose** (로즈) | `#BB605D` | 187, 96, 93 | 따뜻한 강조, 적용/초대 슬라이드 |

---

## 3. Neutral Colors (배경 및 텍스트)

| 이름 | HEX | 용도 |
|------|-----|------|
| **White** | `#FFFFFF` | 라이트 슬라이드 배경 |
| **Cream** | `#FAF8F5` | 본문 배경, 부드러운 라이트 배경 |
| **Charcoal** | `#333333` | 기본 본문 텍스트 |
| **Dark** | `#1A1A1A` | 강한 제목, 다크 배경 |

---

## 4. Slide Color Map (카드뉴스 슬라이드별)

| 슬라이드 | 배경색 | 텍스트 색 | 포인트 색 |
|----------|--------|----------|----------|
| 표지 | `#942192` (퍼플) | `#FFFFFF` | `#E1B44F` (골드) |
| 공감 | `#FAF8F5` (크림) | `#333333` | `#942192` (퍼플) |
| 핵심 메시지 1 | `#FFFFFF` | `#1A1A1A` | `#0433FF` (블루) |
| 핵심 메시지 2 | `#009193` (틸) | `#FFFFFF` | `#E1B44F` (골드) |
| 인용구 | `#FAF8F5` (크림) | `#942192` (퍼플) | `#E1B44F` (골드) |
| 적용/초대 | `#BB605D` (로즈) | `#FFFFFF` | `#E1B44F` (골드) |
| 마무리 | `#385050` (다크 슬레이트, 로고색) | `#FFFFFF` | `#E1B44F` (골드) |

> 마무리 슬라이드에 로고 컬러(`#385050`)를 사용해 로고와 자연스럽게 연결.

---

## 5. Typography

- **Display / 제목**: Noto Serif KR (weight: 700/900) — 핵심 메시지, 인용구, 표지 제목
- **Body / 본문**: Noto Sans KR (weight: 300/400/700) — 본문 텍스트, 설명, 캡션
- **Fallback**: serif → Georgia, sans-serif → Arial

**웹폰트 로드 (HTML 사용 시):**
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&family=Noto+Sans+KR:wght@300;400;700&display=swap" rel="stylesheet">
```

---

## 6. CSS Variables Template

```css
:root {
  /* 로고 컬러 */
  --logo-dark-slate:    #385050;
  --logo-yellow-olive:  #A8B010;
  --logo-yellow-green:  #E0C820;
  --logo-lime:          #80B828;

  /* 확장 브랜드 5색 */
  --color-purple: #942192;
  --color-blue:   #0433FF;
  --color-teal:   #009193;
  --color-gold:   #E1B44F;
  --color-rose:   #BB605D;

  /* 뉴트럴 */
  --color-white:    #FFFFFF;
  --color-cream:    #FAF8F5;
  --color-charcoal: #333333;
  --color-dark:     #1A1A1A;

  /* 폰트 */
  --font-display: 'Noto Serif KR', Georgia, serif;
  --font-body:    'Noto Sans KR', Arial, sans-serif;
}
```

---

## 7. Python (python-pptx) Color Values

```python
from pptx.dml.color import RGBColor

# 로고 컬러
LOGO_COLORS = {
    "dark_slate":    RGBColor(0x38, 0x50, 0x50),
    "yellow_olive":  RGBColor(0xA8, 0xB0, 0x10),
    "yellow_green":  RGBColor(0xE0, 0xC8, 0x20),
    "lime":          RGBColor(0x80, 0xB8, 0x28),
}

# 확장 브랜드 5색
BRAND_COLORS = {
    "purple": RGBColor(0x94, 0x21, 0x92),
    "blue":   RGBColor(0x04, 0x33, 0xFF),
    "teal":   RGBColor(0x00, 0x91, 0x93),
    "gold":   RGBColor(0xE1, 0xB4, 0x4F),
    "rose":   RGBColor(0xBB, 0x60, 0x5D),
}

# 뉴트럴
NEUTRAL_COLORS = {
    "white":    RGBColor(0xFF, 0xFF, 0xFF),
    "cream":    RGBColor(0xFA, 0xF8, 0xF5),
    "charcoal": RGBColor(0x33, 0x33, 0x33),
    "dark":     RGBColor(0x1A, 0x1A, 0x1A),
}
```

---

## 8. Logos

| 용도 | 경로 |
|------|------|
| 기본 로고 | `src/assets/logos/didim-logo.png` |
| 흰색 버전 (어두운 배경용) | CSS `filter: brightness(0) invert(1)` 적용 |
| 기도카드 로고 | `src/assets/logos/prayer-logo.png` |

**로고 사용 규칙:**
- 어두운 배경(퍼플, 다크 슬레이트 등)에서는 `filter: brightness(0) invert(1)` 적용
- 카드뉴스 마지막 슬라이드에는 반드시 실제 이미지 파일 사용 (텍스트 대체 금지)
- 기도카드에는 `prayer-logo.png` 전용 사용
- 로고 배경을 디자인할 때 `--logo-dark-slate` (#385050) 활용 시 로고와 자연스럽게 조화

---

## 9. Quality Gates

어떤 산출물이든 브랜드 적용 후 다음을 확인한다:

- [ ] 로고 컬러(`#385050` 계열) 또는 브랜드 5색 중 하나 이상이 주 색상으로 사용되었는가?
- [ ] 골드 `#E1B44F`가 장식선/포인트로 일관되게 사용되었는가?
- [ ] Noto Serif KR (제목) + Noto Sans KR (본문) 폰트 페어링이 적용되었는가?
- [ ] 어두운 배경에서 로고가 흰색/반전으로 표시되는가?
- [ ] 마무리 슬라이드에 실제 로고 이미지(`didim-logo.png`)가 삽입되었는가?
