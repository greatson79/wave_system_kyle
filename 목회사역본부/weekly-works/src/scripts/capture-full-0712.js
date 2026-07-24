// 전체 높이 캡처(주인님 1번안) — html-with-images 10장 fullPage 재캡처
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const W = '/Users/kylechoi/Desktop/Ai_works/목회사역본부/weekly-works';
const src = path.join(W, 'output/7월/2주차/매일묵상/html-with-images');
const out = path.join(W, 'output/7월/2주차/매일묵상/captured');
(async () => {
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
