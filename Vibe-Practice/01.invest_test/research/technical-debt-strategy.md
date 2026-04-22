# InvestScan: Technical Debt Strategy Analysis

**Analysts**: Two Technical Debt Managers (Debt-Minimized Purist + Practical Pragmatist)
**Date**: 2026-03-27
**System Context**: Solo pastor-developer, 2-4 hrs/week, ~3,050 new LOC (Balanced Scenario B), integrating EnvironmentScan (~25,500 LOC) + GlobalNews-Crawling (~25,400 LOC) via file-based IPC. Investment decisions ride on this output.

---

## Branch 4.1: DEBT-MINIMIZED

**Philosophy**: "Clean code from day 1 -- this tool affects my money. Every shortcut in signal processing is a shortcut in investment reasoning."

**Analyst**: The Debt-Minimized Purist

### 1. Prevention Strategy

The central argument is simple: InvestScan is not a TODO app. When `synthesize_investment.py` outputs "bullish, conviction 0.72 on semiconductors," the developer may shift real capital. A magic string, a silent type coercion, or an unvalidated schema field does not produce a bug report -- it produces a bad investment decision that may not surface for weeks.

#### 1.1 Frozen Dataclasses for All Data Contracts

Every inter-stage boundary must use `@dataclass(frozen=True)`. This is non-negotiable for InvestScan because:

```python
# REQUIRED: Frozen contracts prevent accidental mutation during pipeline transit
@dataclass(frozen=True)
class UnifiedSignal:
    signal_id: str              # IS-{date}-{seq}
    source_system: str          # Literal["envscan", "gnews"]
    source_signal_id: str
    title: str
    summary: str
    detected_at: datetime
    steeps_category: str        # Literal["S", "T", "E", "E_env", "P", "s"]
    signal_layer: str           # Literal["L1_fad", "L2_short", "L3_mid", "L4_long", "L5_singularity"]
    confidence: float           # 0.0-1.0, validated
    burst_score: float          # 0.0-1.0, validated
    novelty_score: float        # 0.0-1.0, validated
    schema_version: str         # "1.0.0"
```

GlobalNews already demonstrates this pattern with its `RawArticle` frozen dataclass (14 typed fields with `to_jsonl_dict()`/`from_jsonl_dict()` serialization). InvestScan inherits this discipline.

**Why frozen matters here specifically**: If a mutable signal object passes through sector mapping, then direction scoring, then report generation, any stage could silently mutate `confidence` or `steeps_category`. In a debugging session 3 months later, tracking which stage corrupted a score is nearly impossible for a solo developer with 2-4 hours/week.

**Estimated cost**: +2-3 hours in Month 1 (schema definition). Saves an estimated 10-20 hours in Months 4-6 debugging silent data corruption.

#### 1.2 No Magic Strings -- Constants and Enums Only

```python
# constants.py -- Single source of truth for all categorical values
from enum import Enum, auto

class SourceSystem(str, Enum):
    ENVSCAN = "envscan"
    GNEWS = "gnews"

class SteepsCategory(str, Enum):
    SOCIAL = "S"
    TECHNOLOGICAL = "T"
    ECONOMIC = "E"
    ENVIRONMENTAL = "E_env"
    POLITICAL = "P"
    SECURITY = "s"

class SignalLayer(str, Enum):
    L1_FAD = "L1_fad"
    L2_SHORT = "L2_short"
    L3_MID = "L3_mid"
    L4_LONG = "L4_long"
    L5_SINGULARITY = "L5_singularity"

class Direction(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

# Scoring thresholds externalized to YAML, but referenced via typed constants
class ScoreRange:
    MIN = 0.0
    MAX = 1.0
    PSST_MIN = 0
    PSST_MAX = 100
```

**Why this matters for InvestScan specifically**: The cross-mapping between STEEPs categories and L1-L5 signal layers is the system's core analytical engine. If EnvScan outputs `"T_Technological"` but InvestScan expects `"T"`, the STEEPs classifier silently skips those signals. With ~400 Technology signals (the largest category in the EnvScan database), this single string mismatch could eliminate 50%+ of signal volume with zero error output.

EnvironmentScan's weakness is exactly this: loosely typed JSON where each agent (arxiv, blog, policy) returns different field formats merged into a flat list. InvestScan must not inherit this fragility.

**Estimated cost**: +4-5 hours in Month 1. Prevents an entire class of silent classification errors.

#### 1.3 Every Function < 50 Lines

