#!/usr/bin/env node
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const htmlPath = process.argv[2];
const outPath = process.argv[3];
if (!htmlPath || !outPath) {
  console.error('사용법: node capture-single-card.js <html경로> <출력png경로>');
  process.exit(1);
}

const absHtml = path.resolve(htmlPath);
if (!fs.existsSync(absHtml)) {
  console.error(`파일을 찾을 수 없습니다: ${absHtml}`);
  process.exit(1);
}

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1350, deviceScaleFactor: 1 });
  await page.goto(`file://${absHtml}`, { waitUntil: 'networkidle0', timeout: 30000 });
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 1200));

  const card = await page.$('.card');
  if (!card) {
    console.error('.card 요소를 찾을 수 없습니다');
    await browser.close();
    process.exit(1);
  }
  await card.screenshot({ path: path.resolve(outPath), type: 'png' });
  await browser.close();
  console.log(`저장 완료: ${outPath}`);
})();
