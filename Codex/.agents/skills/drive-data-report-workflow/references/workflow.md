# Drive Data Report Workflow Runbook

## 1. Scope And Source

Collect only the minimum scope needed:

- Drive account or shared drive.
- Folder URL, search query, or exact file list.
- Target workflow: inventory, applications, feedback, report pack, or custom.
- Output destination: local `output/`, Google Sheet, PDF, image, or all of them.

If connector authentication is uncertain, first verify access with a small file search or metadata read. If the connector is unavailable, ask for local exports and continue from local files.

## 2. Source Manifest

Create a manifest before analysis. Include:

- `source_id`
- `file_name`
- `mime_type` or extension
- Drive URL or local path
- modified date when available
- inferred role: `application`, `feedback`, `reference`, `unknown`
- read status: `not_read`, `read`, `blocked`

Keep blocked files in the manifest with the reason. Do not silently drop them.

## 3. Spreadsheet Reading

For Google Sheets:

- Read tab names first.
- Inspect headers and 5-10 rows before deciding schema.
- Read only needed ranges when the sheet is large.

For Excel files:

- Copy or export to a temporary work directory before parsing.
- Prefer structured workbook parsers. If a workbook parser fails, inspect the OOXML or convert through a safer route rather than guessing.
- Preserve source file names in every normalized row.

## 4. Classification

Use file names, tab names, headers, and row samples together.

Typical application signals:

- `신청`, `등록`, `수강`, `참가`, `이름`, `이메일`, `전화`, `강좌`, `희망`

Typical feedback signals:

- `후기`, `설문`, `만족도`, `도움`, `좋았던`, `아쉬운`, `다음`, `의견`

When classification is uncertain, label `unknown` and report the ambiguity.

## 5. Normalization

Normalize into analysis-ready tables before writing conclusions.

Application rows:

- respondent key: email first, then phone/name fallback if needed
- course/session label
- application timestamp
- attendance or status fields if present
- notes and follow-up fields

Feedback rows:

- respondent key when available
- session/day label
- rating fields converted to numeric scale
- free-text fields split by question
- source file and row number

Do not overwrite the raw source values. Keep raw columns or a raw export when practical.

## 6. Analysis Patterns

Application analysis:

- unique applicants
- duplicate applicants
- course/session demand
- same applicant across multiple courses
- missing contact info
- priority follow-up list

Feedback analysis:

- total responses and unique respondents
- average satisfaction, usefulness, and combined score
- session-by-session comparison
- top positive themes
- top requested follow-up topics
- operational recommendations

Use consistent denominator language: responses, unique respondents, files, sessions.

## 7. Artifact Creation

Create durable outputs in this order:

1. Cleaned working dataset or Google Sheet.
2. Analysis report in Markdown or document source.
3. PDF report.
4. PNG/PDF visualization.
5. Final handoff with clickable paths and verification evidence.

For current workspace outputs, prefer:

- `output/sheets/` for exported tables
- `output/pdf/` for PDF reports
- `output/visualizations/` for dashboard images and PDF visuals
- `tmp/` for temporary renders only

## 8. Verification

Before handoff, verify:

- Source manifest includes every intended file.
- Cleaned table row counts reconcile with source row counts or documented exclusions.
- Google Sheet tabs/ranges open or can be read back.
- PDF has expected page count and renders.
- PNG/PDF visualization exists, has nonzero size, and text does not overlap.
- Final response includes what changed, where, what was verified, and what remains uncertain.
