# Design Taxonomy — Design Template Scout

Classification system for design elements. Used in Phase 3 to categorize
search results and generate structured design guides.

---

## Color Palettes by Mood

### Warm & Inviting
```css
--primary: #D4956A;    /* Warm terracotta */
--secondary: #F5E6D3;  /* Cream */
--accent: #8B4513;     /* Saddle brown */
--bg: #FFF8F0;         /* Warm white */
--text: #3D2B1F;       /* Dark brown */
```

### Modern & Clean
```css
--primary: #2D3748;    /* Cool charcoal */
--secondary: #4A5568;  /* Medium gray */
--accent: #3182CE;     /* Blue accent */
--bg: #F7FAFC;         /* Light gray */
--text: #1A202C;       /* Near black */
```

### Sacred & Reverent
```css
--primary: #1B2A4A;    /* Deep navy */
--secondary: #C9A96E;  /* Gold */
--accent: #722F37;     /* Wine red */
--bg: #F5F0E8;         /* Parchment */
--text: #1B2A4A;       /* Deep navy */
```

### Bold & Dynamic
```css
--primary: #E53E3E;    /* Vibrant red */
--secondary: #2B6CB0;  /* Strong blue */
--accent: #ECC94B;     /* Yellow */
--bg: #1A202C;         /* Dark bg */
--text: #FFFFFF;       /* White */
```

### Hopeful & Uplifting
```css
--primary: #38A169;    /* Fresh green */
--secondary: #63B3ED;  /* Sky blue */
--accent: #F6E05E;     /* Sunshine yellow */
--bg: #F0FFF4;         /* Mint white */
--text: #234E52;       /* Dark teal */
```

### Calm & Peaceful
```css
--primary: #718096;    /* Sage */
--secondary: #B794F4;  /* Lavender */
--accent: #9AE6B4;     /* Soft green */
--bg: #F7FAFC;         /* Cool white */
--text: #4A5568;       /* Gray */
```

### Premium & Luxury
```css
--primary: #1A1A2E;    /* Deep black-navy */
--secondary: #D4AF37;  /* Metallic gold */
--accent: #C9B99A;     /* Muted gold */
--bg: #0F0F1A;         /* Near black */
--text: #E2E8F0;       /* Off white */
```

### Friendly & Approachable
```css
--primary: #4299E1;    /* Friendly blue */
--secondary: #FC8181;  /* Soft coral */
--accent: #68D391;     /* Mint green */
--bg: #FFFFFF;         /* Clean white */
--text: #2D3748;       /* Dark gray */
```

---

## Typography Recommendations

### Korean-Optimized Font Stacks

| Style | Heading Font | Body Font | Google Fonts / CDN |
|-------|-------------|-----------|-------------------|
| Modern | Pretendard Bold | Pretendard Regular | [CDN](https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css) |
| Premium | Noto Serif KR | Noto Sans KR | Google Fonts |
| Friendly | Gothic A1 | Noto Sans KR Light | Google Fonts |
| Classic | Nanum Myeongjo | Nanum Gothic | Google Fonts |
| Dynamic | Black Han Sans | Noto Sans KR | Google Fonts |
| Minimal | Spoqa Han Sans Neo | Spoqa Han Sans Neo Light | [CDN](https://spoqa.github.io/spoqa-han-sans/css/SpoqaHanSansNeo.css) |

### Font Size Guidelines

| Element | Card News (1080×1080) | PPT (1920×1080) |
|---------|----------------------|-----------------|
| Main Title | 48-64px | 54-72px |
| Subtitle | 28-36px | 32-44px |
| Body Text | 20-26px | 22-30px |
| Caption/Note | 14-18px | 16-20px |
| Bible Verse | 22-28px (italic) | 26-34px (italic) |

---

## Layout Patterns

### Card News Layouts (1080×1080)

#### 1. Center-Aligned (중앙 정렬형)
- Text centered vertically and horizontally
- Large margins (20%+ on each side)
- Best for: quotes, single message, bible verses
- Mood: elegant, minimal, sacred

#### 2. Top-Heavy (상단 강조형)
- Title/headline in upper 40%
- Visual or whitespace in lower 60%
- Best for: impactful statements, cover slides
- Mood: bold, modern

#### 3. Split (분할형)
- Left/right or top/bottom split
- One side: text, other side: color/graphic
- Best for: question+answer, before+after
- Mood: dynamic, structured

#### 4. Full-Bleed Background (전면 배경형)
- Full-width background image or gradient
- Text overlay with semi-transparent backdrop
- Best for: atmospheric, emotional slides
- Mood: cinematic, warm

#### 5. Card/Box (카드형)
- Content in a floating card/box
- Background color or subtle pattern
- Best for: information-dense slides, tips
- Mood: clean, organized

#### 6. Stacked (적층형)
- Multiple horizontal blocks stacked
- Each block has different bg color or shade
- Best for: multi-point content, numbered lists
- Mood: structured, informative

### PPT Layouts (16:9)

#### 1. Title Slide
- Large centered title with subtitle
- Minimal elements, strong visual hierarchy

#### 2. Content + Visual
- 60/40 or 50/50 split
- Text on one side, image/graphic on other

#### 3. Full-Screen Image + Text Overlay
- Cinematic background
- Title and brief text overlay

#### 4. Data/List
- Bullet points or numbered items
- Icon accompaniments for visual interest

#### 5. Quote Slide
- Large quotation marks
- Centered text with author attribution

---

## Graphic Element Recommendations

### By Mood

| Mood | Recommended Elements |
|------|---------------------|
| Warm | Organic shapes, watercolor textures, hand-drawn icons |
| Modern | Geometric shapes, sharp lines, flat icons |
| Sacred | Cross motifs, light rays, dove, subtle patterns |
| Dynamic | Diagonal lines, bold shapes, arrows, gradients |
| Friendly | Rounded corners, soft shadows, emoji-style icons |
| Premium | Thin lines, gold accents, serif ornaments |

### Background Treatments

| Treatment | CSS/Implementation | Best For |
|-----------|-------------------|----------|
| Solid Color | `background: var(--bg)` | Minimal, clean |
| Linear Gradient | `background: linear-gradient(135deg, #color1, #color2)` | Modern, dynamic |
| Radial Gradient | `background: radial-gradient(circle, #color1, #color2)` | Warm, focused |
| Mesh Gradient | Multiple gradient layers | Premium, trendy |
| Subtle Pattern | `background-image: url(pattern.svg)` | Textured, classic |
| Photo + Overlay | `background-image` + `::after` overlay | Atmospheric |

---

## Season/Church Calendar Design Cues

| Season | Colors | Mood | Elements |
|--------|--------|------|----------|
| Advent | Purple, navy, gold | Anticipation, sacred | Candles, wreath, stars |
| Christmas | Red, green, gold | Joyful, festive | Star, manger, light |
| Lent | Purple, gray, muted | Reflective, solemn | Cross, thorns, ashes |
| Easter | White, gold, green | Triumphant, hopeful | Lily, sunrise, empty tomb |
| Pentecost | Red, orange, flame | Dynamic, powerful | Flames, dove, wind |
| Ordinary Time | Green variations | Growth, teaching | Seeds, paths, bread |
| Thanksgiving | Orange, gold, brown | Grateful, warm | Harvest, bounty |
