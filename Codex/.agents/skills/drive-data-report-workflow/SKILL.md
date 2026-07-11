---
name: drive-data-report-workflow
description: Use when organizing Google Drive, Google Sheets, Excel, CSV, course application, survey, or feedback files into a cleaned dataset, analysis report, PDF, visualization, or repeatable Codex-only data workflow.
---

# Drive Data Report Workflow

## Overview

Use this skill to turn scattered Drive spreadsheet files into a repeatable Codex workflow: source inventory, classification, normalization, analysis, report writing, and visual output. Treat connected Google Drive as source of truth; do not invent rows, metrics, names, dates, or file contents from memory.

## Quick Start

1. Confirm the source scope: Drive account, folder/query, file type, and output type.
2. Use Google Drive/Sheets connectors when available. If not available, ask for exported files or local paths.
3. Read `references/workflow.md` for the end-to-end runbook.
4. Read `references/output-contract.md` before creating Sheets, PDFs, dashboards, or final handoff notes.
5. If the analysis produces a feedback stats JSON, use `scripts/render_feedback_dashboard.py` to create a PNG/PDF dashboard.

## Operating Rules

- Keep all source files traceable. Maintain a source manifest with file name, Drive URL or local path, modified date when available, and role in the analysis.
- Separate private detail from reportable output. Names, emails, phone numbers, and free-text respondent details stay out of public visuals unless the user explicitly requests otherwise.
- Normalize before interpreting. Standardize dates, course/session labels, respondent keys, rating scales, blank values, and duplicate records before drawing conclusions.
- Compare like with like. When comparing sessions, use the same metric definitions across all sessions.
- Verify every artifact after creation: sheet tabs/ranges, PDF page count, image dimensions, and file paths.

## Workflow Modes

| Mode | Trigger words | Main outputs |
| --- | --- | --- |
| File inventory | `Drive files`, `Excel 정리`, `자료 종류별 분류` | source manifest, file categories, next-action table |
| Course applications | `강의신청`, `신청자`, `수강생`, `등록` | applicant master, course/session comparison, duplicates, follow-up list |
| Feedback analysis | `후기`, `설문`, `만족도`, `평가`, `회차 비교` | response summary, session comparison, themes, PDF report, dashboard |
| General report pack | `보고서`, `PDF`, `시각화`, `대시보드` | cleaned Sheet, PDF report, PNG/PDF visualization, final path report |

## Bundled Resources

- `references/workflow.md`: execution runbook for Drive search, spreadsheet reading, normalization, analysis, and handoff.
- `references/output-contract.md`: expected sheet tabs, report sections, dashboard blocks, and stats JSON shape.
- `scripts/render_feedback_dashboard.py`: renders a feedback dashboard PNG/PDF from a stats JSON.

## Common Mistakes

- Do not summarize Drive file names as if file contents were read. Metadata inventory and data analysis are different steps.
- Do not merge repeated respondents until the respondent key strategy is explicit.
- Do not put personal identifiers into slide-style dashboards by default.
- Do not call the workflow complete until output files are opened or inspected in their final format.
