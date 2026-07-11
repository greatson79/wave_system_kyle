# Round 5: External Integration — PHASE 2 + 3 + 4

**Supreme External Integration Moderator**
**Date**: 2026-03-28
**Input**: 5 Phase 1 Branch analyses (Data Sources, Multi-Model CLI, Output/Notification, External Toolchain, Documentation)
**Context**: InvestScan Scenario B (BALANCED), solo dev, pastor, 2-4 hrs/week, MacBook M5 Max 64GB, ~2,710 LOC total budget

---

# PHASE 2: Four Integration Perspectives

## 2.A: Maximum Capability Perspective

**Question**: If we use every external integration available, what is the theoretical ceiling?

### Full Integration Inventory

| Category | Integration | Library/Tool | Auth | LOC | Weekly Runtime |
|----------|------------|-------------|------|-----|----------------|
| **Data: Korean Market** | KOSPI/KOSDAQ indices + sector indices | `pykrx` | None (web scrape) | ~60 | 30s |
| **Data: Global Market** | S&P500, NASDAQ, DJI, FX, Commodities, Treasury | `finance-datareader` | None | ~90 | 45s |
| **Data: Macro** | FRED indicators (GDP, CPI, unemployment, Fed rate) | `fredapi` | Free API key | ~40 | 15s |
| **Data: Trends** | Google Trends for sector keywords | `pytrends` | None | ~35 | 20s |
| **AI: Primary** | Orchestration, synthesis, Korean translation | Claude Code (native) | Subscription | 0 (native) | N/A |
| **AI: Long-context** | 10-K filing analysis, fact verification | Gemini CLI (subprocess) | Google OAuth | ~50 | 28s/call |
| **AI: Structured** | JSON classification, web search, risk scoring | Codex CLI (subprocess) | ChatGPT sub | ~60 | 3s/call |
| **Output: Notification** | Mobile push with summary + file attachment | Telegram Bot | Bot token (permanent) | ~85 | 2s |
| **Output: Email** | Full report delivery with PDF attachment | Gmail SMTP | App password (permanent) | ~55 | 3s |
| **Output: Dashboard** | Interactive browser-based report viewer | Streamlit + Plotly | None | ~300 | N/A (on-demand) |
| **Output: PDF** | Archival-quality report export | WeasyPrint + NanumGothic | None | ~110 | 5s |
| **Output: KakaoTalk** | Korean messaging notification | PyKakao | OAuth (30-day expiry) | ~65 | 2s |
| **Scheduling** | Automatic Sunday 8 PM execution | launchd plist | None | ~40 (XML) | N/A |
| **Logging** | Rotating log files with structured output | `RotatingFileHandler` | None | ~30 | N/A |
| **Storage** | WAL-mode SQLite for decision journal | stdlib `sqlite3` | None | ~40 | N/A |
| **Backup** | Pre-run data copy to timestamped directory | Shell script | None | ~20 | 10s |
| **Export** | JSONL signal archive for future analytics | stdlib `json` | None | ~15 | 5s |

### Capability Ceiling

- **15 external data feeds** (5 Korean sector indices, 4 global indices, 4 FX rates, 3 commodities, 3 Treasury yields + FRED macro)
- **3 AI models** providing cross-validation, long-context analysis, and live web search
- **4 output channels** (Telegram push, email archive, browser dashboard, PDF export)
- **Automated weekly execution** with logging, backup, and decision journaling
- **Total LOC**: ~1,095 for external integrations alone (40% of 2,710 budget)
- **Setup time**: ~12 hours
- **Monthly maintenance**: ~3 hours (dominated by KakaoTalk token refresh + CLI version updates + Streamlit dependency management)

### The Ceiling Assessment

At maximum capability, InvestScan would be a genuinely professional-grade investment intelligence system. The multi-model cross-validation alone elevates output quality significantly -- Gemini catches facts Claude misses, GPT provides structured classifications with live market data, and Claude synthesizes everything into coherent Korean reports.

**But the ceiling is not the target.** The marginal value of the 12th integration is far lower than the 3rd. The question is where diminishing returns begin.

---

## 2.B: Minimum Viable Integration Perspective

**Question**: What is the absolute minimum external connection set for a useful investment report?

### The Irreducible Core

For InvestScan to produce an investment direction report that is **meaningfully better than reading the news yourself**, it needs exactly three things:

1. **Signal data** -- Already exists (EnvironmentScan + GlobalNews-Crawling outputs, read from local files)
2. **Market price context** -- One library that answers "what has the market already priced in?"
3. **AI synthesis** -- One model to reason across signals and produce direction calls

### Minimum Stack

| Component | Integration | Library | LOC | Justification |
|-----------|------------|---------|-----|---------------|
| Market data | KOSPI + S&P500 + USD/KRW + basic FX | `finance-datareader` | ~90 | Single library covers Korean + global + FX + commodities. No API key. |
| AI model | Claude Code (native) | -- | 0 | Already running. Does everything: reasoning, synthesis, Korean, JSON output. |
| Output | Write `.md` file to `output/{date}/` | stdlib | ~10 | File on disk. User opens in editor/browser. |
| Scheduling | Manual or simple cron one-liner | cron | ~1 | `0 20 * * 0 cd /path && .venv/bin/python -m investscan run` |

**Total external integration LOC**: ~101
**Total setup time**: ~30 minutes (install finance-datareader, run once)
**Monthly maintenance**: ~0 hours (finance-datareader has no auth to expire, cron is set-and-forget)

### What You Lose

- No Korean sector indices (pykrx) -- you know KOSPI moved but not which sectors
- No FRED macro data -- you miss the rate environment framing
- No mobile notification -- you must remember to check the file
- No multi-model validation -- single perspective from Claude
- No dashboard -- reading raw Markdown only
- No decision journal -- no tracking of prediction accuracy

### What You Still Get

