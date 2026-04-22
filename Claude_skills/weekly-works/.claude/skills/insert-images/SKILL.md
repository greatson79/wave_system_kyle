---
name: insert-images
description: 생성된 매일묵상 HTML 파일에 이미지를 삽입합니다. [이미지_URL] 플레이스홀더를 실제 이미지 경로로 교체합니다.
disable-model-invocation: true
argument-hint: [주차번호] [이미지소스]
allowed-tools: Read, Write, Bash
---

# 묵상 이미지 삽입

## 실행
```
/insert-images 7 ~/images/week-7/
/insert-images 7 https://example.com/images/
```

## 인수
- **$0**: 주차 번호 (1~52)
- **$1**: 이미지 소스 (로컬 폴더 경로 또는 URL 접두사)

## 작업 대상
- 대상 폴더: `output/week-{N}_YYYY-MM-DD/`
- 소스: `html-original/` 폴더의 HTML 파일들
- 결과: `html-with-images/` 폴더에 이미지 삽입된 HTML 저장

## 이미지 파일 규칙
- 파일명: `mon`, `tue`, `wed`, `thu`, `fri`
- 확장자: `.jpg`, `.jpeg`, `.png`, `.webp` 중 자동 인식
- 로컬 경로 예: `~/images/week-7/mon.jpg`
- URL 예: `https://example.com/images/mon.jpg`

## 작업 순서

### 1단계: 이미지 소스 확인
- 로컬 경로인 경우: 폴더 내 mon~fri 이미지 파일 존재 확인
- URL인 경우: URL 패턴 검증

### 2단계: 대상 HTML 파일 확인
```
output/week-{N}_YYYY-MM-DD/
└── html-original/     ← mon~fri × 3가지 형식 = 15개 HTML
    ├── mon-adult-wordpress.html
    ├── mon-adult-a4.html
    ├── mon-youth-a4.html
    └── ... (총 15개)
```
총 15개 파일에서 `[이미지_URL]` 플레이스홀더가 있는지 확인

### 3단계: 이미지 경로 교체
각 요일(mon~fri)에 해당하는 이미지를 매칭하여 교체:

**⚠️ 워드프레스용(`*-wordpress.html`)과 A4용(`*-a4.html`)은 경로 처리가 다르다:**

#### A4 HTML (`*-adult-a4.html`, `*-youth-a4.html`) — 로컬 상대 경로
- 로컬 브라우저/Puppeteer에서 열어 캡쳐하는 용도
- 이미지를 `images/` 폴더로 복사
- 상대 경로 `../images/mon.png` 형식으로 삽입

#### 워드프레스 HTML (`*-adult-wordpress.html`) — 온라인 URL 필수
- 워드프레스에 HTML 코드를 복사-붙여넣기 하는 용도
- **로컬 상대 경로(`./mon.png`, `../images/mon.png`)는 워드프레스에서 작동하지 않음**
- 반드시 온라인 URL을 사용해야 함
- **자동 업로드 작업 흐름:**
  1. `.wp-config.json`에서 WordPress 인증 정보 읽기
  2. `images/` 폴더의 로컬 이미지(mon~fri)를 WordPress 미디어 라이브러리에 업로드
  3. 업로드 후 반환된 URL을 WordPress HTML에 삽입
  4. `<a href>` 링크도 동일한 WordPress URL로 설정
- **WordPress REST API 업로드 방법:**
  ```bash
  # .wp-config.json 읽기
  WP_URL=$(cat .wp-config.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['site_url'])")
  WP_USER=$(cat .wp-config.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['username'])")
  WP_PASS=$(cat .wp-config.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['app_password'])")

  # 이미지 업로드 (요일별, 파일명: week{N}-{day}.png)
  RESULT=$(curl -s \
    -u "${WP_USER}:${WP_PASS}" \
    -H "Content-Disposition: attachment; filename=\"week{N}-{day}.png\"" \
    -H "Content-Type: image/png" \
    --data-binary @"이미지파일경로" \
    "${WP_URL}/wp-json/wp/v2/media" \
    | tr -d '\000-\031')

  # 업로드된 URL 추출
  IMAGE_URL=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['source_url'])")
  ```
  - `<a href>`와 `<img src>` 모두 `IMAGE_URL` 사용
  - 파일명 규칙: `week{주차번호}-{요일}.png` (예: `week10-mon.png`)
- **업로드 실패 시** — 사용자에게 알리고 해당 요일만 건너뜀

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
