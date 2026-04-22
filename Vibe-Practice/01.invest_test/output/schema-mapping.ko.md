# InvestScan 스키마 매핑(Schema Mapping)
**Step 2 산출물** | 생성일: 2026-03-29 | 언어: English (P5-A)

---

## EnvironmentScan WF-1 → 통합 신호 매핑

### 소스 스키마 탐색

| EnvironmentScan 필드 | 내부 UnifiedSignal 필드 | 비고 |
|----------------------|------------------------------|-------|
| `steeps_category` | `steeps_category` | 직접 매핑 |
| `pSST` | `psst_score` | 척도: 0-100 |
| `summary` | `summary` | 텍스트 콘텐츠 |
| `sector` | `sector` | 섹터 태그 |
| `confidence` | `confidence` | 0.0-1.0 척도 |
| `date` | `date` | YYYY-MM-DD 형식 |

### STEEPs 카테고리 값

| 원시 값 | 정규화 값 | 카테고리명 |
|-----------|-----------------|---------------|
| `"T"` | `"T"` | Technology |
| `"S"` | `"S"` | Social |
| `"E"` | `"E"` | Economic |
| `"E_env"` | `"E_env"` | Environmental |
| `"P"` | `"P"` | Political |
| `"s"` | `"s"` | Sector-specific (소문자 — Social과 구별) |

> **참고**: 소문자 `"s"`(섹터 특화)는 대문자 `"S"`(Social)와 **별개**이다. 이 구분은 steeps_classifier.py 라우팅에서 핵심적이다 (H-2, v3.4).

### 점수 척도 정규화

- 소스 척도: 0-100 (이미 정규화됨)
- 현재 EnvScan WF-1 출력에 대해 변환 불필요
- 향후 소스가 0-10 척도를 사용할 경우: 10을 곱하여 변환

### FRED API → InvestmentMeta 매핑

| FRED 시리즈 | InvestmentMeta 필드 | 로직 |
|------------|---------------------|-------|
| `DFF` | `rate_direction` | >= 5.0 + T10YIE > 2.5 → "hike"; <= 3.0 → "cut"; 그 외 "hold" |
| `CPIAUCSL` | `inflation_trend` | > 3.5 → "rising"; < 2.5 → "cooling"; 그 외 "stable" |
| `VIXCLS` + `BAMLH0A0HYM2` | `risk_appetite` | VIX < 15 + OAS < 3.0 → "high"; VIX > 25 or OAS > 5.0 → "low" |
| `DTWEXBGS` | `usd_strength` | > 105 → "strong"; < 95 → "weak"; 그 외 "neutral" |

### GlobalNews signals.parquet → 통합 신호 매핑

| Parquet 컬럼 | UnifiedSignal 필드 | 비고 |
|---------------|---------------------|-------|
| `headline` | `summary` | 신호 텍스트로 사용 |
| `sector` | `sector` | 직접 매핑 |
| `confidence` | `confidence` | 0.0-1.0 |
| `steeps_tag` | `steeps_category` | E2 → E_env 정규화 필요 가능 |
| `date` | `date` | YYYY-MM-DD |
| `source` | `source` | 중복 제거 해시에 사용 (DG-09) |

> **E_env 정규화**: gnews parquet는 `"E_env"` 태그를 사용한다 (v3.5 IR-13: 통합 표기법). 변환 불필요.

---

## 상태 SOT 참조

```yaml
# state.yaml discovered_schema 섹션 (리서치 에이전트가 자동 채움)
discovered_schema:
  envscan_wf1:
    steeps_field: "steeps_category"
    psst_field: "pSST"
    summary_field: "summary"
    score_scale: "0-100"
  gnews:
    file_exists: true
    confidence_field: "confidence"
```

---

*스키마 매핑은 normalizers.py의 기반이다. 스키마가 변경되면 normalizers.py와 이 문서를 함께 수정해야 한다.*