A weekly Markdown report that reads EnvironmentScan + GlobalNews signals, checks them against actual market prices (KOSPI, S&P500, major FX), and synthesizes investment direction calls per STEEPs category with Claude reasoning. This is already a substantial analytical product for a solo investor.

---

## 2.C: Reliability Priority Perspective

**Question**: Which integrations are most likely to break? Rank every integration by fragility.

### Fragility Ranking (Most Fragile to Most Robust)

| Rank | Integration | Fragility | Primary Failure Mode | MTTR | Impact of Failure |
|------|------------|-----------|---------------------|------|-------------------|
| 1 (MOST FRAGILE) | **KakaoTalk (PyKakao)** | CRITICAL | OAuth token expires every 30 days; pipeline pause > 30 days = manual re-auth via browser | 15-30 min | Notification channel lost |
| 2 | **pykrx** | HIGH | Web-scraping KRX/Naver -- any HTML structure change breaks parsing; library maintainer must patch | Hours to weeks (upstream) | Korean sector indices unavailable |
| 3 | **Google Trends (pytrends)** | HIGH | Google actively blocks automated Trends access; rate limits are aggressive and undocumented; 429 errors common | Minutes (retry) to permanent | Trend context lost |
| 4 | **Gemini CLI** | MEDIUM-HIGH | CLI version updates may change JSON output structure; OAuth token can require re-auth in non-TTY environments | 10-30 min | Long-context analysis falls back to Claude |
| 5 | **Codex CLI** | MEDIUM | CLI version updates; ChatGPT subscription tier changes; output format shifts between versions | 10-30 min | Structured classification falls back to Claude |
| 6 | **fredapi** | MEDIUM-LOW | FRED API key is free but rate-limited (120 req/min); API occasionally returns 503 during maintenance | Minutes (retry) | Macro indicators use cached values |
| 7 | **WeasyPrint** | MEDIUM-LOW | Complex C library dependencies; macOS updates occasionally break the build chain | 30-60 min | PDF generation fails; Markdown report still available |
| 8 | **Streamlit** | LOW-MEDIUM | Dependency chain is large (Streamlit + Plotly + pandas); version conflicts possible during upgrades | 15-30 min | Dashboard unavailable; report files still readable |
| 9 | **FinanceDataReader** | LOW | Multiple backends (KRX, Naver, Yahoo); if one fails, others may still work; 8+ years battle-tested | Minutes (retry) | Market data temporarily unavailable |
| 10 | **Telegram Bot** | LOW | Token never expires; API is extremely stable (no changes since Bot API 6.0); timeout-only failure mode | 1-2 min (retry) | Notification delayed |
| 11 | **Gmail SMTP** | LOW | App passwords never expire; SMTP protocol is 40+ years old; only fails if Google account is suspended | 1-2 min (retry) | Email delayed |
| 12 | **launchd** | VERY LOW | macOS native; survives OS updates; only fails if plist XML is malformed | 5 min | Scheduled run missed; manual trigger works |
| 13 | **SQLite** | VERY LOW | Stdlib; WAL mode is production-proven; corruption only from hardware failure | N/A | Decision journal uses new file |
| 14 (MOST ROBUST) | **Claude Code** | VERY LOW | Subscription-based; already the runtime environment; failure = entire session is down anyway | N/A | Everything stops |

### Reliability Zones

**Green Zone (reliable -- set and forget):**
- Claude Code (native), SQLite, launchd, Telegram Bot, Gmail SMTP, FinanceDataReader

**Yellow Zone (occasional attention needed):**
- Gemini CLI, Codex CLI, fredapi, Streamlit, WeasyPrint

**Red Zone (regular maintenance burden):**
- KakaoTalk (PyKakao), pykrx (web scraper), pytrends (Google blocking)

---

## 2.D: Maintenance Priority Perspective

**Question**: What is the ongoing maintenance cost per integration?

### Maintenance Burden Ranking (Highest to Lowest)

| Integration | Setup (one-time) | Monthly Maintenance | Annual Total | Maintenance Activities |
|-------------|-----------------|-------------------|-------------|----------------------|
| **KakaoTalk** | 30 min | 30 min/month | 6.5 hrs/yr | Token refresh, OAuth re-auth if pipeline pauses, API changes |
| **Streamlit Dashboard** | 2 hrs | 20 min/month | 6 hrs/yr | Dependency updates (Streamlit releases monthly), Plotly version sync |
| **Gemini CLI** | 1 hr | 15 min/month | 4 hrs/yr | CLI updates (npm), output format changes, OAuth credential refresh |
| **Codex CLI** | 1 hr | 15 min/month | 4 hrs/yr | CLI updates (npm), output format changes, subscription tier checks |
| **WeasyPrint (PDF)** | 45 min | 10 min/month | 2.75 hrs/yr | Rebuild after macOS updates, font path changes, CSS tweaks |
| **pykrx** | 15 min | 10 min/month | 2.25 hrs/yr | Monitor for scraping breakage, update after KRX site changes |
| **pytrends** | 15 min | 10 min/month | 2.25 hrs/yr | Adjust for Google blocking patterns, retry tuning |
| **fredapi** | 10 min | 5 min/month | 1.17 hrs/yr | API key renewal check (never expires but good practice) |
| **FinanceDataReader** | 10 min | 5 min/month | 1.17 hrs/yr | Version updates, backend changes |
| **Telegram Bot** | 5 min | 0 min/month | 0.08 hrs/yr | Essentially zero -- token is permanent |
| **Gmail SMTP** | 5 min | 0 min/month | 0.08 hrs/yr | Essentially zero -- app password is permanent |
| **launchd** | 15 min | 0 min/month | 0.25 hrs/yr | Only touched during OS major upgrades |
| **SQLite** | 0 min | 0 min/month | 0 hrs/yr | Zero maintenance |
| **Claude Code** | 0 min | 0 min/month | 0 hrs/yr | Already maintained as primary tool |

### Maintenance Budget Reality Check

