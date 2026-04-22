#!/usr/bin/env node
/**
 * 디딤수요기도회 기도제목 HTML → PNG 캡처
 * Puppeteer를 사용하여 HTML을 PNG로 캡처한다.
 *
 * Usage: node capture_png.js <input.html> <output.png> [--format card] [--high-res]
 *   --format card  : 4:5 카드뉴스 사이즈 (1080×1350px)
 *   --high-res     : A4 고해상도 (2x, a4 형식에서만 적용)
 */

const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const os = require('os');

/** ~/.cache/puppeteer/chrome/ 에서 최신 Chrome 실행 파일 경로를 찾는다. */
function findChromePath() {
    const cacheDir = path.join(os.homedir(), '.cache', 'puppeteer', 'chrome');
    if (!fs.existsSync(cacheDir)) return null;

    const platform = process.platform === 'darwin'
        ? (process.arch === 'arm64' ? 'mac_arm' : 'mac')
        : process.platform === 'win32' ? 'win64' : 'linux';

    const entries = fs.readdirSync(cacheDir)
        .filter(d => d.startsWith(platform))
        .sort()
        .reverse(); // 최신 버전 우선

    for (const entry of entries) {
        const base = path.join(cacheDir, entry);
        // macOS
        const macApp = path.join(base, 'chrome-mac-arm64', 'Google Chrome for Testing.app', 'Contents', 'MacOS', 'Google Chrome for Testing');
        if (fs.existsSync(macApp)) return macApp;
        const macApp2 = path.join(base, 'chrome-mac-x64', 'Google Chrome for Testing.app', 'Contents', 'MacOS', 'Google Chrome for Testing');
        if (fs.existsSync(macApp2)) return macApp2;
        // Linux
        const linux = path.join(base, 'chrome-linux64', 'chrome');
        if (fs.existsSync(linux)) return linux;
    }
    return null;
}

async function captureHtmlToPng(inputHtml, outputPng, highRes = false, format = 'a4') {
    const htmlPath = path.resolve(inputHtml);
    const pngPath = path.resolve(outputPng);

    if (!fs.existsSync(htmlPath)) {
        console.error(`HTML 파일을 찾을 수 없습니다: ${htmlPath}`);
        process.exit(1);
    }

    // 사이즈 결정
    // A4: 96 DPI 기준 210mm=794px, 297mm=1123px (--high-res 시 2x)
    // card: 4:5 카드뉴스 1080×1350px (이미 고해상도, scale=1)
    let width, height, scale;
    if (format === 'card') {
        width = 1080;
        height = 1350;
        scale = 1;
    } else {
        width = 794;
        height = 1123;
        scale = highRes ? 2 : 1;
    }
    
    const chromePath = findChromePath();
    if (!chromePath) {
        console.error('Chrome 실행 파일을 찾을 수 없습니다. npm install 후 다시 시도하세요.');
        process.exit(1);
    }

    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--font-render-hinting=none',
        ],
    });
    
    try {
        const page = await browser.newPage();
        
        await page.setViewport({
            width: width,
            height: height,
            deviceScaleFactor: scale,
        });
        
        // HTML 파일 로드
        const fileUrl = `file://${htmlPath}`;
        await page.goto(fileUrl, { 
            waitUntil: 'networkidle0',
            timeout: 30000 
        });
        
        // 폰트 로딩 대기
        await page.evaluate(() => document.fonts.ready);
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 스크린샷 캡처
        await page.screenshot({
            path: pngPath,
            type: 'png',
            clip: {
                x: 0,
                y: 0,
                width: width,
                height: height,
            },
        });
        
        console.log(`PNG 캡처 완료: ${pngPath}`);
        console.log(`해상도: ${width * scale} × ${height * scale}px`);
        
    } finally {
        await browser.close();
    }
}

// CLI
const args = process.argv.slice(2);
if (args.length < 2) {
    console.log('Usage: node capture_png.js <input.html> <output.png> [--format card] [--high-res]');
    process.exit(1);
}

const inputHtml = args[0];
const outputPng = args[1];
const highRes = args.includes('--high-res');
const formatIdx = args.indexOf('--format');
const format = formatIdx !== -1 ? args[formatIdx + 1] : 'a4';

captureHtmlToPng(inputHtml, outputPng, highRes, format).catch(err => {
    console.error('캡처 실패:', err.message);
    process.exit(1);
});
