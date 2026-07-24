#!/usr/bin/env node
/**
 * HTML → PNG 자동 캡쳐 스크립트 (메신저·모바일 공유용)
 *
 * ★용도 구분 (CEO 확정 2026-07-20 — 두 스크립트는 통합하지 않고 용도별로 병존한다)
 *   - 이 파일 capture-a4.js       : **메신저·모바일 공유용**. 폭 540px, `.page` 엘리먼트 단위 캡처.
 *   - src/scripts/capture-full-a4.js : **A4 인쇄용 캡처 표준**. 폭 794px + fullPage(문서 전체 높이).
 *     매일묵상 인쇄본 산출은 이쪽을 쓴다(7월 3주차에서 하단 잘림 없음 검증).
 *   용도가 다르므로 어느 한쪽으로 일원화하지 않는다.
 *
 * 사용법:
 *   node capture-a4.js <월> <주차>          예: node capture-a4.js 4월 4주차
 *   node capture-a4.js <week-N_YYYY-MM-DD>  예: node capture-a4.js week-6_2026-02-09 (구형 호환)
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('사용법: node capture-a4.js <월> <주차>');
  console.error('예시:   node capture-a4.js 4월 4주차');
  process.exit(1);
}

const outputRoot = path.join(__dirname, '..', '..', 'output');

// 폴더 경로 결정: 신형(월/주차) 또는 구형(week-N_YYYY) 모두 지원
let weekDir;
if (args.length >= 2) {
  // 신형: "4월" "4주차"
  weekDir = path.join(outputRoot, args[0], args[1]);
} else {
  // 구형: "week-6_2026-02-09"
  const matchDir = fs.readdirSync(outputRoot).find(d => d.startsWith(args[0]));
  if (!matchDir) {
    console.error(`폴더를 찾을 수 없습니다: ${args[0]}`);
    process.exit(1);
  }
  weekDir = path.join(outputRoot, matchDir);
}

if (!fs.existsSync(weekDir)) {
  console.error(`폴더가 없습니다: ${weekDir}`);
  process.exit(1);
}

const BASE = path.join(weekDir, '매일묵상', 'html-with-images');
const OUT  = path.join(weekDir, '매일묵상', 'captured');

const DAYS  = ['mon', 'tue', 'wed', 'thu', 'fri'];
const TYPES = ['adult-a4', 'youth-a4'];

// 9:16 비율 고정 너비 (deviceScaleFactor=2 → 출력 1080px)
const A4_W = 540;
const A4_H = 960; // 초기 뷰포트 높이 (실제 캡처는 콘텐츠 높이 기준)

(async () => {
  if (!fs.existsSync(BASE)) {
    console.error(`html-with-images 폴더 없음: ${BASE}`);
    process.exit(1);
  }
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: A4_W, height: A4_H, deviceScaleFactor: 2 });

  let success = 0, skip = 0;

  for (const day of DAYS) {
    for (const type of TYPES) {
      const htmlFile = path.join(BASE, `${day}-${type}.html`);
      const pngFile  = path.join(OUT,  `${day}-${type}.png`);

      if (!fs.existsSync(htmlFile)) {
        console.log(`  건너뜀: ${day}-${type}.html`);
        skip++;
        continue;
      }

      await page.goto(`file://${htmlFile}`, { waitUntil: 'networkidle0', timeout: 20000 });
      await page.evaluate(() => document.fonts.ready);
      await new Promise(r => setTimeout(r, 800));

      // 고정 너비, 높이 자동 (메신저 배포용 9:16 비율 기준)
      await page.evaluate(() => {
        const el = document.querySelector('.page');
        if (!el) return;
        // 뷰포트 너비에 꽉 맞게, 높이는 콘텐츠 따라 자동
        el.style.width = '100%';
        el.style.height = 'auto';
        el.style.minHeight = '0';
        el.style.overflow = 'visible';
        el.style.boxSizing = 'border-box';
        // body: 패딩 없이 page가 전체 너비 차지
        document.body.style.minHeight = '0';
        document.body.style.padding = '0';
        document.body.style.margin = '0';
        document.body.style.display = 'block';
        document.body.style.backgroundColor = '#fdfcf8';
      });

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
  console.log(`\n캡쳐 완료`);
  console.log(`├── 성공: ${success}개`);
  console.log(`├── 건너뜀: ${skip}개`);
  console.log(`└── 저장 위치: ${OUT}`);
})();