**User constraint**: 2-4 hours/week total for InvestScan, including running it, reviewing reports, and making investment decisions.

- **Full integration maintenance**: ~31 hrs/yr = ~2.6 hrs/month = ~40 min/week just on maintenance
- **Balanced integration maintenance**: ~12 hrs/yr = ~1 hr/month = ~15 min/week on maintenance
- **Minimal integration maintenance**: ~1.3 hrs/yr = negligible

At 2-4 hrs/week total, **full integration would consume 17-33% of available time on maintenance alone**. This is unacceptable for a solo dev who also needs to review reports and make actual investment decisions.

---

## Unified Integration Zone Table

This table synthesizes all four perspectives into a single Green/Yellow/Red classification.

| Integration | Capability Value | Minimum Viable? | Reliability | Maintenance | **ZONE** | **Verdict** |
|------------|-----------------|-----------------|-------------|-------------|----------|-------------|
| **Claude Code** | ESSENTIAL | YES | Green | Green | **GREEN** | Core. Non-negotiable. |
| **FinanceDataReader** | ESSENTIAL | YES | Green | Green | **GREEN** | Core. Single best data library. |
| **Telegram Bot** | HIGH | No (but near-essential) | Green | Green | **GREEN** | Include. 5 min setup, zero maintenance, permanent. |
| **Gmail SMTP** | MODERATE | No | Green | Green | **GREEN** | Include. Archival email for record-keeping. |
| **launchd** | HIGH | No (cron as fallback) | Green | Green | **GREEN** | Include. macOS native, reliable, set-and-forget. |
| **SQLite** | MODERATE | No | Green | Green | **GREEN** | Include. Decision journal is P1 feature. |
| **pykrx** | HIGH | No | Yellow-Red | Yellow | **YELLOW** | Defer to M2. Korean sector indices are valuable but fragile. |
| **fredapi** | MODERATE | No | Yellow | Green | **YELLOW** | Defer to M2. Macro framing is useful but not essential for M1. |
| **Gemini CLI** | MODERATE-HIGH | No | Yellow | Yellow | **YELLOW** | Defer to M3+. Only needed for 10-K filings or fact-checking. |
| **Codex CLI** | MODERATE | No | Yellow | Yellow | **YELLOW** | Defer to M3+. Only needed for live web search or schema validation. |
| **Streamlit** | MODERATE | No | Yellow | Yellow | **YELLOW** | Defer to M3+. Nice-to-have visualization. |
| **WeasyPrint (PDF)** | LOW-MODERATE | No | Yellow | Yellow | **YELLOW** | Defer to M4+. Markdown is sufficient for solo user. |
| **KakaoTalk** | LOW | No | Red | Red | **RED** | SKIP. 200-char limit + 30-day token expiry. Telegram is strictly better. |
| **pytrends** | LOW | No | Red | Yellow | **RED** | SKIP. Google actively blocks; unreliable for automated pipeline. |

### Zone Summary

- **GREEN (6 items)**: Include in Month 1. Total LOC: ~280. Setup: ~1.5 hours. Maintenance: ~0 hrs/month.
- **YELLOW (6 items)**: Phase in over Months 2-4+. Total LOC: ~655. Setup: ~6 hours. Maintenance: ~1.5 hrs/month.
- **RED (2 items)**: Do not implement. Negative ROI.

---

# PHASE 3: Three Integration Scenarios

## 3.A: Full Integration Scenario

**Profile**: All data sources + 3 AI models + Telegram + Email + Streamlit + PDF + launchd

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    FULL INTEGRATION SCENARIO                     │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ EnvironmentScan│ │ GlobalNews   │  │ External Data │          │
│  │ (116+ sources) │ │ (8-stage NLP)│  │ Sources (5)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         │    ┌─────────────┴──────────────────┘                  │
│         │    │                                                    │
│  ┌──────▼────▼──────────────────────────────────────────────┐   │
│  │              investscan/ Python Package                    │   │
│  │  normalize → synthesize → report → distribute             │   │
│  └─────────┬──────────┬──────────┬──────────┬───────────────┘   │
│            │          │          │          │                     │
│     ┌──────▼──┐ ┌─────▼────┐ ┌──▼───┐ ┌───▼──────┐            │
│     │ Gemini  │ │ Codex/GPT│ │Claude│ │ Claude   │            │
│     │ (verify)│ │ (classify)│ │(synth)│ │(translate)│           │
│     └─────────┘ └──────────┘ └──────┘ └──────────┘            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Output Channels                        │   │
│  │  Telegram │ Email (Gmail) │ Streamlit │ PDF │ Markdown   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Scheduling: launchd (Sunday 8 PM)                              │
│  Storage: SQLite (WAL) + JSONL archive                          │
│  Logging: RotatingFileHandler                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Metrics

| Metric | Value |
|--------|-------|
| **External integration LOC** | ~935 |
| **Remaining LOC for core pipeline** | ~1,775 (of 2,710) |
| **Setup time** | ~10 hours |
| **Monthly maintenance** | ~2.5 hours |
| **Weekly pipeline runtime** | ~5-8 minutes (data fetch + 3 AI models + distribution) |
| **External dependencies** | 12 pip packages + 2 npm CLIs + 1 launchd plist |
| **Failure modes** | 14 distinct (one per integration) |
| **Authentication credentials** | 4 (.env: Gmail app password, FRED API key, Telegram bot token + chat ID) |

### Data Source Breakdown

| Source | Library | LOC | Auth | Phase |
|--------|---------|-----|------|-------|
| KOSPI/KOSDAQ + FX + Global + Commodities + Treasury | `finance-datareader` | 90 | None | M1 |
| 22 KRX sector indices | `pykrx` | 60 | None | M2 |
| FRED macro indicators | `fredapi` | 40 | Free API key | M2 |
| Google Trends keywords | `pytrends` | 35 | None | SKIP (Red zone) |

### AI Model Breakdown

