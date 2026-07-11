const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 540, height: 540, deviceScaleFactor: 2 });

  const filePath = path.resolve(
    '/Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works',
    'output/6월/2주차/카드뉴스/카드뉴스_24주차.html'
  );

  await page.goto('file://' + filePath, { waitUntil: 'networkidle0', timeout: 20000 });

  // 슬라이드 1 — 세이지 표지
  const s1 = await page.$('.slide-1');
  await s1.screenshot({ path: '/tmp/preview_slide1.png' });

  // 슬라이드 2 — 크림 구절
  const s2 = await page.$('.slide-2');
  await s2.screenshot({ path: '/tmp/preview_slide2.png' });

  // 슬라이드 5 — 크림 변화
  const s5 = await page.$('.slide-5');
  await s5.screenshot({ path: '/tmp/preview_slide5.png' });

  await browser.close();
  console.log('캡처 완료: /tmp/preview_slide1.png, slide2, slide5');
})().catch(e => { console.error(e.message); process.exit(1); });