This is a discipline rule, not a dogma. The intent: force decomposition of complex logic into named, testable units.

The primary target is `synthesize_investment.py`, which will contain the most complex logic in InvestScan (~500 LOC in Balanced Scenario B). Without the 50-line rule, the natural tendency is a 200-line `synthesize()` function that:
1. Reads unified signals
2. Maps to sectors
3. Scores directions
4. Computes conviction
5. Detects convergence
6. Generates output

With the 50-line rule, each step becomes a named function: `map_signal_to_sectors()`, `score_direction()`, `compute_conviction()`, `detect_convergence()`. When the sector mapper produces unexpected results in Month 4, you know exactly which function to examine.

**Cost for a solo developer**: Marginal. The decomposition is the design thinking you would do anyway; the rule just prevents the "I will refactor later" trap.

#### 1.4 Type Hints on Every Public Function

```python
def normalize_envscan_signal(
    raw_signal: dict[str, Any],
    schema_version: str = "1.0.0"
) -> UnifiedSignal:
    """Convert EnvScan JSON signal to unified schema.

    Raises:
        SchemaValidationError: if required fields missing or types wrong.
    """
```

Python's type system is optional at runtime, but `mypy --strict` catches:
- Passing a `str` where `float` expected (pSST score parsed from JSON as string)
- Missing fields in dict unpacking (EnvScan schema drift)
- Incompatible return types between functions

**For InvestScan specifically**: The confidence normalization (pSST 0-100 to 0.0-1.0, GlobalNews confidence 0.0-1.0 native) is the most error-prone operation. A type hint that says `confidence: float` with a `@validate(0.0, 1.0)` decorator prevents the scenario where un-normalized pSST scores (72, 85, 91) flow into averaging functions expecting values <= 1.0.

**Estimated cost**: +1 hour per module. ~8-10 hours total across InvestScan's 8 modules. Pays for itself the first time `mypy` catches a score normalization bug.

#### 1.5 100% Test Coverage on Schema Normalization Logic

Not 100% coverage of the entire codebase -- that would be absurd for a solo project. But 100% coverage specifically on:

1. **`normalize_signals.py`**: Every field mapping between EnvScan JSON and UnifiedSignal. Every field mapping between GlobalNews Parquet and UnifiedSignal. Every edge case (missing field, unexpected type, null value).

2. **`sector_mapper.py`**: Every STEEPs-to-GICS mapping rule. Every Korean market-specific mapping. Boundary conditions (signal with no clear sector, signal spanning multiple sectors).

3. **Score normalization functions**: pSST-to-confidence conversion, confidence fusion (simple average for V1), conviction calculation.

**Why 100% here and not elsewhere**: These are the functions where bugs produce **wrong investment signals with correct-looking output**. A bug in `generate_report.py` produces an ugly report. A bug in `normalize_signals.py` produces a report that says "bearish on semiconductors" when the data says "bullish." The first is cosmetic; the second costs money.

```python
# test_normalize.py -- Example test for the most critical path
class TestPSSTNormalization:
    def test_psst_to_confidence_basic(self):
        assert psst_to_confidence(0) == 0.0
        assert psst_to_confidence(100) == 1.0
        assert psst_to_confidence(72) == pytest.approx(0.72)

    def test_psst_to_confidence_boundary(self):
        with pytest.raises(ValueError):
            psst_to_confidence(-1)
        with pytest.raises(ValueError):
            psst_to_confidence(101)

    def test_psst_to_confidence_none_handling(self):
        # EnvScan signals sometimes lack pSST scores
        assert psst_to_confidence(None) == 0.5  # Default mid-confidence

    def test_envscan_signal_with_missing_category(self):
        raw = {"id": "TC-001", "title": "Test", "source": {"name": "TechCrunch"}}
        # Missing preliminary_category should not crash, should assign "UNKNOWN"
        result = normalize_envscan_signal(raw)
        assert result.steeps_category == "UNKNOWN"
```

**Estimated cost**: +15-20 hours across Months 1-3 (~100 test cases). This is the single largest investment in the Debt-Minimized approach.

### 2. Monitoring

#### 2.1 Code Complexity Metrics (radon)

```bash
# Run monthly, track trend
radon cc invest_pipeline/ -a -nc  # Cyclomatic complexity, A-F grades
radon mi invest_pipeline/ -s       # Maintainability index
```

**Threshold**: No function above CC grade C (complexity > 10). If `synthesize_investment.py` hits CC grade D, that is the signal to decompose.