| Model | Method | LOC | Auth | Phase |
|-------|--------|-----|------|-------|
| Claude Code | Native (orchestrator) | 0 | Subscription | M1 |
| Gemini 2.5 Pro | subprocess | 50 | Google OAuth | M3+ |
| GPT-5.4 (Codex) | subprocess | 60 | ChatGPT subscription | M3+ |
| Multi-model orchestrator | Python class | 80 | -- | M3+ |
| Error handling + retry | Python decorator | 60 | -- | M3+ |

### Output Channel Breakdown

| Channel | Library | LOC | Auth | Phase |
|---------|---------|-----|------|-------|
| Telegram Bot | `requests` | 85 | Bot token (permanent) | M1 |
| Gmail SMTP | stdlib `smtplib` | 55 | App password (permanent) | M1 |
| Streamlit Dashboard | `streamlit` + `plotly` | 300 | None | M3+ |
| PDF Export | `weasyprint` | 110 | None | M4+ |
| Markdown file | stdlib | 10 | None | M1 |

### Full Scenario Verdict

**Overkill for Month 1 but the correct long-term target.** The full scenario is what InvestScan should look like at Month 6. Building it all at once is incompatible with 2-4 hrs/week. The risk is that 14 simultaneous failure modes make debugging a nightmare for a solo developer.

---

## 3.B: Balanced Integration Scenario (RECOMMENDED)

**Profile**: Essential data + Claude primary (Gemini/Codex scaffolded but not active) + Telegram + Email + launchd

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                  BALANCED INTEGRATION SCENARIO                   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ EnvironmentScan│ │ GlobalNews   │  │FinanceData-  │          │
│  │ (local files) │ │ (local files)│  │Reader (1 lib)│          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│  ┌──────▼──────────────────▼──────────────────▼─────────────┐   │
│  │              investscan/ Python Package                    │   │
│  │  normalize → synthesize → report → distribute             │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│                    ┌────▼────┐                                   │
│                    │ Claude  │  (sole AI model in M1-M2)        │
│                    │ (native)│                                   │
│                    └────┬────┘                                   │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │              Output Channels                              │   │
│  │  Telegram (push) │ Email (archive) │ Markdown (file)     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Scheduling: launchd (Sunday 8 PM)                              │
│  Storage: SQLite (WAL) decision journal                         │
│  Logging: RotatingFileHandler                                   │
│  Future-ready: Gemini/Codex wrappers exist but inactive         │
└──────────────────────────────────────────────────────────────────┘
```

### Metrics

| Metric | Value |
|--------|-------|
| **External integration LOC** | ~420 |
| **Remaining LOC for core pipeline** | ~2,290 (of 2,710) |
| **Setup time** | ~2.5 hours |
| **Monthly maintenance** | ~15 minutes |
| **Weekly pipeline runtime** | ~2-3 minutes (data fetch + Claude synthesis + distribution) |
| **External dependencies** | 4 pip packages + 1 launchd plist |
| **Failure modes** | 6 distinct |
| **Authentication credentials** | 3 (.env: Gmail app password, Telegram bot token + chat ID) |

### What Is Included

| Component | Integration | LOC | Auth | Why Included |
|-----------|------------|-----|------|-------------|
| Market data | `finance-datareader` | 90 | None | Covers Korean + global + FX + commodities in one library. No API key. |
| AI model | Claude Code (native) | 0 | Subscription | Does everything. Multi-model adds complexity without proportional benefit in M1. |
| Notification | Telegram Bot | 85 | Bot token (perm) | 5 min setup, zero maintenance, mobile push + file attachment. |
| Archival | Gmail SMTP | 55 | App password (perm) | Permanent email record of every report. |
| File output | Markdown to `output/{date}/` | 10 | None | Always available, zero dependency. |
| Scheduling | launchd plist | 40 (XML) | None | macOS native, handles sleep/wake, set-and-forget. |
| Journal | SQLite (WAL mode) | 40 | None | Decision tracking from Day 1 enables future accuracy analysis. |
| Logging | RotatingFileHandler | 30 | None | Structured logs for debugging pipeline failures. |
| Backup | Pre-run file copy script | 20 | None | Safety net before each run. |
| JSONL export | Signal archive | 15 | None | Append-only archive for future DuckDB analytics. |

### What Is Scaffolded (Code Exists But Not Active)

```python
# config/investscan.yaml
multi_model:
  enabled: false  # Flip to true in M3+
  gemini:
    model: "gemini-2.5-pro"
    timeout: 120
  codex:
    model: "gpt-5.4"
    timeout: 60
```

The `GeminiCLI` and `CodexCLI` wrapper classes from Branch 2 research (~110 LOC) are included in the codebase but behind a feature flag. When the user is ready (Month 3+), enabling multi-model is a config change, not a code change.

### What Is Excluded (and Why)

| Excluded | Why | When to Add |
|----------|-----|-------------|
| pykrx (sector indices) | Web-scraper fragility; FinanceDataReader covers KOSPI composite | M2 (when sector-level direction matters) |
| fredapi (FRED macro) | Adds API key management; macro context is nice but not essential | M2 |
| Gemini CLI (active) | 28s latency per call; unnecessary for standard weekly analysis | M3+ (for 10-K filings) |
| Codex CLI (active) | Adds complexity; Claude handles JSON output adequately | M3+ (for web search) |
| Streamlit dashboard | 300 LOC + ongoing dependency management for visualization | M3+ |
| WeasyPrint PDF | Complex C dependencies; Markdown is sufficient for solo user | M4+ (if sharing reports) |
| KakaoTalk | 200-char limit + 30-day token expiry. Telegram is strictly superior. | NEVER |
| pytrends | Google actively blocks. Unreliable. | NEVER |

### Balanced Scenario Verdict

**This is the sweet spot.** 420 LOC for external integrations leaves 2,290 LOC (85%) for the core pipeline -- normalization, synthesis, report generation, and the investment logic that actually matters. Six failure modes are manageable for a solo developer. Monthly maintenance is negligible. And the multi-model capability is one config toggle away when the time comes.

---

## 3.C: Minimal Integration Scenario

**Profile**: FinanceDataReader only + Claude only + Markdown file output only + cron one-liner

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   MINIMAL INTEGRATION SCENARIO                   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ EnvironmentScan│ │ GlobalNews   │  │FinanceData-  │          │
│  │ (local files) │ │ (local files)│  │Reader         │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│  ┌──────▼──────────────────▼──────────────────▼─────────────┐   │
│  │              investscan/ Python Package                    │   │
│  │  normalize → synthesize → report                          │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│                    ┌────▼────┐                                   │
│                    │ Claude  │                                   │
│                    │ (native)│                                   │
│                    └────┬────┘                                   │
│                         │                                        │
│                    ┌────▼────┐                                   │
│                    │ .md file│                                   │
│                    │ on disk │                                   │
│                    └─────────┘                                   │
│                                                                  │
│  Scheduling: cron (one line)                                    │
│  Storage: JSON files only (no SQLite)                           │
└──────────────────────────────────────────────────────────────────┘
```

