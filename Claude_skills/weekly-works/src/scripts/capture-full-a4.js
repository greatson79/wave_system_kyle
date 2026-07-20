#!/usr/bin/env node
/**
 * 매일묵상 A4 HTML → PNG fullPage 캡처 (하단 잘림 재발방지 표준)
 *
 * ★용도 구분 (CEO 확정 2026-07-20 — 두 스크립트는 통합하지 않고 용도별로 병존한다)
 *   - 이 파일 capture-full-a4.js : **A4 인쇄용 캡처 표준**. 폭 794px + fullPage로
 *     문서 전체 높이를 캡처한다. 7월 3주차(week29)에서 하단 잘림 없음이 검증된 조건이며,
 *     7월 4주차(week30)부터 이 스크립트를 정본으로 사용한다.
 *   - src/scripts/capture-a4.js : **메신저·모바일 공유용 캡처**. 폭 540px, `.page`
 *     엘리먼트 단위 캡처. 인쇄물 용도로 쓰지 말 것(A4 규격과 다름).
 *   용도가 다르므로 어느 한쪽으로 일원화하지 않는다.
 *
 * 사용법: node capture-full-a4.js <월> <주차>
 * 예시:   node capture-full-a4.js 7월 4주차
 *
 * 유래: 7월 3주차의 일회용 하드코딩 스크립트(capture-full-week29.js)를 인자 기반으로
 *       범용화한 것. 경로 하드코딩 제거 · 인자 검증 · browser finally 정리 · fonts.ready 대기.
 *
 * 보안 경계/TOCTOU 위협모델: 캡처 전과 각 파일의 page.goto·screenshot 직전에 실제 경로와
 * 심링크를 재검증한다. 이 스크립트는 단일 사용자 로컬 개발기에서 소유자가 수동 실행하는
 * 내부 산출 도구이므로, 로컬 쓰기권한을 가진 공격자는 이미 스크립트 자체를 변조할 수 있어
 * 디렉터리 FD 고정이 실질 방어선을 늘리지 않는다. 다중 사용자 또는 CI 공유 환경으로 이관하면
 * 디렉터리 FD 기반 처리나 전용 권한 디렉터리를 포함해 위협모델을 재평가해야 한다.
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const A4_WIDTH = 794;
const A4_HEIGHT = 1123;
const DEVICE_SCALE_FACTOR = 2;
const MONTH_PATTERN = /^[0-9]{1,2}월$/;
const WEEK_PATTERN = /^[0-9]{1,2}주차$/;

const [month, week] = process.argv.slice(2);

if (!month || !week) {
  console.error('사용법: node capture-full-a4.js <월> <주차>   예: node capture-full-a4.js 7월 4주차');
  process.exit(1);
}

if (!MONTH_PATTERN.test(month) || !WEEK_PATTERN.test(week)) {
  console.error('월/주차 인자 형식 오류: 월은 N월, 주차는 N주차 형식이어야 합니다.');
  process.exit(1);
}

const workspaceRoot = path.resolve(__dirname, '..', '..');
const outputRoot = path.resolve(workspaceRoot, 'output');
const devotionDir = path.resolve(outputRoot, month, week, '매일묵상');
const srcDir = path.resolve(devotionDir, 'html-with-images');
const outDir = path.resolve(devotionDir, 'captured');

function isWithinDirectory(rootPath, targetPath) {
  const relativePath = path.relative(rootPath, targetPath);
  return relativePath && !relativePath.startsWith(`..${path.sep}`) && !path.isAbsolute(relativePath);
}

if (!isWithinDirectory(outputRoot, srcDir) || !isWithinDirectory(outputRoot, outDir)) {
  console.error('캡처 경로 오류: source/output 경로는 workspace output 하위여야 합니다.');
  process.exit(1);
}

function findSymbolicLinkComponent(rootPath, targetPath) {
  const components = path.relative(rootPath, targetPath).split(path.sep);
  let currentPath = rootPath;

  for (const component of components) {
    currentPath = path.join(currentPath, component);
    if (fs.existsSync(currentPath) && fs.lstatSync(currentPath).isSymbolicLink()) {
      return currentPath;
    }
  }

  return null;
}

function assertCapturePaths() {
  if (fs.lstatSync(workspaceRoot).isSymbolicLink()) {
    throw new Error('workspaceRoot 심링크는 허용되지 않습니다.');
  }
  if (fs.lstatSync(outputRoot).isSymbolicLink()) {
    throw new Error('outputRoot 심링크는 허용되지 않습니다.');
  }

  const realWorkspaceRoot = fs.realpathSync(workspaceRoot);
  const realOutputRoot = fs.realpathSync(outputRoot);
  const expectedOutputRoot = path.join(realWorkspaceRoot, 'output');
  if (realOutputRoot !== expectedOutputRoot) {
    throw new Error('outputRoot 실경로가 workspaceRoot/output와 일치하지 않습니다.');
  }

  if (!fs.existsSync(srcDir)) {
    throw new Error(`html-with-images 폴더 없음: ${srcDir}`);
  }

  const realSrcDir = fs.realpathSync(srcDir);
  if (!isWithinDirectory(realOutputRoot, realSrcDir)) {
    throw new Error('html-with-images 심링크/실경로는 workspace output 하위여야 합니다.');
  }

  const outputSymlink = findSymbolicLinkComponent(outputRoot, outDir);
  if (outputSymlink) {
    throw new Error(`출력 경로의 심링크 구성요소는 허용되지 않습니다: ${outputSymlink}`);
  }
}

try {
  assertCapturePaths();
} catch (error) {
  console.error(`캡처 경로 오류: ${error.message}`);
  process.exit(1);
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });

  const files = fs.readdirSync(srcDir).filter((f) => f.endsWith('-a4.html')).sort();
  if (files.length === 0) {
    console.error(`캡처 대상 A4 HTML이 없습니다: ${srcDir}`);
    process.exit(1);
  }

  const browser = await puppeteer.launch({ headless: 'new' });
  try {
    const page = await browser.newPage();
    await page.setViewport({
      width: A4_WIDTH,
      height: A4_HEIGHT,
      deviceScaleFactor: DEVICE_SCALE_FACTOR
    });

    for (const file of files) {
      try {
        assertCapturePaths();
      } catch (error) {
        console.error(`캡처 경로 오류: ${error.message}`);
        process.exitCode = 1;
        return;
      }
      await page.goto(`file://${path.join(srcDir, file)}`, { waitUntil: 'networkidle0', timeout: 30000 });
      await page.evaluate(() => document.fonts.ready);

      const pngName = file.replace('.html', '.png');
      try {
        assertCapturePaths();
      } catch (error) {
        console.error(`캡처 경로 오류: ${error.message}`);
        process.exitCode = 1;
        return;
      }
      await page.screenshot({ path: path.join(outDir, pngName), fullPage: true });
      console.log(`  ✓ ${pngName}`);
    }
  } finally {
    await browser.close();
  }

  console.log(`\n캡처 완료: ${files.length}개 → ${outDir}`);
})();
