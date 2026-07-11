# 수련회 도우미 앱 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 교회학교 교사가 수련회 준비에 바로 쓸 수 있는 바닐라 JS 웹앱을 제작한다 — 성경 캐릭터 성향 검사 탭 + 수련회 프로그램 생성(ChatGPT 프롬프트 복사) 탭으로 구성.

**Architecture:** API 없는 순수 클라이언트 앱. 성향 검사는 내장 로직으로 즉시 결과 출력, 프로그램 생성기는 입력값을 받아 최적화된 ChatGPT 프롬프트를 생성·복사. 두 탭은 성향 결과를 공유 state로 연결. 단일 저장소, GitHub Pages로 배포.

**Tech Stack:** HTML5, CSS3 (Custom Properties + CSS Grid), Vanilla JavaScript (ES6 모듈), GitHub Pages

---

## 파일 구조

```
camp-helper/
├── index.html              # 진입점, 탭 레이아웃
├── css/
│   └── style.css           # 전체 스타일 (Warm Paper 디자인)
├── js/
│   ├── app.js              # 탭 전환, 전역 state 관리
│   ├── quiz.js             # 성향 검사 UI + 점수 계산
│   └── program.js          # 프로그램 생성기 UI + 프롬프트 빌더
├── data/
│   ├── questions.js        # 성향 검사 질문 10개 + 선택지
│   ├── types.js            # 4가지 성경 캐릭터 유형 데이터
│   └── themes.js           # 5가지 수련회 주제 + 프롬프트 템플릿
└── README.md               # 배포 방법 + 사용법
```

---

## Task 1: 프로젝트 스캐폴드 + 기본 레이아웃

**Files:**
- Create: `camp-helper/index.html`
- Create: `camp-helper/css/style.css`

- [ ] **Step 1: 디렉터리 생성**

```bash
mkdir -p camp-helper/css camp-helper/js camp-helper/data
```

- [ ] **Step 2: `index.html` 작성**

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>수련회 도우미</title>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <header class="app-header">
    <h1 class="app-title">수련회 도우미</h1>
    <p class="app-subtitle">청소년 수련회를 AI로 준비하세요</p>
  </header>

  <nav class="tab-bar" role="tablist">
    <button class="tab-btn active" role="tab" aria-selected="true"
            aria-controls="panel-program" id="tab-program">
      🎮 프로그램 생성
    </button>
    <button class="tab-btn" role="tab" aria-selected="false"
            aria-controls="panel-quiz" id="tab-quiz">
      🧠 성향 검사
    </button>
  </nav>

  <main>
    <section id="panel-program" role="tabpanel" aria-labelledby="tab-program" class="tab-panel active">
      <!-- Task 4에서 채움 -->
    </section>
    <section id="panel-quiz" role="tabpanel" aria-labelledby="tab-quiz" class="tab-panel hidden">
      <!-- Task 2에서 채움 -->
    </section>
  </main>

  <script type="module" src="js/app.js"></script>
</body>
</html>
```

- [ ] **Step 3: `css/style.css` 작성 — Warm Paper 디자인 토큰 + 레이아웃**

```css
/* ===== DESIGN TOKENS ===== */
:root {
  --bg: #faf7f2;
  --bg-alt: #f3ede3;
  --text-primary: #1c1917;
  --text-secondary: #57534e;
  --text-light: #a8a29e;
  --accent: #d97706;
  --accent-warm: #ef4444;
  --accent-light: #fef3c7;
  --border: #e7ddd0;
  --card-bg: #ffffff;
  --shadow: 0 1px 4px rgba(0,0,0,0.08);

  --font-serif: 'Noto Serif KR', serif;
  --font-sans: 'Noto Sans KR', sans-serif;

  --radius: 10px;
  --radius-lg: 16px;
  --space-xs: 0.4rem;
  --space-sm: 0.75rem;
  --space-md: 1.25rem;
  --space-lg: 2rem;
}

/* ===== RESET + BASE ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font-sans);
  background: var(--bg);
  color: var(--text-primary);
  min-height: 100vh;
}

/* ===== HEADER ===== */
.app-header {
  background: var(--bg-alt);
  border-bottom: 1px solid var(--border);
  padding: var(--space-md) var(--space-lg);
  text-align: center;
}
.app-header::before {
  content: '';
  display: block;
  height: 4px;
  background: linear-gradient(90deg, var(--accent), var(--accent-warm));
  margin-bottom: var(--space-md);
}
.app-title {
  font-family: var(--font-serif);
  font-size: clamp(1.4rem, 4vw, 2rem);
  font-style: italic;
  color: var(--text-primary);
}
.app-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: var(--space-xs);
}

/* ===== TAB BAR ===== */
.tab-bar {
  display: flex;
  border-bottom: 2px solid var(--border);
  background: var(--bg-alt);
}
.tab-btn {
  flex: 1;
  padding: var(--space-sm) var(--space-md);
  border: none;
  background: transparent;
  font-family: var(--font-sans);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: color 0.2s, border-color 0.2s;
}
.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
  font-weight: 700;
}
.tab-btn:hover:not(.active) { color: var(--text-primary); }

/* ===== TAB PANELS ===== */
.tab-panel { padding: var(--space-lg); max-width: 760px; margin: 0 auto; }
.tab-panel.hidden { display: none; }

/* ===== CARD ===== */
.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-md);
  box-shadow: var(--shadow);
}

