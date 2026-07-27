---
name: insert-images
description: 생성된 매일묵상 HTML 파일에 이미지를 삽입합니다. [이미지_URL] 플레이스홀더를 실제 이미지 경로로 교체합니다.
disable-model-invocation: true
argument-hint: [주차번호] [output경로]
allowed-tools: Read, Write, Bash
---

# 묵상 이미지 삽입

## 실행
```
python3 src/scripts/insert-images.py 1 output/8월/1주차
```

## 인수
- **$0**: 주차 번호 (1~52)
- **$1**: 프로젝트 루트 기준 output 경로 (예: `output/8월/1주차`)

## 작업 대상
- 대상 폴더: `<output경로>/매일묵상/`
- 소스: `<output경로>/매일묵상/html-original/`의 HTML 파일들
- 이미지: `<output경로>/매일묵상/images/`
- 결과: `<output경로>/매일묵상/html-with-images/`에 이미지 삽입된 HTML 저장

## 이미지 파일 규칙
- 파일명: `mon`, `tue`, `wed`, `thu`, `fri`
- 확장자: `.jpg`, `.jpeg`, `.png`, `.webp` 중 자동 인식
- 위치 예: `output/8월/1주차/매일묵상/images/mon.png`

## 작업 순서

### 1단계: 이미지 확인
- `<output경로>/매일묵상/images/`에 mon~fri 이미지 파일이 있는지 확인

### 2단계: 대상 HTML 파일 확인
```
<output경로>/매일묵상/
└── html-original/     ← mon~fri × 3가지 형식 = 15개 HTML
    ├── mon-adult-wordpress.html
    ├── mon-adult-a4.html
    ├── mon-youth-a4.html
    └── ... (총 15개)
```
총 15개 파일에서 `[이미지_URL]` 플레이스홀더가 있는지 확인

### 3단계: 이미지 경로 교체
각 요일(mon~fri)에 해당하는 이미지를 매칭하여 교체:

**모든 HTML 변형(`*-adult-a4.html`, `*-youth-a4.html`, `*-adult-wordpress.html`)은 동일한 로컬 상대 경로를 사용한다.**

- WordPress REST API 업로드·인증 설정·온라인 URL 검증은 이 작업 범위에 없다.
- 각 요일의 `<img src>`와 `<a href>`에 `[이미지_URL]`, `[이미지_원본_URL]`가 있으면 둘 다 `../images/{day}.png`로 교체한다.
- `*-wordpress.html`도 로컬 경로 계약을 따른다. 외부 게시가 필요하면 발행 단계에서 별도 자산 경로를 제공한다.

**모든 파일을 `html-with-images/` 폴더에 저장**

### 4단계: A4 HTML 자동 캡쳐
- `html-with-images/` 폴더의 A4 HTML 파일들을 PNG로 캡쳐
- 캡쳐 결과를 `captured/` 폴더에 저장
- capture-a4.js 스크립트 사용 (Puppeteer)

### 5단계: 결과 보고
```
✅ 이미지 삽입 및 캡쳐 완료 (week-7_2026-02-16)
├── html-with-images/: 15개 HTML 파일 생성
├── images/: 5개 이미지 복사됨
└── captured/: 10개 PNG 캡쳐됨 (성인/청소년 A4)
이미지 소스: ~/images/week-7/
```

## 교체 대상
HTML 파일 내 `[이미지_URL]`이 포함된 모든 `<img>` 태그의 `src` 속성을 교체한다.

## 주의사항
- 이미 이미지가 삽입된 파일(플레이스홀더가 없는 파일)은 건너뛴다
- 교체 전 원본 파일을 변경하므로, 필요 시 사전 백업을 권장한다
- 이미지 파일이 누락된 요일은 경고를 표시하고 해당 파일만 건너뛴다

## 캡처 규격 계약 (명문화 — 2026-07-27)

> 기존 스크립트 계약(`capture-full-a4.js` 상단 주석)을 SKILL 차원에서 문서화한 것이다. **기준 변경 아님**(CEO 승인 조건 c).

- **A4 인쇄용 = `src/scripts/capture-full-a4.js`**: 폭 794px 고정 + **`fullPage: true`** 로 문서 전체를 캡처한다. 따라서 `captured/`의 PNG는 **폭 고정·높이 콘텐츠 가변**이며 **A4 세로비(1:1.414)로 고정되지 않는다** — 긴 묵상 본문의 하단 잘림을 방지하기 위한 **의도된 동작**이다.
- **메신저·모바일 공유용 = `src/scripts/capture-a4.js`**: 폭 540px, `.page` 엘리먼트 단위 캡처(용도 분리 — 인쇄물에 쓰지 말 것).
- **검수 지침**: `captured/`의 A4 세로비 불일치·높이 편차는 결함이 아니다. 판정은 **콘텐츠 전체가 한 이미지에 담기고 하단 잘림이 없는지**로 한다.
- **선례**: 7월 3·4주차 captured도 폭 고정·높이 가변(2786~3040px)으로 캡처됐고 dual 적대검수 ACCEPT로 발행됨.