### Metrics

| Metric | Value |
|--------|-------|
| **External integration LOC** | ~101 |
| **Remaining LOC for core pipeline** | ~2,609 (of 2,710) |
| **Setup time** | ~30 minutes |
| **Monthly maintenance** | ~0 hours |
| **Weekly pipeline runtime** | ~1-2 minutes |
| **External dependencies** | 1 pip package |
| **Failure modes** | 2 (FinanceDataReader backend + Claude session) |
| **Authentication credentials** | 0 |

### Minimal Scenario Verdict

**Viable but leaves value on the table.** The marginal cost of adding Telegram (5 min setup, 85 LOC, zero maintenance) and Gmail (5 min setup, 55 LOC, zero maintenance) is so low that skipping them is false economy. Similarly, launchd (15 min setup) eliminates the need to remember to run the pipeline manually -- critical for a busy pastor.

The minimal scenario is a good **"build this first in the first 2 hours"** target, then immediately layer on Telegram + Email + launchd to arrive at the Balanced scenario.

---

## Scenario Comparison Matrix

| Criterion | 3.A Full | 3.B Balanced | 3.C Minimal |
|-----------|----------|-------------|-------------|
| **External LOC** | ~935 | ~420 | ~101 |
| **Core pipeline LOC remaining** | 1,775 (65%) | 2,290 (85%) | 2,609 (96%) |
| **Setup time** | ~10 hrs | ~2.5 hrs | ~30 min |
| **Monthly maintenance** | ~2.5 hrs | ~15 min | ~0 |
| **Failure modes** | 14 | 6 | 2 |
| **Credentials to manage** | 4 | 3 | 0 |
| **Mobile notification** | Yes (Telegram) | Yes (Telegram) | No |
| **Email archive** | Yes | Yes | No |
| **Multi-model AI** | Yes (3 models) | Scaffolded (1 active) | No |
| **Dashboard** | Yes (Streamlit) | No (M3+) | No |
| **Korean sector indices** | Yes (pykrx) | No (M2) | No |
| **Automated scheduling** | launchd | launchd | cron |
| **Decision journal** | SQLite | SQLite | None |
| **Compatible with 2-4 hrs/week?** | BORDERLINE | YES | YES |
| **Upgrade path** | Already maxed | Clear path to Full | Clear path to Balanced |

---

# PHASE 4: Final Integration Guide

## 1. Recommended Scenario: 3.B (Balanced Integration)

### Justification

The Balanced scenario is recommended for five concrete reasons:

1. **LOC efficiency**: 420 LOC for external integrations leaves 85% of the 2,710 budget for the core pipeline. The core pipeline -- normalization, STEEPs-to-GICS mapping, direction scoring, report generation -- is where InvestScan's value proposition lives. Starving it of LOC for the sake of more output channels is backwards.

2. **Maintenance reality**: At 2-4 hrs/week total availability, the ~15 min/month maintenance of the Balanced scenario is negligible. The Full scenario's ~2.5 hrs/month would consume 25-50% of one week's entire budget just to keep integrations working.

3. **Debugging tractability**: Six failure modes can be diagnosed by a solo developer reading logs. Fourteen failure modes create combinatorial debugging nightmares ("is the report wrong because pykrx returned stale data, or because Gemini's OAuth expired, or because pytrends hit a rate limit?").

4. **Zero-cost upgrade path**: Every Yellow-zone integration (pykrx, fredapi, Gemini, Codex, Streamlit) can be added incrementally in Months 2-4 without architectural changes. The scaffolding is already in the codebase.

5. **Output channel sufficiency**: Telegram push (mobile, instant, 4096 chars) + Gmail (archival, searchable) + Markdown file (local, always available) covers every realistic consumption pattern for a solo user.

---

## 2. Complete External Dependency List

### Active Dependencies (Month 1)

| # | Library | Version | Purpose | Auth Method | Install | Failure Mode | Degradation |
|---|---------|---------|---------|-------------|---------|-------------|-------------|
| 1 | `finance-datareader` | >=0.9.85 | Korean+global market data, FX, commodities, Treasury yields | None (no API key) | `pip install finance-datareader` | Backend (KRX/Naver/Yahoo) temporarily down | Use cached last-known values; report marks data as stale |
| 2 | `requests` | >=2.31 | HTTP calls for Telegram API | None | `pip install requests` (usually pre-installed) | Network timeout | Retry 3x with exponential backoff; file output still succeeds |
| 3 | `python-dotenv` | >=1.0 | Load .env credentials | None | `pip install python-dotenv` | .env file missing | Telegram/Email silently skip; report still generated |
| 4 | `pyyaml` | >=6.0 | Config file loading | None | `pip install pyyaml` | Config file malformed | Fail-fast with clear error |
| 5 | `jinja2` | >=3.1 | Report template rendering | None | `pip install Jinja2` | Template syntax error | Fail-fast; raw data dump as fallback |
| 6 | `rich` | >=13.0 | CLI progress display | None | `pip install rich` | Terminal incompatibility | Falls back to plain print() |