For ~3,050 LOC, this takes 30 seconds to run and 5 minutes to review. Monthly cadence is sufficient.

#### 2.2 Regular Manual Code Review (Solo: Re-read After 48 Hours)

The 48-hour re-read rule: after writing a module, wait two days, then re-read it as if someone else wrote it. For a part-time developer working 2-4 hours per session, this naturally happens between work sessions.

**InvestScan-specific review checklist**:
- [ ] Are all score calculations producing values in the documented range?
- [ ] Can every direction call ("bullish"/"bearish") be traced to specific source signals?
- [ ] Are there any `.get()` calls without default values on critical fields?
- [ ] Does this function work correctly if one source system's data is missing?

#### 2.3 Refactoring Budget: 20% of Dev Time

At 2-4 hrs/week = 8-16 hrs/month. 20% = 1.6-3.2 hrs/month dedicated to refactoring.

**In practice**: One refactoring session per month (~2-3 hours). Specific targets:
- Month 2: Refactor normalize_signals.py after encountering real EnvScan/GlobalNews data quirks
- Month 3: Refactor sector_mapper.py after accumulating 4-8 weeks of mapping failures
- Month 4: Refactor synthesize_investment.py based on report quality feedback
- Month 5-6: Address whatever has accumulated the most TODO comments

### 3. Long-term Cost Projection

| Timeframe | Speed | Quality | Cumulative Effort |
|-----------|-------|---------|-------------------|
| Month 1 | **SLOW** -- schema design, enum definitions, test setup consume ~40% of dev time | HIGH -- every function typed, tested, constrained | ~28-35 hrs (vs. ~20-25 hrs for Practical) |
| Month 3 | MODERATE -- test infrastructure exists, new code writes faster | HIGH -- regressions caught by tests | ~55-65 hrs cumulative |
| Month 6 | **MAINTAINED** -- no "mystery bugs" consuming investigation time | HIGH -- confident in output accuracy | ~85-100 hrs cumulative |
| Year 1 | MAINTAINED -- refactoring budget keeps complexity managed | HIGH -- EnvScan schema changes caught immediately | ~170-200 hrs cumulative |
| Year 2 | **STILL MAINTAINED** -- codebase is familiar, tests are comprehensive | HIGH -- can modify with confidence after 2+ month gaps | ~340-400 hrs cumulative |

**Total 2-year cost**: LOWER than Practical Debt. The front-loaded investment in types, tests, and contracts pays compound returns every time:
- You return to the code after a 2-week gap (common for a pastor)
- EnvScan or GlobalNews updates their output format
- A score normalization edge case surfaces
- You want to add a new analysis module in Year 2

### 4. Specific InvestScan Debt Risks -- Prevention Strategy

#### 4.1 Schema Normalization Drift (EnvScan updates their JSON format)

**Risk**: EnvScan is actively developed. The `items[]` array has no enforced schema -- each agent returns different field sets. When a new field appears or an existing field is renamed, `normalize_signals.py` silently produces partial signals or crashes.

**Prevention**:
```python
# Schema validation on every run (fail-fast)
REQUIRED_ENVSCAN_FIELDS = {"id", "title", "source", "published_date"}
EXPECTED_ENVSCAN_FIELDS = {"preliminary_category", "summary", "metadata", "pSST_score"}

def validate_envscan_signal(raw: dict) -> tuple[bool, list[str]]:
    """Validate EnvScan signal against expected schema.

    Returns (is_valid, list_of_warnings).
    Missing required fields -> exception.
    Missing expected fields -> warning in log + default values.
    Unexpected new fields -> info log (potential schema evolution).
    """
    missing_required = REQUIRED_ENVSCAN_FIELDS - set(raw.keys())
    if missing_required:
        raise SchemaValidationError(f"EnvScan signal missing: {missing_required}")

    missing_expected = EXPECTED_ENVSCAN_FIELDS - set(raw.keys())
    unexpected = set(raw.keys()) - REQUIRED_ENVSCAN_FIELDS - EXPECTED_ENVSCAN_FIELDS

    warnings = []
    if missing_expected:
        warnings.append(f"Expected fields missing (using defaults): {missing_expected}")
    if unexpected:
        warnings.append(f"New fields detected (schema evolution?): {unexpected}")

    return (len(warnings) == 0, warnings)
```

**Cost**: ~3-4 hours. **Value**: Catches schema drift on the very next run after EnvScan changes, rather than weeks later when corrupted signals have already influenced investment thinking.

