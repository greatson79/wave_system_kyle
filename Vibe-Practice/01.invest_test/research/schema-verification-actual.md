# InvestScan 소스 시스템 실제 스키마 검증 보고서

**Date**: 2026-03-28
**Method**: 코드 분석 (실제 Parquet 파일 없음 — GlobalNews 미실행 상태)
**Scope**: EnvScan database.json + priority-ranked + GlobalNews parquet_writer.py

---

## 1. EnvScan 스키마 검증

### 1.1 database.json 실제 구조

파일: `env-scanning/signals/database.json`

**최상위 구조:**
```json
{
  "version": "1.0",
  "created_at": "2026-01-30T12:11:53...",
  "total_signals": 509,
  "statistics": { "categories": {...}, "sources": {...} },
  "signals": [...]
}
```

**개별 신호 스키마 (9개 필드, pSST 없음 — Phase 1 수집 레코드):**

| 필드 | 타입 | 예시 |
|------|------|------|
| `id` | string | `"arxiv-2601.21760v1"`, `"federal-register-d48b..."` |
| `title` | string | 신호 제목 |
| `source.name` | string | `"arXiv"`, `"US Federal Register"`, `"TechCrunch"` |
| `source.type` | string | `"academic"`, `"policy"`, `"blog"` |
| `source.url` | string | 원본 URL |
| `source.published_date` | string (YYYY-MM-DD) | `"2026-01-29"` |
| `content.abstract` | string | 요약 텍스트 |
| `content.keywords` | list[string] | `["cs.AI", "fintech"]` |
| `content.language` | string | `"en"` |
| `metadata` | object | 소스별 상이 |
| `preliminary_category` | string | STEEPs 단축코드 |
| `collected_at` | ISO datetime | |
| `scan_date` | string (YYYY-MM-DD) | |

**⚠️ 핵심 발견**: database.json 신호 레코드에는 **pSST 필드 없음**.
pSST는 Phase 2 처리 후 `wf*/analysis/priority-ranked-{date}.json`에만 존재.

### 1.2 WF4 priority-ranked pSST 스케일: 확정값

**결론: 공식 Python 엔진 = 0-100, LLM 직접 생성 = 0-10 (비공식)**

| 파일 생성 방식 | `ranking_metadata.engine` | pSST 스케일 | 실측 범위 |
|---|---|---|---|
| `priority_score_calculator.py` (공식) | `"priority_score_calculator.py"` | **0-100** | 31.3–95.0 |
| LLM 직접 생성 (비공식) | 없음 | **0-10** | 1.5–10.0 |
| 구형 LLM 정수 (2026-02-xx) | 없음 | **0-100 정수** | 40–95 |

**공식 스케일 근거** (`psst_calculator.py`):
- 6개 차원 (SR, ES, CC, TC, DC, IC) 각 0-100
- Grade: A≥90, B≥70, C≥50, D<50 → 명백히 0-100 기준

**공식 엔진 감지 조건**: `ranking_metadata.engine == "priority_score_calculator.py"` → 0-100 적용

> ⚠️ **final-research.md 수정 필요**: Part I.1.4의 "WF4 priority-ranked: 부동소수점 0-10" 설명은
> LLM 직접 생성 비공식 파일에만 해당. 공식 Python 엔진 출력은 0-100.

### 1.3 STEEPs 코드 형식 변이 목록 (총 17가지)

**database.json 발견:**

| 코드 | 의미 |
|------|------|
| `"T"` | Technology |
| `"E"` | Economic |
| `"S"` | Social |
| `"P"` | Political |
| `"s"` | Spiritual (소문자, 7개) |
| `"E_Environmental"` | Environmental |

**priority-ranked 추가 발견:**

| 코드 | 형식 |
|------|------|
| `"T_Technological"` | 장형 |
| `"E_Economic"` | 장형 |
| `"E_economic"` | 장형 소문자 혼용 |
| `"E_environmental"` | 장형 소문자 혼용 |
| `"P_Political"` | 장형 |
| `"S_Social"` | 장형 |
| `"s_spiritual"` | 장형 소문자 |
| `"Economic"` | 전체 영문자 |
| `"Political"` | 전체 영문자 |
| `"Technological"` | 전체 영문자 |
| `"Environmental"` | 전체 영문자 |

**normalizers.py 필수 정규화 코드:**
```python
STEEPS_MAP = {
    "T": "T", "T_Technological": "T", "Technological": "T",
    "E": "E", "E_Economic": "E", "E_economic": "E", "Economic": "E",
    "E_Environmental": "E_ENV", "E_environmental": "E_ENV", "Environmental": "E_ENV",
    "S": "S", "S_Social": "S", "Social": "S",
    "P": "P", "P_Political": "P", "Political": "P",
    "s": "S_SPIRITUAL", "s_spiritual": "S_SPIRITUAL",
}
```

### 1.4 실제 발견된 source.type 열거값

코드 정의 8종: `"academic"`, `"patent"`, `"government"`, `"policy"`, `"news_major"`, `"news_minor"`, `"blog"`, `"social_media"`
실제 database.json 발견값: `"academic"`, `"policy"`, `"blog"` (3종)

---

## 2. GlobalNews Parquet 스키마 검증 (코드 기반)

**주의**: `data/output/`에 실제 Parquet 파일 없음 (GlobalNews ML 분석 미실행).
아래는 `src/storage/parquet_writer.py`의 `SIGNALS_PA_SCHEMA` 코드에서 확인한 스키마.

### 2.1 signals.parquet 컬럼 목록 (12컬럼)

