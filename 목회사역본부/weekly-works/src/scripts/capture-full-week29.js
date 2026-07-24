// 전체 높이 캡처(fullPage 재발방지 표준) — week29(7월 3주차) html-with-images 10장 fullPage 캡처
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const W = '/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works';
const src = path.join(W, 'output/7월/3주차/매일묵상/html-with-images');
const out = path.join(W, 'output/7월/3주차/매일묵상/captured');
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const files = fs.readdirSync(src).filter(f => f.endsWith('-a4.html'));
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 2 });
  for (const f of files) {
    await page.goto('file://' + path.join(src, f), { waitUntil: 'networkidle0' });
    const png = f.replace('.html', '.png');
    await page.screenshot({ path: path.join(out, png), fullPage: true });
    console.log('captured(full):', png);
  }
  await browser.close();
})();
