# Search Strategies — Design Template Scout

Systematic approach for finding design references across multiple platforms.

---

## Keyword Generation Rules

### Step 1: Extract Core Elements

From user input or sermon-context.md, extract:

| Element | Example | Variable |
|---------|---------|----------|
| Topic | "servant leadership" | `{topic}` / `{주제}` |
| Mood | warm, modern, bold | `{mood}` / `{감성}` |
| Content Type | card news, PPT, poster | `{type}` / `{유형}` |
| Platform | Instagram, KakaoTalk | `{platform}` |
| Season | Easter, Advent, Summer | `{season}` / `{시즌}` |
| Audience | youth, young adult, senior | `{audience}` |

### Step 2: Mood-to-Keyword Mapping

| Korean Mood | English Keywords | Color Direction |
|-------------|-----------------|-----------------|
| 따뜻함 | warm, cozy, soft, pastel | Beige, cream, peach, warm orange |
| 경건함 | sacred, reverent, elegant | Deep navy, gold, burgundy, ivory |
| 역동적 | dynamic, bold, vibrant, energetic | Bright red, electric blue, yellow |
| 모던 | modern, clean, minimalist, sleek | Monochrome, cool gray, white space |
| 친근함 | friendly, approachable, casual | Light blue, mint, soft pink |
| 고급스러움 | premium, luxury, sophisticated | Black, gold, deep green, serif fonts |
| 희망적 | hopeful, bright, uplifting | Sky blue, light yellow, green |
| 차분함 | calm, serene, peaceful | Sage green, lavender, muted tones |

### Step 3: Query Templates

#### Korean Queries (for 미리캔버스, Naver, Korean results)

```
KR_TEMPLATE_1: "{주제} 카드뉴스 디자인 템플릿"
KR_TEMPLATE_2: "{주제} {감성} 인스타그램 디자인"
KR_TEMPLATE_3: "{유형} 디자인 레퍼런스 {감성}"
KR_TEMPLATE_4: "{시즌} 교회 {유형} 디자인"
KR_TEMPLATE_5: "미리캔버스 {주제} 템플릿"
```

#### English Queries (for Pinterest, Behance, Canva)

```
EN_TEMPLATE_1: "pinterest {topic} {type} design {mood}"
EN_TEMPLATE_2: "behance {topic} social media design template"
EN_TEMPLATE_3: "canva {topic} {platform} template {mood}"
EN_TEMPLATE_4: "dribbble {topic} card design {mood} aesthetic"
EN_TEMPLATE_5: "{topic} {type} design inspiration {season}"
EN_TEMPLATE_6: "church {topic} social media graphic design"
```

#### Specialized Queries (for specific content types)

```
# Card News
CARD_1: "{topic} instagram carousel design"
CARD_2: "{주제} 카드뉴스 슬라이드 디자인"
CARD_3: "instagram slide post template {mood}"

# PPT / Presentation
PPT_1: "{topic} presentation template {mood} aesthetic"
PPT_2: "{주제} 프레젠테이션 디자인 {감성}"
PPT_3: "keynote {topic} slide deck design"
PPT_4: "slidesgo {topic} template"

# YouTube Thumbnail
YT_1: "{topic} youtube thumbnail design {mood}"
YT_2: "{주제} 유튜브 썸네일 디자인"

# General Social Media
SNS_1: "{topic} social media post design {mood}"
SNS_2: "{주제} SNS 포스트 디자인 {감성}"
```

---

## Search Execution Strategy

### Round 1: Broad Discovery (3 queries minimum)

Execute at least 3 `search_web` calls with diverse query patterns:

1. **Pinterest/Visual** — Focus on visual inspiration
2. **Template Platform** — Focus on usable templates (Canva, 미리캔버스)
3. **Design Portfolio** — Focus on professional examples (Behance, Dribbble)

### Round 2: Deep Dive (1-2 queries, optional)

If Round 1 results are insufficient or too generic:

1. Refine keywords based on Round 1 findings
2. Try alternative mood keywords from the mapping table
3. Add specific style modifiers: "gradient", "geometric", "organic", "flat design"

### Round 3: Detail Extraction (read_url_content)

For the top 2-3 most promising URLs:

1. Use `read_url_content` to extract detailed design information
2. Look for: color codes, font names, layout descriptions
3. Note any design trends mentioned in the page content

---

## Result Filtering Criteria

### Relevance Score (mental evaluation)

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Topic Match | 40% | Does the design relate to the content topic? |
| Mood Match | 25% | Does the visual feel match the desired mood? |
| Platform Fit | 20% | Is the format appropriate (square, 16:9, etc.)? |
| Quality | 15% | Is it a professional, polished design? |

### Minimum Requirements

- At least **5 relevant references** collected across all sources
- At least **2 different sources** represented (not all from one platform)
- At least **1 Korean source** and **1 English source**

---

## Fallback Strategy

If standard searches yield poor results:

1. **Broaden the topic**: "리더십" instead of "섬김의 리더십"
2. **Change the mood**: Try adjacent mood keywords
3. **Use generic queries**: "{type} design trends 2026"
4. **Try color-based search**: "navy gold card design template"
5. **Last resort**: Use `references/design-taxonomy.md` defaults