| 컬럼명 | PyArrow 타입 | nullable | 값 범위 |
|--------|-------------|----------|--------|
| `signal_id` | `utf8` | NOT NULL | UUID |
| `signal_layer` | `utf8` | NOT NULL | `L1_fad`, `L2_short`, `L3_mid`, `L4_long`, `L5_singularity` |
| `signal_label` | `utf8` | NOT NULL | 사람 가독 레이블 |
| `detected_at` | `timestamp("us", tz="UTC")` | NOT NULL | |
| `topic_ids` | `list_(int32)` | nullable | Stage 4 연결 |
| `article_ids` | `list_(utf8)` | nullable | 출처 기사 IDs |
| `burst_score` | `float32` | nullable | 0.0+ (상한 없음, z-score 기반) |
| `changepoint_significance` | `float32` | nullable | 0.0–1.0 |
| `novelty_score` | `float32` | nullable | 0.0–1.0 |
| `singularity_composite` | `float32` | nullable | 0.0–1.0 |
| `evidence_summary` | `utf8` | NOT NULL | |
| `confidence` | `float32` | NOT NULL | 0.0–1.0 |

### 2.2 analysis.parquet 핵심 컬럼 (21컬럼 중 발췌)

| 컬럼명 | 타입 | 값 범위 | 비고 |
|--------|------|--------|------|
| `article_id` | utf8 | — | signals.parquet JOIN 키 |
| `steeps_category` | utf8 | STEEPs 코드 | signals와 JOIN 필요 |
| `importance_score` | float32 | **0.0–100.0** | `/100` 정규화 필요 |
| `sentiment_score` | float32 | -1.0~1.0 | |
| `emotion_*` (8개) | float32 각 | 0.0~1.0 | joy, fear, anger 등 |
| `embedding` | list_(float32) | 384-dim | SBERT all-MiniLM |

### 2.3 final-research.md 추정 vs 실제 불일치

| 항목 | final-research.md | 실제 확인 | 조치 |
|------|------------------|---------|------|
| signals.parquet 컬럼 수 | 12 | 12 | ✅ 일치 |
| confidence 범위 | 0.0–1.0 | 0.0–1.0 | ✅ 일치 |
| signal_layer 구체 값 | L1-L5 (미명시) | `L1_fad`, `L2_short`, `L3_mid`, `L4_long`, `L5_singularity` | ⚠️ 구체 값 추가 필요 |
| burst_score 범위 | 미명시 | 0.0+ 무제한 | ⚠️ 신규 추가 필요 |
| WF4 pSST 스케일 | "0-10" | 공식=0-100, 비공식=0-10 혼재 | ❌ 수정 필요 |
| importance_score | 미언급 | 0.0–100.0 (analysis.parquet) | ⚠️ 신규 추가 필요 |

---

## 3. normalizers.py 구현 확정 스키마

### EnvScan → UnifiedSignal 매핑 (검증됨)

| UnifiedSignal 필드 | 소스 경로 | 변환 규칙 |
|-------------------|----------|---------|
| `id` | `signal.id` | 그대로 |
| `title` | `signal.title` | 그대로 |
| `source_type` | `signal.source.type` | 8종 enum 허용 |
| `published_date` | `signal.source.published_date` | string → date |
| `steeps_category` | `signal.preliminary_category` | STEEPS_MAP 17변이 정규화 |
| `language` | `signal.content.language` | 그대로 |
| `confidence_score` | priority-ranked `psst_score` | engine 필드로 스케일 감지 후 → 0.0–1.0 |

### GlobalNews → UnifiedSignal 매핑 (코드 기반 검증)

| UnifiedSignal 필드 | 소스 컬럼 | 변환 규칙 |
|-------------------|---------|---------|
| `signal_layer` | `signal_layer` | 그대로 (이미 L1_fad 등 표준화됨) |
| `confidence_score` | `confidence` | 그대로 (0.0–1.0) |
| `burst_score` | `burst_score` | 그대로 (백분위 기반 상대 비교) |
| `steeps_category` | `analysis.steeps_category` | JOIN(article_ids 키) 필요 |
| `importance_score_normalized` | `analysis.importance_score` | `/100` 필요 |

### 명시적 스케일 파라미터 (auto-detection 절대 금지)

```python
PSST_SCALE_MAP = {
    "priority_score_calculator": (0.0, 100.0),   # 공식 Python 엔진
    "pSST_unified_llm": (0.0, 10.0),             # 비공식 LLM 출력
    "psst_legacy_int": (0, 100),                  # 구형 정수
}
GNEWS_CONFIDENCE_SCALE = (0.0, 1.0)              # 변환 불필요
GNEWS_IMPORTANCE_SCALE = (0.0, 100.0)            # /100 필요
```

---

## 4. PRD Data Schema 섹션 반영 권고

### 검증된 사실 ✅

1. pSST 공식 스케일 = 0-100 (`psst_calculator.py` 코드 확인)
2. database.json에 pSST 없음 (Phase 1 레코드)
3. STEEPs 17가지 코드 변이 확인 (소문자 `"s"` 포함)
4. GlobalNews signals.parquet 12컬럼 확정 (parquet_writer.py)
5. burst_score 상한 없음 (z-score 기반 무제한)
6. importance_score 범위 0.0–100.0 (analysis.parquet 전용)

### 여전히 가정 ⚠️

1. GlobalNews signals.parquet 실제 데이터 없음 (ML 분석 1회 실행 후 검증 필요)
2. pSST 차원 가중치 실운용값 (thresholds.yaml 오버라이드 가능)
3. STEEPs 분류기 정확도 70-80% (실측 불가)
