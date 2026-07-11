const sampleText = `예수님이 물을 포도주로 바꾸신 곳은? | 가나 혼인잔치
니고데모가 예수님께 찾아온 때는? | 밤
예수님께서 사마리아 여인에게 말씀하신 생수는 무엇을 의미할까요? | 예수님이 주시는 영원한 생명
오병이어 후 남은 바구니는 몇 개였나요? | 열두 바구니
나사로는 무덤에 있은 지 며칠 만에 살아났나요? | 나흘`;

const app = document.querySelector(".app");
const quizInput = document.querySelector("#quizInput");
const quizGrid = document.querySelector("#quizGrid");
const parseStatus = document.querySelector("#parseStatus");
const boardSummary = document.querySelector("#boardSummary");
const startButton = document.querySelector("#startButton");
const loadSampleButton = document.querySelector("#loadSampleButton");
const downloadButton = document.querySelector("#downloadButton");
const applyButton = document.querySelector("#applyButton");
const backButton = document.querySelector("#backButton");
const fullscreenButton = document.querySelector("#fullscreenButton");
const progressLabel = document.querySelector("#progressLabel");
const questionStage = document.querySelector("#questionStage");
const questionText = document.querySelector("#questionText");
const answerButton = document.querySelector("#answerButton");
const answerPanel = document.querySelector("#answerPanel");
const answerText = document.querySelector("#answerText");
const prevButton = document.querySelector("#prevButton");
const nextButton = document.querySelector("#nextButton");

let quizzes = [];
let currentIndex = 0;
let touchStartX = 0;

function parseQuizzes(rawText) {
  const normalized = rawText.replace(/\r\n/g, "\n").trim();
  if (!normalized) return [];

  const lines = normalized
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const hasInlineAnswers = lines.some((line) => getDivider(line));

  if (hasInlineAnswers) {
    return lines.map(parseLineQuiz).filter(Boolean);
  }

  const blocks = normalized
    .split(/\n\s*\n/)
    .map((block) => block.split("\n").map((line) => line.trim()).filter(Boolean))
    .filter((block) => block.length > 0);

  if (blocks.length > 1) {
    return blocks
      .map((block) => makeQuiz(block[0], block.slice(1).join("\n")))
      .filter(Boolean);
  }

  return lines.map((line) => makeQuiz(line, ""));
}

function parseLineQuiz(line) {
  const divider = getDivider(line);
  if (!divider) return makeQuiz(line, "");
  const [question, ...answerParts] = line.split(divider);
  return makeQuiz(question, answerParts.join(divider));
}

function getDivider(line) {
  return ["|", "=>"].find((divider) => line.includes(divider));
}

function makeQuiz(question, answer) {
  const cleanQuestion = (question || "").trim();
  const cleanAnswer = (answer || "").trim();
  if (!cleanQuestion) return null;
  return {
    question: cleanQuestion,
    answer: cleanAnswer || "정답이 입력되지 않았습니다.",
  };
}

function applyInput() {
  quizzes = parseQuizzes(quizInput.value);
  currentIndex = 0;
  renderDashboard();
}

function renderDashboard() {
  quizGrid.innerHTML = "";
  startButton.disabled = quizzes.length === 0;
  boardSummary.textContent =
    quizzes.length === 0
      ? "문제를 입력하면 여기에 카드가 표시됩니다."
      : `총 ${quizzes.length}개의 문제가 준비되었습니다.`;
  parseStatus.textContent =
    quizzes.length === 0 ? "인식된 문제가 없습니다." : `${quizzes.length}개 문제를 불러왔습니다.`;

  quizzes.forEach((quiz, index) => {
    const card = document.createElement("button");
    card.className = "quiz-card";
    card.type = "button";
    card.innerHTML = `<span>Q${index + 1}</span><strong></strong>`;
    card.querySelector("strong").textContent = quiz.question;
    card.addEventListener("click", () => openPresenter(index));
    quizGrid.append(card);
  });
}

function openPresenter(index) {
  if (quizzes.length === 0) return;
  currentIndex = clampIndex(index);
  app.dataset.view = "presenter";
  renderPresenter();
  questionStage.focus();
}

function renderPresenter() {
  const quiz = quizzes[currentIndex];
  progressLabel.textContent = `Q${currentIndex + 1} / ${quizzes.length}`;
  questionText.textContent = quiz.question;
  answerText.textContent = quiz.answer;
  answerPanel.hidden = true;
  answerButton.textContent = "정답 보기";
  prevButton.disabled = quizzes.length <= 1;
  nextButton.disabled = quizzes.length <= 1;
}

