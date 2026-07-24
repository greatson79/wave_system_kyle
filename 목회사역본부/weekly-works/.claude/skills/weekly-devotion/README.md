# 📖 디딤교회 주간 매일묵상 스킬 (weekly-devotion)

매주 토요일, 다음 주 월~금 매일묵상 콘텐츠 15개를 일괄 생성하는 Claude Code 스킬입니다.

## 출력물

| 출력물 | 형식 | 디자인 | 용도 |
|--------|------|--------|------|
| 성인 워드프레스 × 5 | HTML article | Noto Serif / 크림색 | 홈페이지 게시 |
| 성인 카톡 × 5 | A4 HTML | Sanctified Olive | 카톡 파일 공유 |
| 청소년 카톡 × 5 | A4 HTML | Fresh Lime & Navy | 카톡 파일 공유 |

---

## 설치

```bash
cp -r weekly-devotion ~/.claude/skills/weekly-devotion
```

## 사용

```bash
/weekly-devotion 7       # 7주차 생성
/weekly-devotion          # 다음 주차 자동 계산
```

## 출력 구조

```
output/week-7/
├── adult-wordpress/     ← 워드프레스 게시용 (5개)
│   └── mon~fri.html
├── adult-kakao/         ← 성인 카톡용 A4 (5개)
│   └── mon~fri.html
└── youth-kakao/         ← 청소년 카톡용 A4 (5개)
    └── mon~fri.html
```

## 주간 워크플로우

1. **토요일**: `/weekly-devotion` 실행 → 15개 파일 생성
2. **토요일**: 이미지 준비 → `[이미지_URL]` 교체
3. **일요일**: 워드프레스에 월~금 예약 게시
4. **월~금**: 해당 요일 카톡 HTML 파일 공유 (성인+청소년)

## 파일 구조

```
~/.claude/skills/weekly-devotion/
├── SKILL.md                          ← 스킬 지침
├── devotion-data.json                ← 52주 묵상 본문
├── templates/
│   ├── adult-wordpress.html          ← WP 게시용
│   ├── adult-a4.html                 ← 성인 카톡 A4 (Sanctified Olive)
│   └── youth-a4.html                 ← 청소년 카톡 A4 (Fresh Lime)
└── README.md
```