**Note**: `pandas`, `numpy`, `pyarrow` are also required but they are core pipeline dependencies, not external integration dependencies. They would exist regardless of external integrations.

### Scaffolded Dependencies (Inactive, for Future Activation)

| # | Library | Version | Purpose | Auth Method | Activation Trigger |
|---|---------|---------|---------|-------------|-------------------|
| 7 | `pykrx` | >=1.0 | KRX sector indices | None | M2: `config.data_sources.pykrx.enabled: true` |
| 8 | `fredapi` | >=0.5 | FRED macro indicators | Free API key (.env) | M2: `config.data_sources.fred.enabled: true` |
| 9 | Gemini CLI | >=0.35 | Long-context AI analysis | Google OAuth (existing) | M3: `config.multi_model.enabled: true` |
| 10 | Codex CLI | >=0.116 | Structured classification + web search | ChatGPT subscription (existing) | M3: `config.multi_model.enabled: true` |
| 11 | `streamlit` | >=1.35 | Dashboard UI | None | M3+: separate `dashboard.py` |
| 12 | `plotly` | >=5.18 | Interactive charts for dashboard | None | M3+: with Streamlit |
| 13 | `weasyprint` | >=62 | PDF export | None | M4+: `config.output.pdf.enabled: true` |

### Never-Install List

| Library | Reason |
|---------|--------|
| `PyKakao` | 200-char limit, 30-day OAuth token expiry, Telegram is strictly superior |
| `pytrends` | Google actively blocks automated access, unreliable for production |

---

## 3. Integration LOC Budget

### Budget Allocation (of 2,710 Total LOC)

| Category | LOC | % of Total | Details |
|----------|-----|-----------|---------|
| **Core Pipeline** | **~1,700** | **63%** | normalize_signals.py (~400), synthesize_investment.py (~350), generate_report.py (~250), schema.py (~100), config.py (~80), decision_journal.py (~120), __main__.py (Click CLI, ~100), sector_mapping.py (~150), deduplication.py (~150) |
| **External Data Fetch** | **~130** | **5%** | korean_market.py (FinanceDataReader wrappers, ~90), data_cache.py (stale-data fallback, ~40) |
| **AI Integration** | **~160** | **6%** | multi_model.py (GeminiCLI + CodexCLI wrappers, ~110 scaffolded/inactive), synthesis_prompts.py (Claude prompt templates, ~50) |
| **Output/Notification** | **~160** | **6%** | notify_telegram.py (~85), notify_email.py (~55), output_manager.py (dispatch, ~20) |
| **Toolchain/Infra** | **~160** | **6%** | launchd plist (~40 XML), run.sh (~30), logging_config.py (~30), backup.py (~20), jsonl_export.py (~15), decision_journal SQLite (~25) |
| **Templates** | **~150** | **5%** | weekly-report.md.j2 (~100), sector-heatmap partial (~50) |
| **Tests** | **~250** | **9%** | test_normalize.py (~100), test_sector_mapping.py (~80), test_synthesis.py (~70) |

### External Integration Subtotal

**Active M1 external integration LOC**: 130 (data) + 50 (AI prompts) + 160 (output) + 160 (toolchain) = **~500 LOC (18%)**

**Scaffolded inactive LOC**: ~110 (multi-model wrappers) + ~135 (pykrx/fredapi/dashboard stubs) = **~245 LOC (9%)**

**Core pipeline LOC**: ~1,700 + 250 (tests) = **~1,950 LOC (72%)**

This allocation ensures the core analytical pipeline -- the part that actually generates investment insights -- receives the overwhelming majority of LOC and development attention.

---

## 4. Setup Order

### Step-by-Step Configuration (Estimated: 2.5 hours total)

**Step 1: Python Environment (15 minutes)**
```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test
python3 -m venv .venv
source .venv/bin/activate
pip install finance-datareader requests python-dotenv pyyaml jinja2 rich
pip install pandas pyarrow numpy  # Core pipeline deps
```

**Step 2: Credentials File (10 minutes)**
```bash
# Create .env (gitignored)
cat > .env << 'EOF'
# Telegram Bot (via @BotFather -- token never expires)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Gmail (via Google Account > App Passwords -- never expires)
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password

# Future: FRED API (free, register at https://fred.stlouisfed.org/docs/api/api_key.html)
# FRED_API_KEY=your_key_here
EOF
```

**Step 3: Telegram Bot Setup (5 minutes)**
1. Open Telegram, message `@BotFather`, send `/newbot`
2. Name it "InvestScan Bot", username `investscan_yourname_bot`
3. Copy the bot token to `.env`
4. Message `@userinfobot` to get your chat ID
5. Send any message to your new bot (activates the chat)

**Step 4: Gmail App Password (5 minutes)**
1. Go to Google Account > Security > 2-Step Verification
2. At the bottom, "App passwords" > Select "Other" > Name "InvestScan"
3. Copy the 16-character password to `.env`

**Step 5: Verify Data Source (5 minutes)**
```python
# Quick test
import FinanceDataReader as fdr
print(fdr.DataReader("KS11", "2026-03-01").tail())  # KOSPI last few days
print(fdr.DataReader("USD/KRW", "2026-03-01").tail())  # USD/KRW
```

**Step 6: launchd Plist (15 minutes)**
```bash
# Create plist
cat > ~/Library/LaunchAgents/com.investscan.weekly.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.investscan.weekly</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/.venv/bin/python</string>
        <string>-m</string>
        <string>investscan</string>
        <string>run</string>
        <string>--scheduled</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
        <key>LANG</key>
        <string>en_US.UTF-8</string>
    </dict>
    <key>Nice</key>
    <integer>10</integer>
    <key>KeepAlive</key>
    <false/>
    <key>TimeOut</key>
    <integer>14400</integer>
</dict>
</plist>
PLIST

# Load and verify
launchctl load ~/Library/LaunchAgents/com.investscan.weekly.plist
launchctl list | grep investscan
```