/* ===== BUTTON ===== */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border: none;
  border-radius: var(--radius);
  font-family: var(--font-sans);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
}
.btn:active { transform: scale(0.97); }
.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover { opacity: 0.9; }
.btn-secondary {
  background: transparent;
  border: 1.5px solid var(--border);
  color: var(--text-secondary);
}
.btn-secondary:hover { border-color: var(--accent); color: var(--accent); }

/* ===== FORM ELEMENTS ===== */
.form-group { display: flex; flex-direction: column; gap: var(--space-xs); margin-bottom: var(--space-md); }
.form-label { font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); letter-spacing: 0.05em; text-transform: uppercase; }
select, input[type="number"] {
  padding: var(--space-sm);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  font-family: var(--font-sans);
  font-size: 0.95rem;
  background: var(--card-bg);
  color: var(--text-primary);
  width: 100%;
}
select:focus, input:focus { outline: none; border-color: var(--accent); }

/* ===== HIGHLIGHT / WARN BOX ===== */
.highlight-box {
  background: var(--accent-light);
  border-left: 4px solid var(--accent);
  border-radius: var(--radius);
  padding: var(--space-md);
  font-size: 0.9rem;
  color: #92400e;
  line-height: 1.6;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 600px) {
  .tab-panel { padding: var(--space-md); }
  .tab-btn { font-size: 0.82rem; padding: var(--space-sm); }
}
```

- [ ] **Step 4: 브라우저에서 확인**

```bash
cd camp-helper && open index.html
```

탭 바가 보이고, 패널이 전환 가능 구조인지 확인.

- [ ] **Step 5: 커밋**

```bash
cd camp-helper
git init
git add index.html css/style.css
git commit -m "feat: project scaffold with tab layout and Warm Paper design"
```

---

## Task 2: 성향 검사 데이터 정의

**Files:**
- Create: `camp-helper/data/questions.js`
- Create: `camp-helper/data/types.js`

- [ ] **Step 1: `data/types.js` 작성 — 4가지 성경 캐릭터 유형**

```js
// 각 유형의 key는 점수 집계에 사용됨
export const TYPES = {
  david: {
    key: 'david',
    name: '다윗형',
    emoji: '⚔️',
    trait: '리더십 · 용기',
    bible: '다윗',
    verse: '"여호와께서 나의 빛이요 나의 구원이시니" (시 27:1)',
    description: '앞에서 이끌고 결단을 내리는 리더. 위기 앞에서도 담대하고 팀의 방향을 제시합니다.',
    teamRole: '팀장 / 방향 제시자',
    campActivity: '리더십 팀빌딩, 대표 기도, 그룹 토론 진행',
  },
  joseph: {
    key: 'joseph',
    name: '요셉형',
    emoji: '🌿',
    trait: '인내 · 지혜',
    bible: '요셉',
    verse: '"하나님이 나를 여기 보내신 것은..." (창 45:5)',
    description: '어떤 상황에서도 흔들리지 않는 사람. 지혜롭게 상황을 분석하고 장기적으로 봅니다.',
    teamRole: '조율자 / 문제 해결사',
    campActivity: '묵상 나눔 리드, 갈등 중재, 조용한 섬김',
  },
  barnabas: {
    key: 'barnabas',
    name: '바나바형',
    emoji: '🤝',
    trait: '섬김 · 격려',
    bible: '바나바',
    verse: '"그는 착한 사람이요 성령과 믿음이 충만한 자라" (행 11:24)',
    description: '팀원을 세우고 격려하는 사람. 모두가 소외되지 않도록 살피며 분위기를 따뜻하게 합니다.',
    teamRole: '분위기 메이커 / 돌봄 역할',
    campActivity: '팀원 케어, 소그룹 나눔 진행, 새로 온 친구 돌봄',
  },
  nehemiah: {
    key: 'nehemiah',
    name: '느헤미야형',
    emoji: '✍️',
    trait: '계획 · 실행',
    bible: '느헤미야',
    verse: '"내가 이 일을 우리 하나님의 선한 손이 나를 도우심으로..." (느 2:18)',
    description: '목표를 정하고 체계적으로 실행하는 사람. 준비와 계획을 꼼꼼하게 하여 팀을 완성으로 이끕니다.',
    teamRole: '기획자 / 실행 책임자',
    campActivity: '프로그램 준비, 시간 관리, 물자 점검',
  },
};
```

- [ ] **Step 2: `data/questions.js` 작성 — 상황형 질문 10개**

각 선택지 `type`은 TYPES의 key와 매핑됨.

```js
export const QUESTIONS = [
  {
    id: 1,
    situation: '수련회 첫날, 팀이 처음 모였습니다. 아직 서먹한 분위기입니다.',
    choices: [
      { text: '먼저 일어나 팀을 소개하고 아이스브레이킹을 제안한다.', type: 'david' },
      { text: '상황을 살피며 어떻게 하면 좋을지 조용히 생각한다.', type: 'joseph' },
      { text: '어색해 보이는 팀원에게 먼저 다가가 말을 건다.', type: 'barnabas' },
      { text: '팀 활동 순서와 시간표를 미리 정리해 공유한다.', type: 'nehemiah' },
    ],
  },
  {
    id: 2,
    situation: '팀 게임에서 우리 팀이 불리한 상황이 됐습니다.',
    choices: [
      { text: '"우리 할 수 있어!" 팀을 큰 소리로 격려하며 전략을 바꾼다.', type: 'david' },
      { text: '당장의 결과보다 과정에서 배울 점을 생각한다.', type: 'joseph' },
      { text: '풀죽은 팀원 옆에 앉아 "괜찮아, 잘하고 있어"라고 말한다.', type: 'barnabas' },
      { text: '남은 시간과 규칙을 분석해 가장 효율적인 방법을 찾는다.', type: 'nehemiah' },
    ],
  },
  {
    id: 3,
    situation: '묵상 시간입니다. 말씀을 읽은 후 나눔을 해야 합니다.',
    choices: [
      { text: '먼저 나눔을 시작해 다른 팀원들이 쉽게 말할 수 있도록 분위기를 연다.', type: 'david' },
      { text: '말씀을 깊이 묵상한 후, 삶과 연결된 통찰을 나눈다.', type: 'joseph' },
      { text: '말이 없는 팀원에게 "네 생각은 어때?"라고 부드럽게 물어본다.', type: 'barnabas' },
      { text: '나눔 질문을 정리해 모두가 대답하기 쉽게 구조를 만든다.', type: 'nehemiah' },
    ],
  },
  {
    id: 4,
    situation: '수련회 중 두 팀원 사이에 작은 갈등이 생겼습니다.',
    choices: [
      { text: '즉시 개입해 양쪽 이야기를 듣고 결단을 내려 해결한다.', type: 'david' },
      { text: '서두르지 않고 양쪽이 진정될 때까지 기다렸다가 돕는다.', type: 'joseph' },
      { text: '각자에게 따로 다가가 마음을 먼저 들어준다.', type: 'barnabas' },
      { text: '갈등의 원인을 파악하고 재발 방지 방법을 함께 생각한다.', type: 'nehemiah' },
    ],
  },
  {
    id: 5,
    situation: '자유 시간이 생겼습니다. 팀원들이 각자 쉬고 있습니다.',
    choices: [
      { text: '남은 프로그램을 어떻게 더 잘할지 팀과 함께 전략을 짠다.', type: 'david' },
      { text: '조용한 곳에서 혼자 기도하거나 책을 읽으며 에너지를 충전한다.', type: 'joseph' },
      { text: '혼자 있는 팀원에게 다가가 함께 시간을 보낸다.', type: 'barnabas' },
      { text: '다음 활동 준비물이나 장소를 미리 점검한다.', type: 'nehemiah' },
    ],
  },
  {
    id: 6,
    situation: '팀이 어떤 역할을 맡을지 정해야 합니다.',
    choices: [
      { text: '팀장이 필요하다면 자원한다. 책임지는 것을 두려워하지 않는다.', type: 'david' },
      { text: '팀에 필요한 역할이 무엇인지 파악한 후 빈 자리를 채운다.', type: 'joseph' },
      { text: '다른 사람이 원하는 역할을 먼저 하게 하고 남은 것을 맡는다.', type: 'barnabas' },
      { text: '역할 분배표를 만들어 누가 무엇을 해야 하는지 정리한다.', type: 'nehemiah' },
    ],
  },
  {
    id: 7,
    situation: '예배 시간에 마음이 뜨겁게 감동되었습니다.',
    choices: [
      { text: '바로 결단하고, 이 경험을 팀원들과 나누며 함께 헌신한다.', type: 'david' },
      { text: '조용히 하나님 앞에 앉아 그 감동을 깊이 새긴다.', type: 'joseph' },
      { text: '눈물 흘리는 팀원 옆에 함께 앉아 손을 잡아준다.', type: 'barnabas' },
      { text: '이 감동을 일상에서 어떻게 실천할지 구체적으로 계획한다.', type: 'nehemiah' },
    ],
  },
  {
    id: 8,
    situation: '프로그램이 예상보다 길어져 일정이 밀렸습니다.',
    choices: [
      { text: '즉시 판단하고 팀에게 다음 행동을 지시한다.', type: 'david' },
      { text: '당황하지 않고 상황을 받아들이며 유연하게 대응한다.', type: 'joseph' },
      { text: '지친 팀원들을 살피며 격려와 간식으로 분위기를 살린다.', type: 'barnabas' },
      { text: '남은 시간을 계산해 수정된 시간표를 빠르게 만든다.', type: 'nehemiah' },
    ],
  },
  {
    id: 9,
    situation: '수련회가 끝나고 뒤풀이 자리입니다.',
    choices: [
      { text: '이번 수련회에서 좋았던 점과 다음을 위한 제안을 팀과 나눈다.', type: 'david' },
      { text: '이번 경험에서 배운 것을 혼자 정리하며 감사 기도를 드린다.', type: 'joseph' },
      { text: '한 명 한 명에게 "같이 해서 좋았어"라고 진심으로 말한다.', type: 'barnabas' },
      { text: '다음 수련회를 더 잘 하기 위한 피드백을 메모한다.', type: 'nehemiah' },
    ],
  },
  {
    id: 10,
    situation: '내가 가장 기쁨을 느끼는 순간은?',
    choices: [
      { text: '팀이 내 리드를 따라 하나가 되어 목표를 이뤘을 때', type: 'david' },
      { text: '어려운 상황에서도 포기하지 않고 결국 이겨냈을 때', type: 'joseph' },
      { text: '누군가가 "네 덕분에 힘이 났어"라고 말해줄 때', type: 'barnabas' },
      { text: '내가 세운 계획대로 일이 잘 완성됐을 때', type: 'nehemiah' },
    ],
  },
];
```

- [ ] **Step 3: 커밋**

```bash
git add data/questions.js data/types.js
git commit -m "feat: add personality quiz data — 10 questions and 4 biblical character types"
```

---

## Task 3: 성향 검사 UI + 로직

**Files:**
- Create: `camp-helper/js/quiz.js`
- Modify: `camp-helper/index.html` — `#panel-quiz` 섹션 채우기

