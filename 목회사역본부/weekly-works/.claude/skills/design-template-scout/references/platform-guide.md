# Platform Guide — Design Template Scout

How to search each design platform effectively using Claude Code tools.

---

## Available Tools

| Tool | Use Case | Limitations |
|------|----------|-------------|
| `search_web` | Keyword search across all platforms | Text results only, no images |
| `read_url_content` | Extract detailed page content | No JavaScript rendering |
| `browser_subagent` | Full browser automation, screenshots | Slower, may hit login walls |

---

## Platform-Specific Strategies

### 1. Pinterest

**Best for:** Visual mood boards, color palettes, layout ideas

**Search approach:**
```
search_web("pinterest {topic} {type} design {mood}")
search_web("site:pinterest.com {topic} card design")
```

**What to extract:**
- Pin descriptions (color keywords, style names)
- Board names (indicate design categories)
- Related search suggestions (expand keyword universe)

**Tips:**
- Pinterest search results often include "People also searched for" → use these for follow-up queries
- Focus on pins from design agencies and professional accounts
- Look for "collection" or "board" results for curated sets

---

### 2. Behance

**Best for:** Professional portfolio-quality references, detailed process

**Search approach:**
```
search_web("behance {topic} social media design")
search_web("site:behance.net {topic} branding card")
```

**What to extract:**
- Project descriptions (design rationale, tool stack)
- Color palettes (often explicitly listed)
- Typography choices
- Layout variations shown in project galleries

**Tips:**
- Behance projects often include multiple variations → great for options
- "Appreciated" count indicates community-validated quality
- Look for Korean designers: "behance 카드뉴스 디자인 한국"

---

### 3. Canva

**Best for:** Ready-to-use template structures, trending designs

**Search approach:**
```
search_web("canva {topic} instagram template {mood}")
search_web("canva {주제} 카드뉴스 템플릿")
```

**What to extract:**
- Template categories and naming patterns
- Color theme names (Canva uses descriptive names)
- Layout structure descriptions
- Popular/trending indicators

**Tips:**
- Canva template pages often list design specs in text (colors, fonts)
- Free templates are accessible; Pro templates indicate premium trends
- Search by color: "canva template beige minimalist"

---

### 4. 미리캔버스 (MiriCanvas)

**Best for:** Korean-specific designs, Korean typography handling

**Search approach:**
```
search_web("미리캔버스 {주제} 카드뉴스 템플릿")
search_web("site:miricanvas.com {주제} 디자인")
```

**What to extract:**
- Korean font recommendations
- Korean text layout patterns
- Popular Korean design trends
- Template structure for Korean content

**Tips:**
- Best source for Korean card news specific designs
- Categories are well-organized: SNS포스트, 카드뉴스, 프레젠테이션
- Look at "인기 템플릿" for current trends

---

### 5. Dribbble

**Best for:** Cutting-edge UI/UX design, innovative layouts

**Search approach:**
```
search_web("dribbble {topic} card design {mood}")
search_web("site:dribbble.com social media template {topic}")
```

**What to extract:**
- Color hex codes (often shared in shot descriptions)
- Animation/interaction ideas
- Experimental layout concepts
- Design system approaches

**Tips:**
- Dribbble designs tend to be more experimental
- Good for finding unexpected creative directions
- Filter by "Popular" for community-curated quality

---

### 6. Google Images (General)

**Best for:** Broad discovery, finding less-known design sources

**Search approach:**
```
search_web("{topic} {type} design template {mood} site:*.com")
search_web("{주제} 카드뉴스 디자인 예시 {감성}")
```

**What to extract:**
- Source diversity (blogs, portfolios, template sites)
- Design trend articles
- "Best of" compilation posts

---

### 7. Slidesgo / SlidesAI (PPT specific)

**Best for:** Presentation-specific templates

**Search approach:**
```
search_web("slidesgo {topic} presentation template {mood}")
search_web("slides {주제} 프레젠테이션 템플릿")
```

**What to extract:**
- Slide structure (number of slides, layout types)
- Color scheme names
- Typography pairings
- Slide transition/animation suggestions

---

## Instagram Search Workaround

> Instagram content is not directly searchable without authentication.
> Use these workaround strategies:

### Strategy 1: Indirect Search
```
search_web("instagram {topic} card news design examples")
search_web("인스타그램 {주제} 카드뉴스 디자인 사례")
```

### Strategy 2: Blog/Article Roundups
```
search_web("best instagram church card news design 2026")
search_web("교회 인스타그램 카드뉴스 디자인 모음 2026")
```

### Strategy 3: Via Pinterest
Pinterest often mirrors Instagram design trends:
```
search_web("pinterest instagram church post template {mood}")
```

---

## Output Format After Search

After completing searches, compile results in this format:

```markdown
## 검색 결과 요약

### 수집된 레퍼런스 (총 N건)

#### Pinterest (N건)
1. [제목/설명](URL) — 핵심 특징: 컬러톤, 레이아웃 스타일
2. ...

#### Behance (N건)
1. [프로젝트명](URL) — 핵심 특징: 디자인 컨셉, 사용 폰트
2. ...

#### Canva/미리캔버스 (N건)
1. [템플릿명](URL) — 핵심 특징: 카테고리, 스타일 키워드
2. ...

### 발견된 디자인 패턴
- 지배적 컬러톤: [warm beige / cool navy / ...]
- 선호 레이아웃: [center-aligned / split / ...]
- 타이포 패턴: [serif heading + sans body / ...]
- 공통 요소: [ample whitespace / geometric shapes / ...]
```
