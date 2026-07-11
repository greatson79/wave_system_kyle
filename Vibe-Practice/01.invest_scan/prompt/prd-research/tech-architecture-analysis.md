# Tech Deep-Dive: Architecture Analysis (Branch 2.1 + 2.2)

> PHASE 1 Branch 2.1 (Evolutionary) + 2.2 (Big Bang) — 완료됨

---

## 최종 권장: EVOLUTIONARY + 2개 Big Bang 요소

### 핵심 판정

| 기준 | Evolutionary | Big Bang | 승자 |
|------|-------------|----------|------|
| 첫 리포트까지 시간 | Week 3-4 | Week 7-8 | **Evolutionary** |
| 6개월 LOC | ~2,100-2,600 | ~3,000-3,500 | 동률 |
| 개발 시간 | ~50-70hr | ~80-100hr | **Evolutionary** |
| 파이프라인 안정성 | 70-80% | 90-95% | **Big Bang** |
| 스키마 드리프트 대응 | 낮음 (dict) | 높음 (Pydantic) | **Big Bang** |
| 낭비 엔지니어링 위험 | 낮음 | 중간 (40% 미사용 가능) | **Evolutionary** |
| 개발자 동기부여 | 높음 (즉시 결과) | 낮음 (긴 세팅) | **Evolutionary** |

### Big Bang에서 빌려올 2가지

1. **Typed Schema** (`@dataclass(frozen=True)`) — ~100 LOC, dict 키 타이핑 버그 방지
2. **Health Check** (사전 검증) — ~50 LOC, 소스 시스템 출력 존재+최신 여부 확인

### 나머지 Big Bang 요소는 트리거 기반 진화로 연기
- Checkpoint/resume → 실제 크래시 발생 시
- Pydantic → dataclass 부족 증명 시
- SQLite signal store → 8주+ 데이터 축적 시
- 진화 추적 → 수동 추적이 고통스러울 때
- YAML config → 하드코딩 경로가 2회+ 변경 시

### 6개월 진화 로드맵

```
Month 1-2 (~25-30hr): normalize.py + schema.py + synthesize.py + report.py + health_check → ~1,200 LOC
Month 3-4 (~15-20hr): + steeps_classifier + dedup + config.yaml + CLI → ~1,800 LOC
Month 5-6 (~15-20hr): + signal_store + evolution_tracker + journal → ~2,600 LOC
Total: ~2,600 LOC, ~55-70 dev hours (주 2.5-3시간 평균)
```

### 데이터 흐름도

```
EnvScan JSON → normalize.py (+ schema.py) → synthesize.py → report.py → weekly-report.md
GlobalNews Parquet ↗                          ↑ health_check
```

파일 기반 IPC가 영구적 통합 경계. 양 소스 시스템 수정 없음.