- [ ] **Step 1: `js/quiz.js` 작성**

```js
import { QUESTIONS } from '../data/questions.js';
import { TYPES } from '../data/types.js';

// 전역 state — app.js에서 읽어 program.js에 전달
export let quizResult = null; // { topType, scores: {david,joseph,barnabas,nehemiah} }

export function initQuiz(panelEl) {
  panelEl.innerHTML = buildQuizHTML();
  panelEl.querySelector('#quiz-start-btn').addEventListener('click', startQuiz);
}

function buildQuizHTML() {
  return `
    <div id="quiz-intro">
      <h2 class="section-title">🧠 나는 어떤 성경 캐릭터인가?</h2>
      <p class="section-desc">상황형 질문 10개에 답하면 나의 유형을 알 수 있습니다.<br>약 3~5분 소요됩니다.</p>
      <div class="type-preview-grid">
        <div class="type-chip">⚔️ 다윗형 — 리더십·용기</div>
        <div class="type-chip">🌿 요셉형 — 인내·지혜</div>
        <div class="type-chip">🤝 바나바형 — 섬김·격려</div>
        <div class="type-chip">✍️ 느헤미야형 — 계획·실행</div>
      </div>
      <button id="quiz-start-btn" class="btn btn-primary" style="margin-top:1.5rem">검사 시작하기 →</button>
    </div>
    <div id="quiz-body" class="hidden"></div>
    <div id="quiz-result" class="hidden"></div>
  `;
}

function startQuiz() {
  document.getElementById('quiz-intro').classList.add('hidden');
  const body = document.getElementById('quiz-body');
  body.classList.remove('hidden');
  renderQuestion(body, 0, {david:0, joseph:0, barnabas:0, nehemiah:0});
}

function renderQuestion(container, idx, scores) {
  const q = QUESTIONS[idx];
  container.innerHTML = `
    <div class="quiz-progress">
      <div class="progress-bar">
        <div class="progress-fill" style="width:${(idx/QUESTIONS.length)*100}%"></div>
      </div>
      <span class="progress-text">${idx + 1} / ${QUESTIONS.length}</span>
    </div>
    <div class="card quiz-card">
      <p class="quiz-situation">${q.situation}</p>
      <ul class="choice-list">
        ${q.choices.map((c, ci) => `
          <li>
            <button class="choice-btn" data-type="${c.type}" data-idx="${ci}">
              <span class="choice-letter">${['A','B','C','D'][ci]}</span>
              <span class="choice-text">${c.text}</span>
            </button>
          </li>
        `).join('')}
      </ul>
    </div>
  `;
  container.querySelectorAll('.choice-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.dataset.type;
      const next = { ...scores, [type]: scores[type] + 1 };
      if (idx + 1 < QUESTIONS.length) {
        renderQuestion(container, idx + 1, next);
      } else {
        showResult(next);
      }
    });
  });
}

function showResult(scores) {
  document.getElementById('quiz-body').classList.add('hidden');
  const topType = Object.keys(scores).reduce((a, b) => scores[a] >= scores[b] ? a : b);
  quizResult = { topType, scores };

  // 전역 이벤트로 program.js에 알림
  window.dispatchEvent(new CustomEvent('quizComplete', { detail: quizResult }));

  const t = TYPES[topType];
  const resultEl = document.getElementById('quiz-result');
  resultEl.classList.remove('hidden');
  resultEl.innerHTML = `
    <div class="result-card card">
      <div class="result-emoji">${t.emoji}</div>
      <h3 class="result-type-name">${t.name}</h3>
      <p class="result-trait">${t.trait}</p>
      <blockquote class="result-verse">${t.verse}</blockquote>
      <p class="result-desc">${t.description}</p>
      <div class="result-role-box">
        <span class="result-label">팀에서의 역할</span>
        <p>${t.teamRole}</p>
      </div>
      <div class="result-role-box">
        <span class="result-label">수련회 추천 활동</span>
        <p>${t.campActivity}</p>
      </div>
      <div class="score-bar-list">
        ${Object.entries(scores).map(([key, val]) => `
          <div class="score-row">
            <span>${TYPES[key].emoji} ${TYPES[key].name}</span>
            <div class="score-bar-wrap">
              <div class="score-bar-fill" style="width:${(val/QUESTIONS.length)*100}%"></div>
            </div>
            <span class="score-num">${val}</span>
          </div>
        `).join('')}
      </div>
      <p class="result-hint">💡 프로그램 생성 탭으로 이동하면 내 유형에 맞는 수련회 활동을 추천받을 수 있습니다.</p>
      <button class="btn btn-secondary" id="quiz-retry-btn" style="margin-top:1rem">다시 검사하기</button>
    </div>
  `;
  resultEl.querySelector('#quiz-retry-btn').addEventListener('click', () => {
    quizResult = null;
    resultEl.classList.add('hidden');
    document.getElementById('quiz-intro').classList.remove('hidden');
  });
}
```

