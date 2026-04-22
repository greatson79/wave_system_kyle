# InvestScan Schema Mapping
**Step 2 Output** | Generated: 2026-03-29 | Language: English (P5-A)

---

## EnvironmentScan WF-1 → UnifiedSignal Mapping

### Source Schema Discovery

| EnvironmentScan Field | Internal UnifiedSignal Field | Notes |
|----------------------|------------------------------|-------|
| `steeps_category` | `steeps_category` | Direct mapping |
| `pSST` | `psst_score` | Scale: 0-100 |
| `summary` | `summary` | Text content |
| `sector` | `sector` | Sector tag |
| `confidence` | `confidence` | 0.0-1.0 scale |
| `date` | `date` | YYYY-MM-DD format |

### STEEPs Category Values

| Raw Value | Normalized Value | Category Name |
|-----------|-----------------|---------------|
| `"T"` | `"T"` | Technology |
| `"S"` | `"S"` | Social |
| `"E"` | `"E"` | Economic |
| `"E_env"` | `"E_env"` | Environmental |
| `"P"` | `"P"` | Political |
| `"s"` | `"s"` | Sector-specific (lowercase — distinct from Social) |

> **Note**: Lowercase `"s"` (sector-specific) is DISTINCT from uppercase `"S"` (Social). This distinction is critical for steeps_classifier.py routing (H-2, v3.4).

### Score Scale Normalization

- Source scale: 0-100 (already normalized)
- No conversion required for current EnvScan WF-1 output
- If future source uses 0-10 scale: multiply by 10

### FRED API → InvestmentMeta Mapping

| FRED Series | InvestmentMeta Field | Logic |
|------------|---------------------|-------|
| `DFF` | `rate_direction` | >= 5.0 + T10YIE > 2.5 → "hike"; <= 3.0 → "cut"; else "hold" |
| `CPIAUCSL` | `inflation_trend` | > 3.5 → "rising"; < 2.5 → "cooling"; else "stable" |
| `VIXCLS` + `BAMLH0A0HYM2` | `risk_appetite` | VIX < 15 + OAS < 3.0 → "high"; VIX > 25 or OAS > 5.0 → "low" |
| `DTWEXBGS` | `usd_strength` | > 105 → "strong"; < 95 → "weak"; else "neutral" |

### GlobalNews signals.parquet → UnifiedSignal Mapping

| Parquet Column | UnifiedSignal Field | Notes |
|---------------|---------------------|-------|
| `headline` | `summary` | Used as signal text |
| `sector` | `sector` | Direct mapping |
| `confidence` | `confidence` | 0.0-1.0 |
| `steeps_tag` | `steeps_category` | May need E2 → E_env normalization |
| `date` | `date` | YYYY-MM-DD |
| `source` | `source` | Used in dedup hash (DG-09) |

> **E_env normalization**: gnews parquet uses `"E_env"` tag (v3.5 IR-13: unified notation). No conversion needed.

---

## State SOT Reference

```yaml
# state.yaml discovered_schema section (auto-populated by research agents)
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

*Schema mapping is the foundation for normalizers.py. Any schema changes require updating normalizers.py AND this document.*