**Step 7: Directory Structure (5 minutes)**
```bash
mkdir -p output logs config templates tests
mkdir -p investscan/data
touch investscan/__init__.py investscan/__main__.py
```

**Step 8: End-to-End Smoke Test (15 minutes)**
Run the pipeline manually once to verify all integrations work:
```bash
source .venv/bin/activate
python -m investscan run --date 2026-03-28 --dry-run
```

---

## 5. Degradation Matrix

This matrix defines exactly what happens when each external service is unavailable, and what the user sees.

| # | Service Down | Detection | Automatic Response | User Impact | Report Quality |
|---|-------------|-----------|-------------------|-------------|---------------|
| 1 | **FinanceDataReader backend** (KRX/Naver/Yahoo) | `requests.ConnectionError` or empty DataFrame | Use cached last-known values from `data/cache/market_data.json`; report header shows "Market data: cached (2026-03-21)" | Sees stale price data with clear staleness indicator | DEGRADED -- direction calls lack current pricing |
| 2 | **Claude Code session** | N/A (if Claude is down, nothing runs) | Pipeline cannot execute at all | No report generated; launchd logs the failure | NONE -- no report |
| 3 | **Telegram API** | HTTP 4xx/5xx or timeout | Retry 3x with 2s/4s/8s backoff; if all fail, log warning and continue | No mobile notification; report still saved to disk and emailed | UNAFFECTED -- report quality is the same |
| 4 | **Gmail SMTP** | `smtplib.SMTPException` | Retry 2x; if failed, log warning and continue | No email archive; report still saved to disk and sent via Telegram | UNAFFECTED |
| 5 | **Network (total outage)** | All HTTP requests fail | Use cached market data; skip Telegram/Email; generate report from local signals only | No notifications; market data is stale; report still generated from cached + local signals | DEGRADED -- but still useful from signal analysis alone |
| 6 | **launchd missed run** (Mac was off all Sunday) | launchd catches up on next wake automatically | Pipeline runs on Monday morning when Mac wakes | Delayed by hours; report is still valid (uses latest available data) | UNAFFECTED (just delayed) |
| 7 | **SQLite corruption** | `sqlite3.DatabaseError` | Create new database file; log warning; old journal entries lost | Decision journal resets; current report unaffected | UNAFFECTED for current report |
| 8 | **EnvironmentScan data > 7 days old** | Check file modification time | Pipeline logs warning "Source data stale: 12 days old"; continues with stale data | Report header shows staleness warning | DEGRADED -- signals may be outdated |
| 9 | **GlobalNews data missing** | File not found | Pipeline runs with EnvironmentScan data only; report notes "GlobalNews: unavailable" | Reduced signal coverage (one source instead of two) | DEGRADED but functional |

### Degradation Principle

**The pipeline should ALWAYS produce a report**, even if degraded. A stale report with warnings is more useful than no report at all. The only scenario where no report is generated is when Claude Code itself is unavailable -- and in that case, nothing can run anyway.

---

## 6. Critical Insight: Multi-Model CLI Subscription Documentation

### The Discovery

Branch 2 research revealed a finding that should be prominently documented in the PRD:

**All three major AI CLIs (Claude Code, Gemini CLI, OpenAI Codex CLI) authenticate via existing subscription accounts using OAuth -- not API keys.** This means:

- **$0 additional cost** for multi-model integration
- **No API key management** (no rotation, no billing alerts, no quota dashboards)
- **Subscription-tier rate limits** are generous for weekly batch processing (1,500+ Gemini requests/day, unlimited Codex within ChatGPT plan)

### How This Should Appear in the PRD

```markdown
## Multi-Model AI Integration

InvestScan uses three AI models via their respective CLI tools.
ALL models authenticate through existing subscription accounts.
No API keys are required. No additional cost is incurred.

| Model | CLI Tool | Auth Method | Cost |
|-------|---------|-------------|------|
| Claude (Opus/Sonnet) | Claude Code (native) | Anthropic subscription | $0 additional |
| Gemini 2.5 Pro | `gemini` CLI (npm) | Google OAuth (personal) | $0 additional |
| GPT-5.4 | `codex` CLI (npm) | ChatGPT subscription | $0 additional |

### Integration Method

Python `subprocess.run()` calls to CLI tools. Each CLI outputs
structured JSON. Claude Code acts as orchestrator.

### Key Technical Detail

Gemini CLI's subscription auth ONLY works via subprocess. All existing
Gemini MCP servers require API keys. This is why subprocess.run() is
the chosen integration method, not MCP.

### Activation

Multi-model is disabled by default. Enable via:
`config/investscan.yaml` > `multi_model.enabled: true`

This is a runtime configuration change, not a code deployment.
```

### Why This Matters for PRD

Most investment tool PRDs assume API key management as a given -- billing limits, key rotation, cost monitoring. InvestScan's subscription-CLI approach eliminates this entire category of complexity. This should be called out explicitly because:

1. **Reviewers will assume API costs** unless told otherwise
2. **The subprocess integration pattern** is unconventional and needs justification
3. **The Gemini MCP limitation** (no subscription auth for MCP) explains a design choice that might otherwise seem arbitrary
4. **Future developers** need to know that switching to API keys would be a regression, not an improvement

---

## 7. Month-by-Month Integration Plan

### Month 1 (Weeks 1-4): Foundation

**Goal**: Working pipeline that produces useful reports with zero ongoing maintenance.