- [ ] **Step 2: `index.html`의 `#panel-quiz` 안에 마운트 포인트 확인**

`<section id="panel-quiz" ...>` 안이 비어있으면 OK — `initQuiz()`가 innerHTML을 채움.

- [ ] **Step 3: `css/style.css`에 퀴즈 전용 스타일 추가**

```css
/* ===== QUIZ ===== */
.section-title { font-family: var(--font-serif); font-size: 1.5rem; font-style: italic; margin-bottom: var(--space-sm); }
.section-desc { color: var(--text-secondary); line-height: 1.7; margin-bottom: var(--space-md); }

.type-preview-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-sm); margin-top: var(--space-md); }
.type-chip { background: var(--bg-alt); border: 1px solid var(--border); border-radius: var(--radius); padding: var(--space-sm); font-size: 0.85rem; color: var(--text-secondary); }

.quiz-progress { margin-bottom: var(--space-md); }
.progress-bar { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--accent); border-radius: 3px; transition: width 0.3s ease; }
.progress-text { font-size: 0.78rem; color: var(--text-light); display: block; margin-top: var(--space-xs); text-align: right; }

.quiz-card { margin-top: var(--space-md); }
.quiz-situation { font-size: 1rem; font-weight: 500; color: var(--text-primary); line-height: 1.6; margin-bottom: var(--space-md); }

.choice-list { list-style: none; display: flex; flex-direction: column; gap: var(--space-sm); }
.choice-btn {
  width: 100%; display: flex; align-items: flex-start; gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border: 1.5px solid var(--border); border-radius: var(--radius);
  background: var(--card-bg); cursor: pointer;
  text-align: left; font-family: var(--font-sans); font-size: 0.9rem;
  color: var(--text-secondary); transition: border-color 0.2s, background 0.2s;
}
.choice-btn:hover { border-color: var(--accent); background: var(--accent-light); color: var(--text-primary); }
.choice-letter {
  flex-shrink: 0; width: 24px; height: 24px; border-radius: 50%;
  background: var(--bg-alt); border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700; color: var(--text-secondary);
}

/* Result */
.result-card { text-align: center; }
.result-emoji { font-size: 3.5rem; margin-bottom: var(--space-sm); }
.result-type-name { font-family: var(--font-serif); font-size: 1.8rem; font-style: italic; margin-bottom: var(--space-xs); }
.result-trait { color: var(--accent); font-weight: 700; font-size: 0.9rem; margin-bottom: var(--space-md); }
.result-verse { font-family: var(--font-serif); font-style: italic; font-size: 0.95rem; color: var(--text-secondary); border-left: 3px solid var(--accent); padding-left: var(--space-sm); text-align: left; margin-bottom: var(--space-md); }
.result-desc { color: var(--text-secondary); line-height: 1.7; font-size: 0.9rem; margin-bottom: var(--space-md); text-align: left; }
.result-role-box { background: var(--bg-alt); border-radius: var(--radius); padding: var(--space-sm) var(--space-md); text-align: left; margin-bottom: var(--space-sm); }
.result-label { font-size: 0.75rem; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 4px; }
.score-bar-list { display: flex; flex-direction: column; gap: var(--space-xs); margin: var(--space-md) 0; text-align: left; }
.score-row { display: flex; align-items: center; gap: var(--space-sm); font-size: 0.82rem; color: var(--text-secondary); }
.score-row > span:first-child { min-width: 90px; }
.score-bar-wrap { flex: 1; height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
.score-bar-fill { height: 100%; background: var(--accent); border-radius: 4px; }
.score-num { min-width: 20px; text-align: right; font-weight: 600; color: var(--text-primary); }
.result-hint { font-size: 0.82rem; color: var(--text-secondary); background: var(--accent-light); border-radius: var(--radius); padding: var(--space-sm); }
```