#### 4.2 Signal Classification Accuracy Degradation Over Time

**Risk**: The keyword-based STEEPs classifier for GlobalNews signals (70-80% accuracy target) may degrade as news topic vocabulary evolves. In 2026, "semiconductor" maps cleanly to T_Technological. In 2027, if "neuromorphic computing" becomes the dominant term, keyword lists become stale.

**Prevention**:
- **Classification audit log**: Every signal classification logged with the matching keywords/rules that triggered it. Monthly review of "UNKNOWN" or "low-confidence" classifications.
- **Accuracy sampling**: Once monthly, randomly sample 10 classified signals, manually verify correctness. Track accuracy rate over time.
- **Keyword refresh trigger**: If accuracy drops below 65% in monthly sample, add new keywords. If below 50%, consider ML migration (the trigger defined in the Balanced scenario refactoring plan).

**Cost**: ~1 hour/month for sampling + review. **Value**: Early warning before degraded classification corrupts investment direction calls.

#### 4.3 Report Template Rot (Stale Sections Nobody Reads)

**Risk**: The initial weekly report template includes sections defined speculatively (risk/opportunity matrix, weak signal watch, sector heat map). After 3 months of use, some sections may consistently be skipped by the reader. Stale sections waste pipeline computation and obscure useful content.

**Prevention**:
- **Usage annotation**: After reading each weekly report, spend 30 seconds annotating which sections were useful (`# USEFUL`, `# SKIPPED`) at the bottom.
- **Quarter review**: After 12 reports, count annotations. Any section marked `# SKIPPED` in 8+ of 12 reports gets removed or redesigned.
- **Template versioning**: `report-template-v1.yaml`, `report-template-v2.yaml`. Never modify in place; create a new version.

**Cost**: ~30 seconds per report + 1 hour per quarter. **Value**: The report evolves toward maximum density of useful information.

#### 4.4 Decision Journal Format Evolution (Schema Changes Break Old Entries)

**Risk**: The decision journal (append-only Markdown in Balanced) is simple initially. But as usage grows, the developer may want to add fields (actual outcome, confidence-at-decision-time, which signals were cited). Changing the format breaks parsing of old entries.

**Prevention**:
- **Version header**: Every journal entry starts with `<!-- schema: v1 -->`.
- **Additive-only changes**: New fields are optional. Parser must handle any schema version >= 1.
- **Migration script**: When schema v2 is introduced, a one-time migration script backfills old entries with default values for new fields.

**Cost**: ~1 hour for version header design. ~2 hours if/when migration is needed. **Value**: Journal entries from Month 1 remain queryable in Year 2.

### 5. Debt-Minimized Implementation Overhead Summary

| Prevention Measure | Upfront Cost (hrs) | Monthly Maintenance (hrs) | Cumulative 6-Month Cost |
|--------------------|-------------------|--------------------------|------------------------|
| Frozen dataclasses + enums | 6-8 | 0 | 6-8 |
| Type hints + mypy | 8-10 | 0.5 | 11-13 |
| 100% normalization tests | 15-20 | 2 | 27-32 |
| Schema validation | 3-4 | 0 | 3-4 |
| Code complexity monitoring | 1 | 0.5 | 4 |
| 48-hour re-read discipline | 0 | 2 | 12 |
| Refactoring budget (20%) | 0 | 2-3 | 12-18 |
| Classification accuracy sampling | 0 | 1 | 5 |
| Report template annotation | 0 | 0.2 | 1.2 |
| **TOTAL OVERHEAD** | **33-43 hrs** | **~8 hrs/month** | **~81-97 hrs** |

**Context**: Balanced Scenario B estimates 60-80 hours total for M1-M2. The Debt-Minimized overhead adds ~33-43 hours upfront, pushing the total to ~93-123 hours for M1-M2. At 3 hrs/week, this extends the M1 milestone from 8 weeks to ~11-12 weeks.

**The honest cost**: Debt-Minimized delays the first useful report by approximately 3-4 weeks. For a tool that affects investment decisions, this may be an acceptable trade.

---

## Branch 4.2: PRACTICAL DEBT

**Philosophy**: "Ship it, fix it later. The important thing is to START using it. I cannot evaluate signal quality from a report I have never produced."

**Analyst**: The Practical Pragmatist

### 1. Acceptance Strategy

