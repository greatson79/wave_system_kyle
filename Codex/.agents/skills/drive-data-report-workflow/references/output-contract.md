# Output Contract

## Sheet Tabs

Use only the tabs that match the requested workflow.

General:

- `요약`
- `원본목록`
- `정리_기준`

Applications:

- `신청자_마스터`
- `강좌별_신청현황`
- `중복_신청자`
- `후속조치`

Feedback:

- `응답자_마스터`
- `후기_이력`
- `회차별_비교`
- `좋았던점_분류`
- `요청_분류`
- `관심사_키워드`
- `관리_후속조치`

## PDF Report Sections

For feedback:

1. Executive summary
2. Source and method
3. Key metrics
4. Session comparison
5. Positive themes
6. Follow-up demand
7. Operational recommendations
8. Limits and verification

For applications:

1. Executive summary
2. Source and method
3. Applicant overview
4. Course demand comparison
5. Duplicate and missing-info checks
6. Follow-up actions
7. Limits and verification

## Dashboard Blocks

A one-page dashboard should include:

- Title and source note
- KPI strip
- Session or category comparison chart
- Top positive categories or demand categories
- Top requests or follow-up actions
- Short operating recommendations

Do not include personal identifiers in a dashboard unless explicitly requested.

## Feedback Stats JSON

`scripts/render_feedback_dashboard.py` expects this shape:

```json
{
  "responses": 61,
  "unique_respondents": 38,
  "avg_satisfaction": 4.75,
  "avg_usefulness": 4.77,
  "avg_score": 4.76,
  "day_comparison": [
    {"day": "첫째날", "responses": 12, "avg_score": 4.58}
  ],
  "top_good_categories": [
    {"category": "실습/결과물", "count": 26}
  ],
  "top_request_categories": [
    {"category": "영상/쇼츠 후속", "count": 15}
  ]
}
```

Optional fields may be present and should be preserved by the analysis, but the renderer only needs the fields above.