- [ ] **Step 4: 브라우저에서 수동 검증**

  - 퀴즈 탭으로 이동 → "검사 시작하기" 클릭
  - 10개 질문 모두 답하기
  - 결과 화면에서 유형명, 설명, 점수 막대 표시 확인
  - "다시 검사하기" → 처음으로 돌아가는지 확인

- [ ] **Step 5: 커밋**

```bash
git add js/quiz.js css/style.css index.html
git commit -m "feat: personality quiz UI with 10 questions and 4 biblical type results"
```

---

## Task 4: 수련회 주제 + 프롬프트 템플릿 데이터

**Files:**
- Create: `camp-helper/data/themes.js`

- [ ] **Step 1: `data/themes.js` 작성**

```js
// typeBoost: 해당 유형이 많을 때 프롬프트에 추가되는 특화 문구
export const THEMES = {
  faith: {
    key: 'faith',
    emoji: '✝️',
    label: '믿음',
    bibleBase: '히브리서 11장 (믿음의 장)',
    teamBuildingIdeas: ['신뢰 낙하 게임', '보이지 않는 길 건너기', '믿음 릴레이 미션'],
    typeBoost: {
      david:    '팀원들이 앞장서서 이끄는 리더십 역할이 필요합니다.',
      joseph:   '인내와 기다림을 배우는 활동을 강조해주세요.',
      barnabas: '서로 격려하고 응원하는 활동을 포함해주세요.',
      nehemiah: '체계적인 단계별 미션 구조를 포함해주세요.',
    },
  },
  love: {
    key: 'love',
    emoji: '❤️',
    label: '사랑',
    bibleBase: '요한복음 13:34-35 / 고린도전서 13장',
    teamBuildingIdeas: ['팀원 감사 편지', '섬김 챌린지', '사랑의 선물 만들기'],
    typeBoost: {
      david:    '희생적 리더십과 팀을 위한 결단을 강조해주세요.',
      joseph:   '오래 참음과 용서의 가치를 활동에 녹여주세요.',
      barnabas: '한 명 한 명을 격려하는 시간을 충분히 포함해주세요.',
      nehemiah: '사랑을 실천하는 구체적 행동 계획을 만들어주세요.',
    },
  },
  courage: {
    key: 'courage',
    emoji: '💪',
    label: '용기',
    bibleBase: '여호수아 1:9 / 다니엘 3장',
    teamBuildingIdeas: ['두려움 극복 도전 과제', '용기 선언문 작성', '불편 도전 릴레이'],
    typeBoost: {
      david:    '두려움 앞에서도 앞장서는 담대함을 강조해주세요.',
      joseph:   '고난을 이겨내는 조용한 용기를 주제로 해주세요.',
      barnabas: '용기가 없는 팀원을 세우고 격려하는 역할을 포함해주세요.',
      nehemiah: '용기 있는 결단을 구체적 실천으로 연결하는 활동을 만들어주세요.',
    },
  },
  hope: {
    key: 'hope',
    emoji: '🌟',
    label: '소망',
    bibleBase: '로마서 15:13 / 예레미야 29:11',
    teamBuildingIdeas: ['비전 보드 만들기', '소망 편지 쓰기', '함께 그리는 미래'],
    typeBoost: {
      david:    '팀의 미래 비전을 선포하는 리더 활동을 포함해주세요.',
      joseph:   '어두운 시간을 지나 소망을 발견한 요셉처럼 묵상 활동을 만들어주세요.',
      barnabas: '서로의 꿈과 소망을 지지하는 나눔 시간을 포함해주세요.',
      nehemiah: '소망을 구체적인 목표와 계획으로 만드는 활동을 포함해주세요.',
    },
  },
  gratitude: {
    key: 'gratitude',
    emoji: '🙏',
    label: '감사',
    bibleBase: '데살로니가전서 5:18 / 시편 107편',
    teamBuildingIdeas: ['감사 돌 놓기', '팀원 감사 릴레이', '24시간 감사 일기'],
    typeBoost: {
      david:    '팀을 이끌며 감사를 선포하는 리더 역할을 포함해주세요.',
      joseph:   '힘든 상황에서도 감사를 발견하는 묵상을 포함해주세요.',
      barnabas: '한 사람 한 사람에게 감사를 표현하는 시간을 만들어주세요.',
      nehemiah: '감사를 삶에서 실천하는 구체적 계획을 세우는 활동을 포함해주세요.',
    },
  },
};

// 프롬프트 생성 함수
export function buildPrompt({ theme, headcount, grade, duration, topType }) {
  const t = THEMES[theme];
  const gradeLabel = { elementary: '초등부', middle: '중등부', high: '고등부' }[grade] || grade;
  const typeBoost = topType ? t.typeBoost[topType] : '';
  const typeNote = topType
    ? `\n참고: 이 팀의 성향 검사 결과 "${THEMES[theme].typeBoost[topType].split('.')[0]}" 유형이 많습니다. ${typeBoost}`
    : '';

  return `아래 조건에 맞는 교회 청소년 수련회 프로그램을 작성해주세요.

