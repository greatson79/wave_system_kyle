---
name: translator
description: InvestScan translation skill. Translates English outputs to Korean. Follows translator.md 7-step protocol with pACS scoring. Triggered by translation_trigger.py or /translate command.
---

# Translator Skill

Translate InvestScan English outputs to Korean. English instruction → Korean output.
Reference: `.claude/agents/translator.md` (full 7-step protocol)
Model: opus (translation quality maximization — P4)

## Trigger Conditions
1. Automatic: `translation_trigger.py` writes `translation-pending.yaml` → Orchestrator spawns
2. Manual: `/translate [step|all]` command

## 7-Step Protocol (from translator.md — mandatory)

### Step 1: Load Glossary
```python
glossary = yaml.safe_load(Path("translations/glossary.yaml").read_text())
# InvestScan-specific terms take priority over general terms
```

### Step 2: Read English Source
Read the complete English source file.
Never translate partially — complete read before starting translation.

### Step 3: Translate to Korean
- Natural Korean (not translationese)
- Financial terminology: use 금감원/DART standard notation
- Preserve all numbers, units (억, %, $), and tickers exactly
- Glossary terms: mandatory use of approved Korean translations
- CATEGORY_A/B_SYSTEM_PROMPT in code files: do NOT translate (code is exempt)

### Step 4: Self-Review + pACS Scoring
Score all steps (2,4,5,11,12,15) on Ft·Ct·Nt dimensions:
- **Ft (Faithfulness)**: no meaning change, no omissions, no additions
- **Ct (Consistency)**: glossary terms used correctly throughout
- **Nt (Naturalness)**: sounds like native Korean, not translated English

Step 12 only — add **Fd (Financial Domain accuracy)**:
- PER/YoY/CAGR Korean equivalents correct
- 억/% units preserved
- 금감원/DART standard notation used
- `Translation pACS (Step 12) = min(Ft, Ct, Nt, Fd)`

Grade:
- **GREEN** (pACS ≥ 70): normal completion
- **YELLOW** (pACS 50-69): complete with warning
- **RED** (pACS < 50): must re-translate (tdd_verify.py will block TaskComplete)

### Step 5: Update Glossary
Add new InvestScan-specific terms discovered during translation:
```yaml
# translations/glossary.yaml additions
"Narrative Output": "내러티브 출력물"
"Category A Stock": "카테고리 A 종목"
"Done Gate": "완료 게이트"
```

### Step 6: Write Korean Output
`[filename].ko.md` or `[filename].ko.json`

### Step 7: Write pACS Log
```markdown
# pacs-logs/step-{N}-translation-pacs.md
Translation pACS = {score} → {GREEN|YELLOW|RED}
Ft: {ft_score} | Ct: {ct_score} | Nt: {nt_score} [| Fd: {fd_score} (Step 12 only)]
Source: {source_path}
Target: {target_path}
New glossary terms: {count}
```

### Step 8: Update Workspace
```yaml
# .claude/agent-workspace/translator.yaml
agent_id: translator
updated_at: "[ISO8601]"
current_step: {N}
translations:
  - step: {N}
    source: "{source_path}"
    target: "{target_path}"
    pacs_score: {int}
    pacs_grade: "{GREEN|YELLOW|RED}"
    glossary_terms_added: {count}
    error: ""
```

### Step 9: Return Result
```python
return {
    "pacs_score": int,
    "pacs_grade": "GREEN" | "YELLOW" | "RED",
    "new_terms": int,
    "step": N,
}
```

## What NOT to Translate
- `.py` code files (never)
- `.yaml`/`.json` configuration and data files
- `state.yaml`, `phase-*.yaml`, `agent-workspace/*.yaml`
- `CATEGORY_A/B_SYSTEM_PROMPT` (English required for LLM quality)
- Variable names, function names, field keys in code
