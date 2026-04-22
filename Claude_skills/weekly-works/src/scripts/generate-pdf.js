#!/usr/bin/env node
/**
 * 나눔지 HTML → PDF 변환 스크립트
 * 사용법: node generate-pdf.js <html-directory>
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const targetDir = process.argv[2];
if (!targetDir) {
  console.error('사용법: node generate-pdf.js <html-directory>');
  process.exit(1);
}

const absDir = path.resolve(targetDir);
if (!fs.existsSync(absDir)) {
  console.error(`디렉토리를 찾을 수 없습니다: ${absDir}`);
  process.exit(1);
}

// HTML 파일 목록
const htmlFiles = fs.readdirSync(absDir).filter(f => f.endsWith('.html'));
if (htmlFiles.length === 0) {
  console.error('HTML 파일이 없습니다.');
  process.exit(1);
}

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  let success = 0;

  for (const htmlFile of htmlFiles) {
    const htmlPath = path.join(absDir, htmlFile);
    const pdfFile = htmlFile.replace('.html', '.pdf');
    const pdfPath = path.join(absDir, pdfFile);

    const page = await browser.newPage();
    await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0', timeout: 30000 });

    // 폰트 로딩 대기
    await page.evaluate(() => document.fonts.ready);
    await new Promise(r => setTimeout(r, 1500));

    await page.pdf({
      path: pdfPath,
      format: 'A4',
      printBackground: true,
      margin: { top: '0', right: '0', bottom: '0', left: '0' },
      preferCSSPageSize: true,
    });

    await page.close();
    console.log(`  ✓ ${pdfFile}`);
    success++;
  }

  await browser.close();
  console.log(`\nPDF 생성 완료: ${success}개`);
  console.log(`저장 위치: ${absDir}`);
})();
