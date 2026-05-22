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

##### 절대 규칙 (Critical)
1. **URL은 절대 추측·하드코딩하지 않는다.** 항상 WordPress REST API 응답의 `source_url` 값을 그대로 사용한다.
   - ❌ 금지: `week{N}-{day}.png` 패턴으로 URL을 생성해서 그대로 삽입
   - ❌ 금지: 이전 주차/이전 업로드의 URL을 재사용
   - ✅ 필수: 매 업로드마다 응답에서 `source_url` 추출 → 그 값을 HTML에 삽입
   - 이유: 동일 파일명이 이미 존재하면 WordPress가 `-1`, `-2`, `-7` 등 자동 suffix를 붙인다. 추측한 URL은 다른 이미지(또는 404)를 가리킬 위험이 크다.
2. **5개 요일 모두 업로드 성공할 때까지 책임진다.** 한 요일이라도 실패하면 즉시 재시도(아래 절차) 후 보고.
3. **업로드 직후 반드시 검증한다.** `curl -I {source_url}` 로 200 OK 확인 후 HTML에 삽입.
4. **응답 파싱 시 제어문자 제거 필수.** WordPress 응답에 NUL/제어바이트가 섞일 수 있어 `json.loads` 가 실패한다. 아래 헬퍼 그대로 사용.

##### 자동 업로드 + 검증 + 재시도 절차
```bash
WP_URL=$(python3 -c "import json;print(json.load(open('.wp-config.json'))['site_url'])")
WP_USER=$(python3 -c "import json;print(json.load(open('.wp-config.json'))['username'])")
WP_PASS=$(python3 -c "import json;print(json.load(open('.wp-config.json'))['app_password'])")

upload_one () {
  local DAY=$1 WEEK=$2 IMG=$3
  local FNAME="week${WEEK}-${DAY}.png"
  for attempt in 1 2 3 4; do
    curl -s -u "${WP_USER}:${WP_PASS}" \
      -H "Content-Disposition: attachment; filename=\"${FNAME}\"" \
      -H "Content-Type: image/png" \
      --data-binary @"${IMG}" \
      "${WP_URL}/wp-json/wp/v2/media" -o /tmp/wp_resp.json
    URL=$(python3 -c "
import json
data=open('/tmp/wp_resp.json','rb').read()
data=bytes([b for b in data if b>=0x20 or b in (0x09,0x0a,0x0d)])
try:
    d=json.loads(data); print(d.get('source_url',''))
except: pass
")
    if [ -n "$URL" ]; then
      # 검증: 200 OK 인지 확인
      CODE=$(curl -s -o /dev/null -w '%{http_code}' "$URL")
      if [ "$CODE" = "200" ]; then echo "$URL"; return 0; fi
    fi
    # 재시도: 파일명을 살짝 바꿔 충돌/캐시 회피
    FNAME="week${WEEK}-${DAY}-r${attempt}.png"
    sleep 5
  done
  echo "FAIL:${DAY}" >&2
  return 1
}
```
- 호출 예: `MON_URL=$(upload_one mon 18 ./images/mon.png)`
- 4회 재시도(파일명 변형 + 5초 대기) 후에도 실패하면 그 요일만 보고하고 사용자에게 수동 업로드 요청

##### URL 삽입 규칙
- `<img src>` 와 `<a href>` 모두 `source_url` 값으로 동일하게 교체
- 5개 요일 URL을 dict로 모은 뒤 placeholder `[이미지_URL]` 일괄 치환
- 작업 종료 시 `grep -oE 'https?://[^"]*\.(png|jpg)' html-with-images/*-wordpress.html | sort -u` 로 최종 URL 목록 출력하여 사용자가 즉시 확인 가능하게 한다

##### 업로드 실패 처리
- 4회 재시도 실패 시: 해당 요일 워드프레스 HTML은 placeholder 유지 + 사용자에게 명시적 보고
  - "fri.png 업로드 4회 실패 (서버 500). 워드프레스 관리자에서 직접 업로드 후 URL 알려주시면 교체해드리겠습니다."
- ❌ 절대 금지: 실패한 요일에 추측 URL이나 이전 URL을 임시로 채워 넣고 마치 성공한 것처럼 보고하지 않는다

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
