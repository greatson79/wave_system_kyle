#!/usr/bin/env python3
"""
Master Workflow Web Dashboard Server
"""
import subprocess, json, re, threading, time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

CMUX = "/Applications/cmux.app/Contents/Resources/bin/cmux"
PORT = 7788

WORKFLOWS = {
    "surface:2": {"name": "환경스캐닝",       "icon": "🌍", "approve": "/env-scan:approve"},
    "surface:3": {"name": "글로벌뉴스 크롤링", "icon": "📰", "approve": "승인"},
    "surface:4": {"name": "투자분석",          "icon": "📈", "approve": "승인"},
}

APPROVAL_KEYWORDS = ["approve","승인","review","checkpoint","human","waiting","approval","confirm","검토","확인","대기"]
DONE_KEYWORDS     = ["complete","완료","done","finished","generated","✓","success"]

_status_cache = {}
_history = {s: [] for s in WORKFLOWS}

def get_tree():
    try:
        r = subprocess.run([CMUX,"tree","--all"], capture_output=True, text=True, timeout=5)
        return r.stdout
    except Exception:
        return ""

def parse_titles(tree):
    titles = {}
    for line in tree.splitlines():
        for sid in WORKFLOWS:
            if sid in line and '"' in line:
                parts = line.split('"')
                if len(parts) >= 2:
                    titles[sid] = parts[1]
    return titles

def infer_status(title):
    t = title.lower()
    for kw in DONE_KEYWORDS:
        if kw in t:
            return "done", "완료"
    for kw in APPROVAL_KEYWORDS:
        if kw in t:
            return "approval", "승인 필요"
    spinners = ("✳","⠂","⠐","⠁","⠿","⣿","⠄","⠆","⠇","⡀","⡄")
    if any(title.startswith(s) for s in spinners):
        return "running", "실행 중"
    if title.strip():
        return "processing", "처리 중"
    return "idle", "대기"

def poll():
    while True:
        tree = get_tree()
        titles = parse_titles(tree)
        now = datetime.now().isoformat()
        for sid, wf in WORKFLOWS.items():
            title = titles.get(sid, "")
            state, label = infer_status(title)
            entry = {"time": now, "state": state, "label": label, "title": title}
            _status_cache[sid] = entry
            hist = _history[sid]
            if not hist or hist[-1]["state"] != state:
                hist.append({"time": now, "state": state, "label": label})
                if len(hist) > 50:
                    hist.pop(0)
        time.sleep(8)

def send_approval(surface_id):
    wf = WORKFLOWS.get(surface_id)
    if not wf:
        return False
    r = subprocess.run(
        [CMUX,"send","--surface",surface_id, wf["approve"]+"\n"],
        capture_output=True, text=True, timeout=5
    )
    return r.returncode == 0

HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Master Workflow Dashboard</title>
<style>
  :root {
    --bg: #0d1117; --card: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e;
    --green: #3fb950; --yellow: #d29922; --red: #f85149;
    --blue: #58a6ff; --purple: #bc8cff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'SF Pro Display', -apple-system, sans-serif; min-height: 100vh; padding: 24px; }
  header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; }
  header h1 { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em; }
  header h1 span { color: var(--blue); }
  .timestamp { font-size: 0.8rem; color: var(--muted); }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-bottom: 24px; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; transition: border-color .3s; }
  .card.approval { border-color: var(--red); box-shadow: 0 0 0 1px var(--red), 0 0 20px rgba(248,81,73,.15); animation: pulse 1.5s ease-in-out infinite; }
  .card.done { border-color: var(--green); }
  .card.running { border-color: var(--blue); }
  @keyframes pulse { 0%,100%{box-shadow:0 0 0 1px var(--red),0 0 20px rgba(248,81,73,.15)} 50%{box-shadow:0 0 0 2px var(--red),0 0 30px rgba(248,81,73,.3)} }
  .card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
  .icon { font-size: 1.4rem; }
  .wf-name { font-size: 1rem; font-weight: 600; }
  .badge { margin-left: auto; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
  .badge.running  { background: rgba(88,166,255,.15); color: var(--blue); }
  .badge.approval { background: rgba(248,81,73,.2);  color: var(--red); }
  .badge.done     { background: rgba(63,185,80,.15); color: var(--green); }
  .badge.processing,.badge.idle { background: rgba(139,148,158,.1); color: var(--muted); }
  .progress-title { font-size: 0.78rem; color: var(--muted); margin-bottom: 8px; word-break: break-all; line-height: 1.5; min-height: 36px; }
  .approve-btn { margin-top: 14px; width: 100%; padding: 10px; border: none; border-radius: 8px; background: var(--red); color: #fff; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: opacity .2s; }
  .approve-btn:hover { opacity: .85; }
  .approve-btn:active { opacity: .7; }
  .history { margin-top: 12px; }
  .history-item { display: flex; align-items: center; gap: 8px; padding: 4px 0; border-top: 1px solid var(--border); font-size: 0.72rem; color: var(--muted); }
  .dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
  .dot.running  { background: var(--blue); }
  .dot.approval { background: var(--red); }
  .dot.done     { background: var(--green); }
  .dot.processing,.dot.idle { background: var(--muted); }
  .alert-bar { background: rgba(248,81,73,.12); border: 1px solid var(--red); border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; }
  .alert-bar.hidden { display: none; }
  .alert-bar .bell { font-size: 1.3rem; animation: shake .5s ease-in-out infinite alternate; }
  @keyframes shake { from{transform:rotate(-10deg)} to{transform:rotate(10deg)} }
  .alert-bar p { font-size: 0.88rem; font-weight: 500; }
  .alert-bar strong { color: var(--red); }
  .refresh-bar { text-align: center; color: var(--muted); font-size: 0.75rem; margin-top: 16px; }
  .refresh-bar span { color: var(--blue); }
</style>
</head>
<body>
<header>
  <h1>🎛️ Master <span>Workflow</span> Dashboard</h1>
  <div class="timestamp" id="ts">-</div>
</header>

<div class="alert-bar hidden" id="alert-bar">
  <div class="bell">🔔</div>
  <p><strong>승인 필요</strong> — <span id="alert-msg"></span></p>
</div>

<div class="grid" id="grid"></div>
<div class="refresh-bar">자동 갱신: <span id="countdown">8</span>초 후</div>

<script>
let countdown = 8;

async function fetchStatus() {
  const r = await fetch('/api/status');
  return r.json();
}

async function approve(surfaceId) {
  const btn = document.querySelector(`[data-surface="${surfaceId}"]`);
  if (btn) { btn.disabled = true; btn.textContent = '전송 중...'; }
  await fetch('/api/approve', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({surface: surfaceId})
  });
  setTimeout(render, 1500);
}

async function render() {
  const data = await fetchStatus();
  const now = new Date().toLocaleString('ko-KR');
  document.getElementById('ts').textContent = now;

  const grid = document.getElementById('grid');
  grid.innerHTML = '';

  const alertBar = document.getElementById('alert-bar');
  const alertMsg = document.getElementById('alert-msg');
  const approvalNeeded = [];

  for (const [sid, wf] of Object.entries(data.workflows)) {
    const { name, icon, state, label, title, history } = wf;
    if (state === 'approval') approvalNeeded.push(name);

    const card = document.createElement('div');
    card.className = `card ${state}`;
    card.innerHTML = `
      <div class="card-header">
        <span class="icon">${icon}</span>
        <span class="wf-name">${name}</span>
        <span class="badge ${state}">${label}</span>
      </div>
      <div class="progress-title">${title || '—'}</div>
      ${state === 'approval' ? `<button class="approve-btn" data-surface="${sid}" onclick="approve('${sid}')">✅ 지금 승인</button>` : ''}
      <div class="history">
        ${(history||[]).slice(-4).reverse().map(h => `
          <div class="history-item">
            <div class="dot ${h.state}"></div>
            <span>${new Date(h.time).toLocaleTimeString('ko-KR')}</span>
            <span>${h.label}</span>
          </div>`).join('')}
      </div>
    `;
    grid.appendChild(card);
  }

  if (approvalNeeded.length > 0) {
    alertBar.classList.remove('hidden');
    alertMsg.textContent = approvalNeeded.join(', ') + ' 워크플로우가 승인을 기다리고 있습니다.';
    if (document.hidden === false) {
      new Notification('워크플로우 승인 필요', { body: alertMsg.textContent });
    }
  } else {
    alertBar.classList.add('hidden');
  }
}

// 알림 권한
if (Notification.permission === 'default') Notification.requestPermission();

// 첫 렌더
render();

// 카운트다운 + 자동 갱신
setInterval(() => {
  countdown--;
  document.getElementById('countdown').textContent = countdown;
  if (countdown <= 0) {
    countdown = 8;
    render();
  }
}, 1000);
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path == "/api/status":
            payload = {"workflows": {}}
            for sid, wf in WORKFLOWS.items():
                cache = _status_cache.get(sid, {})
                payload["workflows"][sid] = {
                    "name":    wf["name"],
                    "icon":    wf["icon"],
                    "state":   cache.get("state", "idle"),
                    "label":   cache.get("label", "대기"),
                    "title":   cache.get("title", ""),
                    "history": _history.get(sid, []),
                }
            self._json(payload)
        elif self.path in ("/", "/index.html"):
            self._html(HTML)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/approve":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            ok = send_approval(body.get("surface",""))
            self._json({"ok": ok})
        else:
            self.send_error(404)

    def _json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    import socket
    # 기존 포트 점유 프로세스 종료
    try:
        with socket.socket() as s:
            s.bind(("", PORT))
    except OSError:
        import os
        os.system(f"lsof -ti :{PORT} | xargs kill -9 2>/dev/null")
        time.sleep(1)
    t = threading.Thread(target=poll, daemon=True)
    t.start()
    print(f"Dashboard server: http://localhost:{PORT}", flush=True)
    HTTPServer(("", PORT), Handler).serve_forever()