function showDashboard() {
  app.dataset.view = "dashboard";
}

function moveQuestion(step) {
  if (quizzes.length <= 1) return;
  currentIndex = clampIndex(currentIndex + step);
  renderPresenter();
}

function clampIndex(index) {
  if (index < 0) return quizzes.length - 1;
  if (index >= quizzes.length) return 0;
  return index;
}

function toggleAnswer() {
  answerPanel.hidden = !answerPanel.hidden;
  answerButton.textContent = answerPanel.hidden ? "정답 보기" : "정답 숨기기";
}

function downloadStandaloneHtml() {
  const exportQuizzes = parseQuizzes(quizInput.value);
  if (exportQuizzes.length === 0) {
    parseStatus.textContent = "다운로드할 문제가 없습니다.";
    return;
  }

  const html = buildStandaloneHtml(exportQuizzes);
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "bible-quiz.html";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  parseStatus.textContent = "bible-quiz.html 다운로드를 준비했습니다.";
}

function buildStandaloneHtml(items) {
  const quizJson = JSON.stringify(items).replace(/</g, "\\u003c");
  return `<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>성경퀴즈</title>
  <style>
    :root { font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111827; background: #f6f8fb; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #f6f8fb; }
    button { border: 0; cursor: pointer; font: inherit; }
    .dashboard { max-width: 1120px; margin: 0 auto; padding: 28px; }
    .top { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
    h1, h2, p { margin: 0; }
    h1 { font-size: 28px; }
    p { color: #667085; line-height: 1.55; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
    .card { min-height: 130px; padding: 16px; text-align: left; background: #fff; border: 1px solid #d9e0ea; border-radius: 8px; }
    .card:hover { border-color: #2563eb; box-shadow: 0 10px 24px rgba(15, 23, 42, .08); }
    .card span { display: block; margin-bottom: 10px; color: #2563eb; font-size: 13px; font-weight: 800; }
    .presenter { display: none; min-height: 100vh; background: #0f172a; color: #fff; grid-template-rows: 64px 1fr auto; }
    body.show .dashboard { display: none; }
    body.show .presenter { display: grid; }
    .bar, .dock { display: grid; align-items: center; gap: 12px; padding: 14px 18px; background: #111827; }
    .bar { grid-template-columns: 120px 1fr 120px; border-bottom: 1px solid #334155; text-align: center; }
    .stage { display: grid; align-content: center; justify-items: center; gap: 20px; padding: clamp(24px, 6vw, 84px); text-align: center; }
    .label { color: #93c5fd; font-weight: 800; }
    .question { max-width: 1100px; font-size: clamp(34px, 6vw, 76px); line-height: 1.25; font-weight: 800; }
    .dock { grid-template-columns: 92px minmax(160px, 1fr) 92px; border-top: 1px solid #334155; }
    .ghost, .nav { min-height: 42px; border-radius: 8px; background: #1e293b; color: #e5edf8; font-weight: 800; }
    .answer-btn { min-height: 42px; border-radius: 8px; background: #fff; color: #0f172a; font-weight: 800; }
    .answer { grid-column: 1 / -1; padding: 16px; border: 1px solid #475569; border-radius: 8px; background: #172033; text-align: center; font-size: clamp(22px, 3vw, 34px); font-weight: 800; }
    @media (max-width: 720px) { .dashboard { padding: 14px; } .top { align-items: stretch; flex-direction: column; } .bar { grid-template-columns: 1fr; } .dock { grid-template-columns: 74px minmax(0, 1fr) 74px; } }
  </style>
</head>
<body>
  <main class="dashboard">
    <div class="top">
      <div>
        <h1>성경퀴즈</h1>
        <p>문제를 클릭하면 전체화면 발표 화면으로 이동합니다.</p>
      </div>
      <button class="ghost" type="button" onclick="openSlide(0)">첫 문제 시작</button>
    </div>
    <div class="grid" id="grid"></div>
  </main>
  <main class="presenter">
    <header class="bar">
      <button class="ghost" type="button" onclick="closeSlide()">대시보드</button>
      <strong id="progress"></strong>
      <button class="ghost" type="button" onclick="toggleFullscreen()">전체화면</button>
    </header>
    <section class="stage" id="stage">
      <p class="label">성경퀴즈</p>
      <h2 class="question" id="question"></h2>
    </section>
    <footer class="dock">
      <button class="nav" type="button" onclick="move(-1)">이전</button>
      <button class="answer-btn" type="button" onclick="toggleAnswer()" id="answerButton">정답 보기</button>
      <button class="nav" type="button" onclick="move(1)">다음</button>
      <div class="answer" id="answer" hidden></div>
    </footer>
  </main>
  <script>
    const quizzes = ${quizJson};
    let index = 0;
    let startX = 0;
    const grid = document.querySelector("#grid");
    const progress = document.querySelector("#progress");
    const question = document.querySelector("#question");
    const answer = document.querySelector("#answer");
    const answerButton = document.querySelector("#answerButton");
    quizzes.forEach((quiz, itemIndex) => {
      const card = document.createElement("button");
      card.className = "card";
      card.type = "button";
      card.innerHTML = "<span>Q" + (itemIndex + 1) + "</span><strong></strong>";
      card.querySelector("strong").textContent = quiz.question;
      card.addEventListener("click", () => openSlide(itemIndex));
      grid.append(card);
    });
    function openSlide(nextIndex) { index = normalize(nextIndex); document.body.classList.add("show"); render(); }
    function closeSlide() { document.body.classList.remove("show"); }
    function render() { const quiz = quizzes[index]; progress.textContent = "Q" + (index + 1) + " / " + quizzes.length; question.textContent = quiz.question; answer.textContent = quiz.answer; answer.hidden = true; answerButton.textContent = "정답 보기"; }
    function normalize(nextIndex) { if (nextIndex < 0) return quizzes.length - 1; if (nextIndex >= quizzes.length) return 0; return nextIndex; }
    function move(step) { index = normalize(index + step); render(); }
    function toggleAnswer() { answer.hidden = !answer.hidden; answerButton.textContent = answer.hidden ? "정답 보기" : "정답 숨기기"; }
    async function toggleFullscreen() { if (!document.fullscreenElement) await document.documentElement.requestFullscreen?.(); else await document.exitFullscreen?.(); }
    document.addEventListener("keydown", (event) => { if (!document.body.classList.contains("show")) return; if (event.key === "ArrowLeft") move(-1); if (event.key === "ArrowRight") move(1); if (event.key === " " || event.key === "Enter") { event.preventDefault(); toggleAnswer(); } if (event.key === "Escape") closeSlide(); });
    document.querySelector("#stage").addEventListener("touchstart", (event) => { startX = event.changedTouches[0].screenX; });
    document.querySelector("#stage").addEventListener("touchend", (event) => { const delta = event.changedTouches[0].screenX - startX; if (Math.abs(delta) >= 48) move(delta > 0 ? -1 : 1); });
  </script>
</body>
</html>`;
}