The central counter-argument: InvestScan produces its first useful report in Week 7-8 under the Balanced scenario. Every hour spent on preventive infrastructure is an hour NOT spent on producing that report. And until the first report exists, every design decision is speculative.

The developer does not yet know:
- Which STEEPs categories actually produce useful investment signals (maybe only T and E matter)
- Whether pSST scores from EnvScan correlate meaningfully with GlobalNews confidence scores
- Whether the sector mapping rules are even approximately right
- Whether the weekly report format is readable and actionable

Spending 33-43 hours on schema validation, type hints, and test coverage for logic that may be wrong from the start is a specific kind of waste: **premature correctness**.

#### 1.1 TODO Comments for Known Shortcuts

```python
def normalize_psst(score):
    # TODO(debt): validate range, handle None, add type hints
    # For now: simple division. If score > 100, cap at 1.0
    return min(score / 100, 1.0) if score else 0.5

def classify_steeps(title, summary):
    # TODO(debt): replace keyword matching with ML classifier when accuracy drops
    # TODO(debt): add type hints and return type
    keywords = {
        "T": ["AI", "semiconductor", "quantum", "robot", "chip", "neural"],
        "E": ["GDP", "inflation", "trade", "tariff", "employment", "rates"],
        # ... (hardcoded, not externalized to YAML)
    }
    for category, words in keywords.items():
        if any(w.lower() in (title + " " + summary).lower() for w in words):
            return category
    return "UNKNOWN"
```

Every shortcut is marked with `# TODO(debt):` and a rationale. This is not laziness; it is **explicit deferral**. The developer knows exactly what to fix and when.

#### 1.2 Hardcoded Values Acceptable for V1 (Refactor When It Hurts)

| Hardcoded Value | Where | Refactor Trigger |
|----------------|-------|------------------|
| STEEPs keyword lists | `steeps_classifier.py` | When accuracy sampling shows < 65% |
| Sector mapping rules | `sector_mapper.py` | When weekly report mismaps > 3 signals obviously |
| pSST-to-L-layer thresholds (0-30, 30-60, etc.) | `normalize_signals.py` | When EnvScan pSST distribution shifts |
| Korean market sector weights | `korean_market_scorer.py` | Quarterly, aligned with KOSPI sector rebalancing |
| Report template sections | `generate_report.py` | After 8 weeks of reading reports |
| TF-IDF similarity threshold (0.85) | `normalize_signals.py` | When dedup misses obvious duplicates or merges distinct signals |

**The principle**: Hardcoding is acceptable when the correct value is unknown and can only be discovered through use. Externalizing to YAML before knowing the right value is premature abstraction.

#### 1.3 Minimal Typing (Python is Dynamically Typed -- Use It)

Type hints on the 3-4 most critical functions only:
- `normalize_envscan_signal(raw: dict) -> dict` -- the bridge between systems
- `normalize_gnews_signal(row: dict) -> dict` -- the other bridge
- `score_direction(signals: list[dict]) -> dict` -- the investment output

Everything else: plain Python. If a function is < 20 lines and its purpose is obvious from the name, type hints are documentation overhead that slows iteration.

**Counter to Debt-Minimized argument**: `mypy --strict` on 8 modules adds ~8-10 hours of initial effort and catches bugs that may never occur in practice. For a 3,050 LOC project with a single developer, the developer IS the type checker -- they know the types because they wrote the code last week.

#### 1.4 Test Only What is Obviously Critical (Normalization Math)

Tests for:
- pSST-to-confidence conversion (5-10 test cases)
- Confidence fusion (average of two scores -- 3-5 test cases)
- Direction scoring output format (valid JSON, required fields present)

NOT tested:
- Report generation (visual output, test by reading)
- CLI argument parsing (test by running)
- Config loading (test by running)
- Sector mapping accuracy (validated by reading reports, not unit tests)
- STEEPs classification (validated by monthly sampling, not automated tests)

**Estimated test effort**: ~5-8 hours total (vs. ~15-20 hours for Debt-Minimized). ~20-30 test cases (vs. ~100+).

### 2. Tracking

#### 2.1 TODO Comments in Code (grep-searchable)

```bash
# Monthly debt inventory
grep -rn "TODO(debt)" invest_pipeline/ | wc -l
grep -rn "TODO(debt)" invest_pipeline/ | sort
```

Simple. Zero infrastructure. Works in any editor. A solo developer does not need Jira.

#### 2.2 Monthly "Debt Day" -- 2 Hours Fixing TODOs