[수련회 조건]
- 주제: "${t.label}" (${t.emoji})
- 대상: ${gradeLabel} ${headcount}명
- 활동 가능 시간: ${duration}분
- 핵심 말씀: ${t.bibleBase}${typeNote}

[프로그램 구성 요청]
다음 3가지를 각각 작성해주세요.

1. 팀빌딩 게임 (${Math.round(duration * 0.35)}분)
   - 게임 이름과 규칙
   - 진행 방법 (단계별)
   - 준비물
   - "${t.label}" 주제와의 연결 멘트

2. 말씀 묵상 & 나눔 (${Math.round(duration * 0.4)}분)
   - 핵심 성경 본문 (${t.bibleBase} 기반)
   - 묵상 포인트 2가지
   - 소그룹 나눔 질문 3가지
   - 삶 적용 방법

3. 기도 & 마무리 (${Math.round(duration * 0.25)}분)
   - 기도제목 3가지
   - 축복 선언문 또는 마무리 멘트
   - 다음 수련회까지 실천 과제 1가지

[추가 요청]
- 교사가 현장에서 바로 사용할 수 있도록 진행 멘트도 포함해주세요.
- 기독교 복음주의 관점을 유지해주세요.
- 결과물을 복사해서 카카오톡으로 팀원들에게 바로 공유할 수 있는 형식으로 작성해주세요.`;
}
```

- [ ] **Step 2: 커밋**

```bash
git add data/themes.js
git commit -m "feat: add retreat themes data and prompt builder function"
```

---

## Task 5: 프로그램 생성기 UI + 프롬프트 복사

**Files:**
- Create: `camp-helper/js/program.js`
- Modify: `camp-helper/css/style.css`

- [ ] **Step 1: `js/program.js` 작성**

