#!/usr/bin/env node
/**
 * 카드뉴스 HTML → 다중 페이지 PDF 생성 스크립트
 * 4:5 비율 (1080×1350 / 285.75mm×357.19mm) 각 슬라이드가 1페이지
 *
 * 사용법: node generate-cardnews-pdf.js <slide-preview.html 경로>
 * 예시:   node generate-cardnews-pdf.js output/4월/성금요일/카드뉴스/slide-preview.html
 *
 * 출력: 같은 폴더에 cardnews.pdf 생성
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const htmlPath = process.argv[2];
if (!htmlPath) {
  console.error('사용법: node generate-cardnews-pdf.js <slide-preview.html 경로>');
  console.error('예시:   node generate-cardnews-pdf.js output/4월/성금요일/카드뉴스/slide-preview.html');
  process.exit(1);
}

const absHtml = path.resolve(htmlPath);
if (!fs.existsSync(absHtml)) {
  console.error(`파일을 찾을 수 없습니다: ${absHtml}`);
  process.exit(1);
}

const outDir = path.dirname(absHtml);
const pdfPath = path.join(outDir, 'cardnews.pdf');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  // PDF 렌더링용 뷰포트 (540px 너비 = CSS 기준)
  await page.setViewport({ width: 540, height: 675, deviceScaleFactor: 1 });

  await page.goto(`file://${absHtml}`, { waitUntil: 'networkidle0', timeout: 30000 });

  // 웹폰트 로딩 대기
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 2000));

  console.log('PDF 생성 중...');

  await page.pdf({
    path: pdfPath,
    printBackground: true,
    preferCSSPageSize: true,   // HTML @page 규격 사용 (285.75mm × 357.19mm)
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
  });

  await browser.close();

  console.log(`\nPDF 생성 완료`);
  console.log(`├── 페이지 크기: 285.75mm × 357.19mm  (= 1080×1350px @ 96dpi)`);
  console.log(`└── 저장 위치: ${pdfPath}`);
})();