One session per month, ~2 hours. Process:
1. `grep -rn "TODO(debt)" invest_pipeline/` -- list all debt
2. Sort by impact on investment decision quality
3. Fix the top 2-3 items
4. Leave the rest for next month

**Prioritization rule**: Fix debt that affects investment output accuracy first. Fix debt that affects code maintainability second. Fix debt that affects code aesthetics never.

#### 2.3 Prioritize by Impact on Investment Decisions

| Debt Category | Priority | Example |
|--------------|----------|---------|
| **Score calculation errors** | P0 -- fix immediately | pSST normalization producing values > 1.0 |
| **Classification errors** | P1 -- fix within 1 week | STEEPs classifier assigning "S" to technology signals |
| **Silent data loss** | P1 -- fix within 1 week | GlobalNews Parquet reader skipping rows with null fields |
| **Report formatting** | P3 -- fix on debt day | Markdown table misalignment |
| **Code style** | P4 -- fix if bored | Inconsistent variable naming |
| **Missing type hints** | P5 -- maybe never | Functions that work correctly without them |

### 3. Long-term Cost Projection

| Timeframe | Speed | Quality | Cumulative Effort |
|-----------|-------|---------|-------------------|
| Month 1 | **FAST** -- no test infrastructure, no type checking, ship features | ACCEPTABLE -- hardcoded values work for known cases | ~18-22 hrs |
| Month 3 | FAST -- still shipping features, debt is manageable | ACCEPTABLE -- monthly sampling catches major classification errors | ~40-48 hrs |
| Month 6 | **DECLINING** -- "where is this hardcoded?" questions consume 30-40% of debugging time | DECLINING -- edge cases in normalization produce occasional wrong signals | ~65-80 hrs |
| Year 1 | SLOW -- every change requires tracing through untyped functions to understand data flow | CONCERNING -- EnvScan schema change causes 2-week debugging session | ~160-200 hrs |
| Year 2 | **SIGNIFICANTLY SLOWER** -- unless major refactoring (20-30 hrs) performed | UNCERTAIN -- accumulated shortcuts interact unpredictably | ~380-480 hrs (includes refactoring) |

**Total 2-year cost**: HIGHER than Debt-Minimized, but **front-loaded delivery**. The first useful report arrives 3-4 weeks earlier. Whether those 3-4 weeks matter depends on market conditions, not engineering principles.