```js
import { THEMES, buildPrompt } from '../data/themes.js';
import { TYPES } from '../data/types.js';

let currentTopType = null; // quiz.js에서 받아옴

export function initProgram(panelEl) {
  panelEl.innerHTML = buildProgramHTML();
  attachProgramEvents(panelEl);

  // 성향 검사 결과 수신
  window.addEventListener('quizComplete', e => {
    currentTopType = e.detail.topType;
    updateTypeNotice(panelEl, currentTopType);
  });
}

function buildProgramHTML() {
  const themeOptions = Object.values(THEMES).map(t =>
    `<option value="${t.key}">${t.emoji} ${t.label}</option>`
  ).join('');

  return `
    <h2 class="section-title">🎮 수련회 프로그램 생성기</h2>
    <p class="section-desc">수련회 정보를 입력하면 ChatGPT에 붙여넣을 최적화된 프롬프트를 만들어드립니다.</p>

    <div id="type-notice" class="type-notice hidden"></div>

    <div class="card form-card">
      <div class="form-group">
        <label class="form-label" for="sel-theme">수련회 주제</label>
        <select id="sel-theme">${themeOptions}</select>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="sel-grade">학년대</label>
          <select id="sel-grade">
            <option value="elementary">초등부</option>
            <option value="middle" selected>중등부</option>
            <option value="high">고등부</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label" for="inp-headcount">인원수</label>
          <input type="number" id="inp-headcount" min="2" max="200" value="20" placeholder="명">
        </div>
        <div class="form-group">
          <label class="form-label" for="inp-duration">활동 시간</label>
          <input type="number" id="inp-duration" min="30" max="480" value="120" placeholder="분">
        </div>
      </div>
      <button class="btn btn-primary" id="btn-generate" style="width:100%;justify-content:center">
        ✨ 프롬프트 생성하기
      </button>
    </div>

    <div id="prompt-result" class="hidden">
      <div class="prompt-header">
        <h3 class="prompt-title">생성된 프롬프트</h3>
        <div style="display:flex;gap:0.5rem">
          <button class="btn btn-primary" id="btn-copy">📋 복사하기</button>
          <button class="btn btn-secondary" id="btn-chatgpt">ChatGPT 열기 →</button>
        </div>
      </div>
      <div class="highlight-box" style="margin-bottom:1rem;font-size:0.82rem">
        💡 아래 프롬프트를 복사한 후 <strong>ChatGPT</strong> 또는 <strong>Claude.ai</strong>에 붙여넣으세요.
      </div>
      <div class="prompt-box">
        <pre id="prompt-text"></pre>
      </div>
      <p id="copy-feedback" class="copy-feedback hidden">✅ 클립보드에 복사되었습니다!</p>
    </div>
  `;
}

function attachProgramEvents(panelEl) {
  panelEl.querySelector('#btn-generate').addEventListener('click', () => {
    const theme    = panelEl.querySelector('#sel-theme').value;
    const grade    = panelEl.querySelector('#sel-grade').value;
    const headcount = parseInt(panelEl.querySelector('#inp-headcount').value, 10) || 20;
    const duration  = parseInt(panelEl.querySelector('#inp-duration').value, 10) || 120;

    const prompt = buildPrompt({ theme, grade, headcount, duration, topType: currentTopType });
    panelEl.querySelector('#prompt-text').textContent = prompt;
    panelEl.querySelector('#prompt-result').classList.remove('hidden');
    panelEl.querySelector('#prompt-result').scrollIntoView({ behavior: 'smooth' });
  });

  panelEl.querySelector('#btn-copy').addEventListener('click', async () => {
    const text = panelEl.querySelector('#prompt-text').textContent;
    await navigator.clipboard.writeText(text);
    const fb = panelEl.querySelector('#copy-feedback');
    fb.classList.remove('hidden');
    setTimeout(() => fb.classList.add('hidden'), 2500);
  });

  panelEl.querySelector('#btn-chatgpt').addEventListener('click', () => {
    window.open('https://chatgpt.com', '_blank');
  });
}

function updateTypeNotice(panelEl, topType) {
  const notice = panelEl.querySelector('#type-notice');
  if (!topType) { notice.classList.add('hidden'); return; }
  const t = TYPES[topType];
  notice.innerHTML = `
    ${t.emoji} 성향 검사 결과: <strong>${t.name}</strong>이 반영됩니다.
    프로그램 생성 시 ${t.name}에 맞는 활동이 강조됩니다.
  `;
  notice.classList.remove('hidden');
}
```

- [ ] **Step 2: `css/style.css`에 프로그램 생성기 스타일 추가**

```css
/* ===== PROGRAM GENERATOR ===== */
.form-card { margin-bottom: var(--space-md); }
.form-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-sm); }
@media (max-width: 500px) { .form-row { grid-template-columns: 1fr; } }

.type-notice {
  background: #ecfdf5;
  border: 1px solid #6ee7b7;
  border-radius: var(--radius);
  padding: var(--space-sm) var(--space-md);
  font-size: 0.88rem;
  color: #065f46;
  margin-bottom: var(--space-md);
}

.prompt-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--space-sm); margin-bottom: var(--space-sm); }
.prompt-title { font-family: var(--font-serif); font-size: 1.2rem; font-style: italic; }

.prompt-box {
  background: #1c1917;
  border-radius: var(--radius);
  padding: var(--space-md);
  overflow-x: auto;
  margin-bottom: var(--space-sm);
}
.prompt-box pre {
  font-family: 'Courier New', monospace;
  font-size: 0.82rem;
  color: #e7e5e4;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
}
.copy-feedback { font-size: 0.85rem; color: #16a34a; font-weight: 600; text-align: center; padding: var(--space-xs); }
```

- [ ] **Step 3: 브라우저 수동 검증**

  - 주제 선택 → 인원·학년·시간 입력 → "프롬프트 생성하기"
  - 생성된 프롬프트가 표시되는지 확인
  - "복사하기" → 메모장에 붙여넣어 복사 확인
  - "ChatGPT 열기" → 새 탭에서 chatgpt.com 열리는지 확인
  - 성향 검사 완료 후 타입 알림 배너 표시 확인

