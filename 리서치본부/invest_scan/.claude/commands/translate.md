# /translate — 번역 수동 트리거

번역 자동 트리거 실패 시 또는 재번역 필요 시 사용합니다.
@translator SubAgent를 수동으로 spawn하여 영어 산출물을 한국어로 번역합니다.

## Usage
```
/translate 2     — Step 2 output 번역 (output/schema-mapping.md)
/translate 4     — Step 4 output 번역 (output/completion-definition.md)
/translate 5     — Step 5 output 번역 (output/blueprint.md)
/translate 11    — Step 11 output 번역 (narrative_{date}.json)
/translate 12    — Step 12 output 번역 (weekly-report-{date}.md — 최종 리포트)
/translate 15    — Step 15 output 번역 (watchlist-{date}.md)
/translate all   — 모든 번역 대상 순차 실행 (2, 4, 5, 11, 12, 15)
```

## Execution Flow (per step)
```python
# Step N translation flow
step_n_targets = {
    2:  ("output/schema-mapping.md", "output/schema-mapping.ko.md"),
    4:  ("output/completion-definition.md", "output/completion-definition.ko.md"),
    5:  ("output/blueprint.md", "output/blueprint.ko.md"),
    11: ("output/temp/narrative_{date}.json", "output/temp/narrative_{date}.ko.json"),
    12: ("output/reports/weekly-report-{date}.md", "output/reports/weekly-report-{date}.ko.md"),
    15: ("output/watchlist-{date}.md", "output/watchlist-{date}.ko.md"),
}
```

1. Read `state.yaml.translations.step_N.status`
2. Verify source file exists (use date-glob for `{date}` templates)
3. Update `state.yaml.translations.step_N.status = "translating"` (atomic write)
4. Spawn `@translator` SubAgent:
   ```python
   result = Agent(
       subagent_type="translator",
       prompt=f"""
       Translate Step {N} InvestScan output to Korean.

       Source: {source_path}
       Target: {target_path}
       Glossary: translations/glossary.yaml (load first, update after)
       pACS log: pacs-logs/step-{N}-translation-pacs.md

       Protocol: Follow translator.md 7-step protocol exactly.
       pACS minimum: 70 (GREEN). Re-translate if RED (<50).
       Step 12 only: Score Fd dimension (Financial Domain accuracy).
       Update glossary with new InvestScan terms found.
       Return: {{"pacs_score": int, "pacs_grade": str, "new_terms": int}}
       """
   )
   ```
5. Parse result `pacs_score`, `pacs_grade`
6. Update `state.yaml.translations.step_N`:
   - `status: done | failed`
   - `pacs_score: [int]`
   - `pacs_grade: GREEN | YELLOW | RED`
   - `translated_at: [ISO8601]`
7. Report result to user in Korean:
   - GREEN (≥70): "✅ Step N 번역 완료 (pACS: [score])"
   - YELLOW (50-69): "⚠️ Step N 번역 완료 (pACS: [score], 품질 경고)"
   - RED (<50): "❌ Step N 재번역 필요 (pACS: [score]). /translate N 재실행"

## Quality Gates
| Grade | pACS | Action |
|-------|------|--------|
| GREEN | ≥ 70 | 정상 완료 |
| YELLOW | 50-69 | 완료 허용 + 경고 기록 |
| RED | < 50 | 재번역 필수 — tdd_verify.py가 TaskComplete 차단 |

## Step 12 Special Handling (Final Report)
Step 12 translation uses Fd (Financial Domain accuracy) pACS dimension:
- Verifies PER/YoY/CAGR financial term accuracy
- Checks 억/% unit preservation
- Validates 금감원/DART standard notation
- `Translation pACS (Step 12) = min(Ft, Ct, Nt, Fd)`