async function requestFullscreen() {
  const presenter = document.querySelector(".presenter");
  if (!document.fullscreenElement) {
    await presenter.requestFullscreen?.();
    return;
  }
  await document.exitFullscreen?.();
}

loadSampleButton.addEventListener("click", () => {
  quizInput.value = sampleText;
  applyInput();
});

downloadButton.addEventListener("click", downloadStandaloneHtml);
applyButton.addEventListener("click", applyInput);
startButton.addEventListener("click", () => openPresenter(0));
backButton.addEventListener("click", showDashboard);
fullscreenButton.addEventListener("click", requestFullscreen);
answerButton.addEventListener("click", toggleAnswer);
prevButton.addEventListener("click", () => moveQuestion(-1));
nextButton.addEventListener("click", () => moveQuestion(1));

document.addEventListener("keydown", (event) => {
  if (app.dataset.view !== "presenter") return;
  if (event.key === "ArrowLeft") moveQuestion(-1);
  if (event.key === "ArrowRight") moveQuestion(1);
  if (event.key === " " || event.key === "Enter") {
    event.preventDefault();
    toggleAnswer();
  }
  if (event.key === "Escape") showDashboard();
});

questionStage.addEventListener("touchstart", (event) => {
  touchStartX = event.changedTouches[0].screenX;
});

questionStage.addEventListener("touchend", (event) => {
  const deltaX = event.changedTouches[0].screenX - touchStartX;
  if (Math.abs(deltaX) < 48) return;
  moveQuestion(deltaX > 0 ? -1 : 1);
});

quizInput.value = sampleText;
applyInput();
