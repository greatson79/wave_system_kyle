#!/usr/bin/env node
/**
 * 카드뉴스 HTML → 개별 슬라이드 PNG 캡쳐 스크립트
 * 사용법: node capture-cardnews.js <slide-preview.html 경로>
 * 예시:   node capture-cardnews.js output/3월/4주차/카드뉴스/slide-preview.html
 *
 * 출력: 같은 폴더에 slide-1.png, slide-2.png, ... 개별 파일 생성
 * 크기: 1080×1080 (540px × deviceScaleFactor 2)
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const htmlPath = process.argv[2];
if (!htmlPath) {
  console.error('사용법: node capture-cardnews.js <slide-preview.html 경로>');
  console.error('예시:   node capture-cardnews.js output/3월/4주차/카드뉴스/slide-preview.html');
  process.exit(1);
}

const absHtml = path.resolve(htmlPath);
if (!fs.existsSync(absHtml)) {
  console.error(`파일을 찾을 수 없습니다: ${absHtml}`);
  process.exit(1);
}

const outDir = path.dirname(absHtml);

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  // 1080×1080 출력을 위해 540px 뷰포트 + 2배 스케일
  await page.setViewport({ width: 540, height: 540, deviceScaleFactor: 2 });

  await page.goto(`file://${absHtml}`, { waitUntil: 'networkidle0', timeout: 30000 });

  // 웹폰트 로딩 대기
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 1500));

  // 모든 .slide 요소 찾기
  const slideCount = await page.$$eval('.slide', els => els.length);

  if (slideCount === 0) {
    console.error('슬라이드를 찾을 수 없습니다 (.slide 클래스 요소 없음)');
    await browser.close();
    process.exit(1);
  }

  console.log(`카드뉴스 캡쳐 시작 (${slideCount}장)`);

  let success = 0;
  const slides = await page.$$('.slide');

  for (let i = 0; i < slides.length; i++) {
    const slideNum = i + 1;
    const pngFile = path.join(outDir, `slide-${slideNum}.png`);

    try {
      await slides[i].screenshot({ path: pngFile, type: 'png' });
      console.log(`  ✓ slide-${slideNum}.png (1080×1080)`);
      success++;
    } catch (err) {
      console.error(`  ✗ slide-${slideNum}.png 실패: ${err.message}`);
    }
  }

  await browser.close();

  console.log(`\n캡쳐 완료`);
  console.log(`├── 성공: ${success}/${slideCount}장`);
  console.log(`└── 저장 위치: ${outDir}`);
})();