| Week | Task | LOC Added | Integrations |
|------|------|-----------|-------------|
| W1 | Project scaffolding: venv, pyproject.toml, investscan/ package, Click CLI, YAML config | ~200 | pyyaml, click |
| W2 | FinanceDataReader integration + data cache layer + normalization module | ~250 | finance-datareader |
| W3 | Synthesis module + Jinja2 report template + Claude prompt design | ~350 | jinja2 |
| W4 | Telegram + Email notification + launchd setup + SQLite journal + first real run | ~300 | requests, python-dotenv, smtplib, launchd, sqlite3 |

**M1 exit criteria**:
- `python -m investscan run` produces a Korean weekly report from real data
- Telegram push notification arrives on phone
- Email copy arrives in inbox
- launchd fires on Sunday at 8 PM
- Decision journal records the run

**M1 LOC total**: ~1,100
**M1 external integration LOC**: ~420

---

### Month 2 (Weeks 5-8): Data Enrichment

**Goal**: Richer market context with Korean sector indices and macro indicators.

| Week | Task | LOC Added | Integrations |
|------|------|-----------|-------------|
| W5 | pykrx integration: 22 KRX sector indices + sector-level direction calls | ~120 | pykrx |
| W6 | fredapi integration: Fed rate, CPI, GDP, unemployment + macro framing section in report | ~100 | fredapi |
| W7 | Enhanced synthesis: cross-source signal convergence scoring + STEEPs-to-GICS mapping refinement | ~200 | -- |
| W8 | Test suite expansion + first accuracy retrospective (compare M1 direction calls to actual market movements) | ~150 | pytest |

**M2 exit criteria**:
- Report includes Korean sector-level direction (not just KOSPI composite)
- Report includes macro environment framing (rate cycle, inflation trend)
- At least 10 contract tests pass for normalization + sector mapping
- First retrospective entry in decision journal

**M2 LOC total**: ~1,670 cumulative
**M2 new external integration LOC**: ~220 (pykrx + fredapi)

---

### Month 3 (Weeks 9-12): Multi-Model Activation

**Goal**: Enable Gemini + Codex for cross-validation and web search.

| Week | Task | LOC Added | Integrations |
|------|------|-----------|-------------|
| W9 | Activate GeminiCLI wrapper: test with real prompts, tune timeouts, handle OAuth edge cases | ~60 | Gemini CLI |
| W10 | Activate CodexCLI wrapper: test structured output, verify web search capability | ~60 | Codex CLI |
| W11 | Multi-model orchestrator: parallel execution, output combination, confidence scoring from model agreement | ~120 | concurrent.futures |
| W12 | Report enhancement: multi-model synthesis section showing where models agree/disagree | ~80 | -- |

**M3 exit criteria**:
- `config.multi_model.enabled: true` activates Gemini + Codex in the pipeline
- Report shows "Model Agreement" section with cross-validation results
- Fallback works correctly: if Gemini times out, Claude-only synthesis proceeds
- Pipeline completes in <8 minutes with all three models

**M3 LOC total**: ~1,990 cumulative
**M3 new external integration LOC**: ~320 (multi-model active)

---

### Month 4-6 (Weeks 13-24): Polish and Visualization

**Goal**: Dashboard, PDF export, and accumulated intelligence features.

| Month | Task | LOC Added | Integrations |
|-------|------|-----------|-------------|
| M4 | Streamlit dashboard: report viewer + sector heatmap + signal explorer (reuse GlobalNews pattern) | ~300 | streamlit, plotly |
| M5 | WeasyPrint PDF export + DuckDB historical analytics on JSONL archive | ~180 | weasyprint, duckdb |
| M6 | Accuracy tracking: automated retrospective comparison, rolling prediction accuracy score, report confidence calibration | ~220 | -- |

**M6 exit criteria**:
- `streamlit run dashboard.py` shows interactive report with sector heatmap
- PDF export generates publication-quality Korean report
- DuckDB queries across 6 months of accumulated JSONL signals
- Rolling prediction accuracy score displayed in dashboard
- System approaches the Full Integration scenario (3.A) organically

**M6 LOC total**: ~2,690 cumulative (within 2,710 budget)
**M6 external integration LOC**: ~935 total

---

### Integration Timeline Visual

```
Month:  M1          M2          M3          M4          M5          M6
        ├───────────┼───────────┼───────────┼───────────┼───────────┤

GREEN ZONE (M1):
[===== FinanceDataReader ==========================================]
[===== Telegram Bot ===============================================]
[===== Gmail SMTP =================================================]
[===== launchd ====================================================]
[===== SQLite Journal =============================================]
[===== Claude (native) ============================================]

YELLOW ZONE (M2-M4):
              [==== pykrx ========================================]
              [==== fredapi ======================================]
                          [==== Gemini CLI =======================]
                          [==== Codex CLI ========================]
                                    [==== Streamlit ==============]
                                              [==== WeasyPrint ===]

RED ZONE:
  KakaoTalk ── NEVER
  pytrends ── NEVER
```

---

## Summary of Key Decisions

1. **Recommended scenario**: 3.B (Balanced Integration) -- 420 LOC for external integrations in M1, scaling to ~935 by M6
2. **Primary data library**: FinanceDataReader (one library, no API key, covers Korean + global + FX + commodities)
3. **Primary AI model**: Claude Code (native, no subprocess overhead, best reasoning + Korean)
4. **Primary notification**: Telegram Bot (permanent token, 4096 chars, file attachment, 5 min setup)
5. **Scheduling**: launchd (macOS native, handles sleep/wake, set-and-forget)
6. **Multi-model approach**: Scaffolded in M1, activated in M3 via config toggle
7. **Explicitly excluded**: KakaoTalk (negative ROI), pytrends (unreliable)
8. **LOC budget**: 72% core pipeline, 18% active external integrations, 9% scaffolded future integrations
9. **Degradation principle**: Always produce a report, even if degraded, with clear staleness indicators
10. **The critical CLI insight**: All 3 AI models use subscription auth ($0 additional), documented prominently in PRD