- [ ] **Step 4: 커밋**

```bash
git add js/program.js css/style.css
git commit -m "feat: program generator UI with prompt builder and clipboard copy"
```

---

## Task 6: 앱 통합 — 탭 전환 + state 연결

**Files:**
- Create: `camp-helper/js/app.js`

- [ ] **Step 1: `js/app.js` 작성**

```js
import { initQuiz } from './quiz.js';
import { initProgram } from './program.js';

const panelProgram = document.getElementById('panel-program');
const panelQuiz    = document.getElementById('panel-quiz');
const tabProgram   = document.getElementById('tab-program');
const tabQuiz      = document.getElementById('tab-quiz');

// 각 탭 패널 초기화
initProgram(panelProgram);
initQuiz(panelQuiz);

// 탭 전환
function switchTab(targetTab) {
  const isProgram = targetTab === 'program';

  tabProgram.classList.toggle('active', isProgram);
  tabQuiz.classList.toggle('active', !isProgram);
  tabProgram.setAttribute('aria-selected', String(isProgram));
  tabQuiz.setAttribute('aria-selected', String(!isProgram));

  panelProgram.classList.toggle('hidden', !isProgram);
  panelQuiz.classList.toggle('hidden', isProgram);
}

tabProgram.addEventListener('click', () => switchTab('program'));
tabQuiz.addEventListener('click',    () => switchTab('quiz'));
```

- [ ] **Step 2: 브라우저 수동 검증 — 전체 흐름**

  1. 앱 열기 → 프로그램 생성기 탭 기본 표시
  2. 성향 검사 탭으로 이동 → 검사 완료 → 결과 확인
  3. 프로그램 생성 탭으로 이동 → 타입 알림 배너 표시 확인
  4. 프롬프트 생성 → topType 반영된 문구 포함 확인
  5. 탭 전환이 빠르고 부드럽게 동작하는지 확인

- [ ] **Step 3: 커밋**

```bash
git add js/app.js
git commit -m "feat: wire tab switching and quiz-to-program state flow"
```

---

## Task 7: README + GitHub Pages 배포

**Files:**
- Create: `camp-helper/README.md`

- [ ] **Step 1: `README.md` 작성**

```markdown
# 수련회 도우미

교회학교 청소년 수련회 준비를 위한 AI 활용 웹앱.

## 기능

- **성경 캐릭터 성향 검사** — 상황형 질문 10개 → 다윗/요셉/바나바/느헤미야형 결과
- **수련회 프로그램 생성** — 주제·인원·학년 입력 → ChatGPT용 최적화 프롬프트 자동 생성

## 사용법

1. [앱 접속](https://your-github-username.github.io/camp-helper)
2. 성향 검사 탭에서 팀원들과 함께 검사
3. 프로그램 생성 탭에서 수련회 정보 입력 → 프롬프트 복사
4. ChatGPT 또는 Claude.ai에 붙여넣기 → 프로그램 완성

## 로컬 실행

```bash
# Python 3
python3 -m http.server 8080
# 브라우저: http://localhost:8080
```

## 배포 (GitHub Pages)

```bash
git remote add origin https://github.com/your-username/camp-helper.git
git push -u origin main
# GitHub 저장소 Settings → Pages → Source: main branch → Save
```

## 기술 스택

HTML5 / CSS3 / Vanilla JavaScript (ES6 모듈) — 외부 의존성 없음.
```

- [ ] **Step 2: GitHub 저장소 생성 및 배포**

```bash
# GitHub에서 'camp-helper' 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/camp-helper.git
git push -u origin main
```

GitHub 저장소 Settings → Pages → Source: Deploy from a branch → Branch: `main` / `/ (root)` → Save

- [ ] **Step 3: 배포 URL 확인**

약 1~2분 후 `https://YOUR_USERNAME.github.io/camp-helper` 접속 확인.

- [ ] **Step 4: QR 코드 생성**

[qr.io](https://qr.io) 또는 [qrcode-monkey.com](https://qrcode-monkey.com)에서 배포 URL로 QR 생성 → 슬라이드 14번에 삽입.

- [ ] **Step 5: 최종 커밋**

```bash
git add README.md
git commit -m "docs: add README with deployment instructions"
git push
```

---

## Self-Review

### 스펙 커버리지 체크

| 스펙 요구사항 | 담당 Task |
|---|---|
| 탭 1: 수련회 주제 선택 (5가지) | Task 4 — themes.js |
| 탭 1: 인원·학년·시간 입력 | Task 5 — program.js |
| 탭 1: 팀빌딩·묵상·기도 포함 프롬프트 | Task 4 — buildPrompt() |
| 탭 1: 복사·공유 기능 | Task 5 — clipboard API |
| 탭 2: 상황형 질문 10개 4지선다 | Task 2 — questions.js |
| 탭 2: 4가지 성경 캐릭터 결과 | Task 2 — types.js |
| 탭 2: 성향 → 프로그램 연동 | Task 3 quizComplete 이벤트 + Task 5 topType |
| GitHub Pages 배포 | Task 7 |
| QR 코드 | Task 7 Step 4 |

### 타입 일관성

- `buildPrompt()` 파라미터 `{ theme, grade, headcount, duration, topType }` — Task 4, 5 모두 동일
- `quizResult.topType` — Task 3에서 emit, Task 5에서 수신, TYPES key와 동일

### 플레이스홀더 없음 확인 ✅