**The honest trajectory**: By Month 9-12, Practical Debt accumulates approximately 40-60 TODO comments. The codebase becomes a minefield of "I know this is wrong but it works." For a solo developer who may have a 3-week gap between sessions (pastor's schedule), re-entering this codebase becomes increasingly painful. The 48-hour re-read rule of Debt-Minimized is a luxury; in Practical Debt, you may return after 21 days and spend the entire session just remembering how things work.

### 4. Specific InvestScan Debt Risks -- Acceptance Strategy

#### 4.1 Schema Normalization Drift (EnvScan updates their JSON format)

**Accepted risk**. Defensive parsing with `.get()` and defaults:

```python
def normalize_envscan_signal(raw):
    return {
        "signal_id": f"IS-{date}-{seq}",
        "source_system": "envscan",
        "title": raw.get("title", "UNTITLED"),
        "steeps_category": raw.get("preliminary_category", "UNKNOWN"),
        "confidence": (raw.get("pSST_score", 50) or 50) / 100,
        # ... no validation, no schema check, just defaults
    }
```

**When it breaks**: The pipeline produces signals with `"UNTITLED"` and `"UNKNOWN"`. The developer notices in the weekly report and fixes the parser. Estimated fix time: 1-2 hours. Estimated detection time: within 1 week (next report run).

**Accepted downside**: One week of degraded report quality. For a personal tool run weekly, this is acceptable.

#### 4.2 Signal Classification Accuracy Degradation Over Time

**Accepted risk**. The keyword-based classifier will degrade. But:
- The developer reads every report and will notice when "AI chip breakthrough" is classified as "UNKNOWN"
- Manual correction (adding a keyword) takes 5 minutes
- The degradation is gradual, not catastrophic
- ML migration is the planned refactoring trigger (Month 7+ per analysis-monolithic-architecture.md)

**Key question for InvestScan**: Is 70% classification accuracy good enough for investment direction? The Practical Pragmatist says YES -- because the developer applies human judgment on top. InvestScan is a telescope, not an autopilot. Misclassifying 30% of signals is noise, but the 70% correctly classified signals still provide value. No investment decision is made solely on InvestScan output.

#### 4.3 Report Template Rot

**Accepted risk**. The report template will have sections nobody reads. The developer will simply skip them. When the annoyance threshold is crossed, they will edit the template. No tracking mechanism needed -- the irritation IS the tracking mechanism.

#### 4.4 Decision Journal Format Evolution

**Accepted risk**. Start with plain Markdown. If the format needs to change, just change it. Old entries are still readable text even if the parser cannot parse them. A migration script can be written in 30 minutes when actually needed.

### 5. Practical Debt Implementation Timeline

| Month | Feature Work (hrs) | Debt Created | Debt Paid | Net Debt |
|-------|-------------------|-------------|-----------|----------|
| 1 | ~20 hrs -- full pipeline working | ~15 TODOs | 0 | 15 |
| 2 | ~16 hrs -- STEEPs + synthesis + report | ~12 TODOs | 0 | 27 |
| 3 | ~12 hrs -- convergence + polish | ~8 TODOs | ~5 (debt day) | 30 |
| 4 | ~10 hrs -- confidence calibration + health | ~5 TODOs | ~5 (debt day) | 30 |
| 5 | ~8 hrs -- conditional features | ~3 TODOs | ~8 (debt day) | 25 |
| 6 | ~6 hrs -- hardening + docs | ~2 TODOs | ~10 (debt day) | 17 |

**Peak debt at Month 3-4**: ~30 TODO comments. This is manageable for 3,050 LOC (approximately 1 TODO per 100 lines). Above 50 TODOs would signal a problem.

---

## COMPARISON: The InvestScan-Specific Tension

### The Unique Dilemma

InvestScan sits at the intersection of two normally opposing forces:

**Force 1: Personal Tool Dynamics** -- Favor Practical Debt
- Solo developer, no team to confuse
- The developer IS the user -- they know the quirks
- No external API, no SLA, no uptime requirements
- If it breaks, the only cost is a skipped weekly report
- Python's dynamic typing is a feature for rapid iteration
- "Ship it and learn" is how personal tools evolve

**Force 2: Financial Decision Consequences** -- Favor Debt-Minimized
- Investment decisions based on output (errors have monetary cost)
- Signal misclassification is invisible in the output (looks correct, is wrong)
- Confidence scores feel precise but may be arbitrary (garbage in, garbage out)
- The developer reads the report and trusts the numbers -- this trust must be earned
- A 2-week gap between sessions means "I will remember how this works" is unreliable
- Schema drift between source systems is not hypothetical -- both are actively developed

### The Critical Question: What Type of Error Has Financial Consequences?

Not all technical debt creates financial risk. The debt that matters for InvestScan:

| Debt Type | Financial Risk | Example |
|-----------|---------------|---------|
| **Score normalization error** | **HIGH** | pSST=85 rendered as confidence=8.5 (not divided by 100). Appears as extreme high conviction. Developer over-allocates to that sector. |
| **STEEPs misclassification** | **MEDIUM** | Technology signal classified as Economic. Sector mapping puts it in wrong sector. Weekly direction for Tech sector is weaker than reality. |
| **Silent data loss** | **HIGH** | Parquet reader skips rows with null `signal_layer`. 20% of GlobalNews signals lost. Report under-represents coverage areas. |
| **Dedup over-matching** | **LOW-MEDIUM** | TF-IDF threshold too low: distinct signals merged. Reduces signal count but does not corrupt direction. |
| **Report formatting bug** | **NONE** | Ugly table. No financial impact. |
| **Missing type hint** | **NONE** | Code works the same whether typed or not. |
| **Hardcoded threshold** | **LOW** | pSST 30/60/80/95 boundaries for L-layer mapping. Approximate is fine; the mapping is heuristic anyway. |

**Conclusion**: Only 3 categories of debt have meaningful financial risk: score normalization, classification, and data loss. Everything else is engineering preference.

### The Recommended Synthesis: Hybrid Approach

Neither pure Debt-Minimized nor pure Practical Debt is optimal for InvestScan. The right strategy is **targeted prevention on the financial-risk debt, practical acceptance everywhere else**.

#### Prevent (Debt-Minimized Rules Apply):

| Measure | Why | Cost |
|---------|-----|------|
| Frozen dataclass for `UnifiedSignal` | Prevents mutation of scores during pipeline transit | +2 hrs |
| Enums for STEEPs, SignalLayer, Direction | Prevents magic string mismatches between EnvScan and InvestScan | +3 hrs |
| Range validation on all 0-1 scores | Catches normalization errors before they reach the report | +2 hrs |
| Schema validation on EnvScan JSON input | Catches schema drift on first run after source update | +3 hrs |
| Tests for normalization math (30-40 cases) | Catches the highest-financial-risk bugs | +8 hrs |
| **Subtotal** | | **+18 hrs** |

#### Accept (Practical Debt Rules Apply):

| Shortcut | Why Acceptable | Future Cost |
|----------|---------------|-------------|
| No type hints except on normalization functions | Other functions are low-risk | ~4 hrs to add later if needed |
| Hardcoded sector mapping keywords | Correct values unknown until real usage | ~2 hrs to externalize |
| Hardcoded scoring thresholds | Heuristic values, not precision-critical | ~1 hr to externalize |
| No tests for report generation | Visual output, tested by reading | ~4 hrs to add if format stabilizes |
| No tests for CLI | Tested by running | ~2 hrs to add if CLI grows |
| No complexity monitoring (radon) | 3,050 LOC is small enough to read entirely | ~1 hr to set up if codebase doubles |
| Simple Markdown for decision journal | Migration script is 30 min if format changes | ~0.5 hrs |
| TODO comments instead of formal debt tracking | Solo developer, grep is sufficient | ~0 hrs |

#### The Hybrid Cost

| Approach | M1-M2 Cost (hrs) | 6-Month Total (hrs) | 2-Year Total (hrs) |
|----------|-------------------|--------------------|--------------------|
| Pure Debt-Minimized | 93-123 | 85-100 monthly effort | 340-400 |
| Pure Practical | 58-72 | 65-80 monthly effort | 380-480 |
| **Hybrid** | **76-98** | **75-90 monthly effort** | **300-370** |

The Hybrid adds ~18 hours of targeted prevention to the Practical approach, which:
- Delays the first report by ~1-2 weeks (not 3-4 weeks like pure Debt-Minimized)
- Prevents the 3 highest-financial-risk debt categories
- Accepts all low-risk debt as Practical recommends
- Results in the lowest 2-year total cost

### Final Verdict from Both Analysts

**Debt-Minimized Purist**: "I accept the Hybrid. The frozen dataclass, enums, range validation, and normalization tests are non-negotiable for a system that influences investment decisions. The rest -- type hints on utility functions, tests for report formatting, complexity monitoring -- I concede are premature for a 3,050 LOC personal tool."

**Practical Pragmatist**: "I accept the Hybrid. The 18 hours of targeted prevention is justified because score normalization errors and silent data loss are invisible in the output. I cannot debug what I cannot see. For everything else -- hardcoded values, minimal typing, TODO-based tracking -- the 'ship and iterate' approach is correct for a solo developer discovering what works."

**The unified recommendation**: Invest in prevention exactly where bugs are invisible and financially consequential. Accept debt everywhere else. Track debt with grep-able TODOs. Reassess at Month 6 when real usage data reveals which shortcuts actually hurt.

---

## Appendix: Decision Matrix

| Decision Point | Debt-Minimized | Practical | Hybrid (Recommended) |
|---------------|---------------|-----------|---------------------|
| Data contracts | Frozen dataclasses, all stages | Plain dicts | **Frozen dataclass for UnifiedSignal only** |
| Enums | All categorical values | None (strings) | **STEEPs, SignalLayer, Direction, SourceSystem** |
| Type hints | Every public function | 3-4 critical functions | **Normalization + synthesis functions** |
| Tests | 100+ cases, 100% normalization coverage | 20-30 cases, math only | **40-50 cases, normalization + score validation** |
| Schema validation | Every field, every run | .get() with defaults | **Required fields validated, expected fields default** |
| Score range validation | Decorator-based, compile-time | None (trust the math) | **Runtime assertion on 0-1 range** |
| Complexity monitoring | Monthly radon runs | None | **None (reassess at 5,000+ LOC)** |
| Refactoring budget | 20% of dev time | Monthly 2-hr debt day | **Monthly 2-hr debt day + ad-hoc when scores look wrong** |
| Config externalization | All values in YAML from day 1 | Hardcoded, refactor when painful | **Hardcoded, refactor when painful** |
| Decision journal schema | Versioned from day 1 | Plain Markdown | **Plain Markdown with version header** |
| Test coverage target | 100% normalization | "what is obviously critical" | **100% score normalization, 80% signal parsing** |
