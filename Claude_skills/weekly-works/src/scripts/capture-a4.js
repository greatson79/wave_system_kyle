#!/usr/bin/env node
/**
 * A4 HTML → PNG 자동 캡쳐 스크립트
 * 사용법: node capture-a4.js [주차번호]
 * 예시:   node capture-a4.js 6
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const weekNum = process.argv[2];
if (!weekNum) {
  console.error('사용법: node capture-a4.js [주차번호]');
  console.error('예시:   node capture-a4.js 6');
  process.exit(1);
}

// output/week-{N}_YYYY-MM-DD/ 폴더를 동적으로 탐색
const outputRoot = path.join(__dirname, '..', '..', 'output');
const matchDir = fs.readdirSync(outputRoot).find(d => d.startsWith(`week-${weekNum}_`));
if (!matchDir) {
  console.error(`week-${weekNum}_ 로 시작하는 폴더를 output/ 에서 찾을 수 없습니다.`);
  process.exit(1);
}
const weekDir = path.join(outputRoot, matchDir);
const BASE = path.join(weekDir, 'html-with-images');
const OUT = path.join(weekDir, 'captured');

const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri'];
const TYPES = ['adult-a4', 'youth-a4'];

(async () => {
  // HTML 폴더 확인
  if (!fs.existsSync(BASE)) {
    console.error(`HTML 폴더를 찾을 수 없습니다: ${BASE}`);
    process.exit(1);
  }

  // 출력 폴더 생성
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  // A4 크기 뷰포트 (2배 해상도로 선명하게)
  await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 2 });

  let success = 0;
  let skip = 0;

  for (const day of DAYS) {
    for (const type of TYPES) {
      const htmlFile = path.join(BASE, `${day}-${type}.html`);
      const pngFile = path.join(OUT, `${day}-${type}.png`);

      if (!fs.existsSync(htmlFile)) {
        console.log(`  건너뜀: ${day}-${type}.html (파일 없음)`);
        skip++;
        continue;
      }

      await page.goto(`file://${htmlFile}`, { waitUntil: 'networkidle0', timeout: 15000 });

      // 폰트 로딩 대기
      await page.evaluate(() => document.fonts.ready);
      await new Promise(r => setTimeout(r, 1000));

      // .page 높이 제한 해제 → 내용이 잘리지 않도록
      await page.evaluate(() => {
        const el = document.querySelector('.page');
        if (el) {
          el.style.height = 'auto';
          el.style.minHeight = '297mm';
        }
      });

      // .page 요소만 캡쳐 (전체 내용 포함)
      const element = await page.$('.page');
      if (element) {
        await element.screenshot({ path: pngFile, type: 'png' });
      } else {
        await page.screenshot({ path: pngFile, type: 'png', fullPage: false });
      }

      console.log(`  ✓ ${day}-${type}.png`);
      success++;
    }
  }

  await browser.close();

  console.log(`\n캡쳐 완료 (week-${weekNum})`);
  console.log(`├── 성공: ${success}개`);
  console.log(`├── 건너뜀: ${skip}개`);
  console.log(`└── 저장 위치: ${OUT}`);
})();
