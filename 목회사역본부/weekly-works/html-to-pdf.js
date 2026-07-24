const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");

const htmlPath = "/Users/kylechoi/Desktop/Ai_works/목회사역본부/weekly-works/output/4월/1주차/카드뉴스/easter-article.html";
const pdfPath = "/Users/kylechoi/Desktop/Ai_works/목회사역본부/weekly-works/output/4월/1주차/카드뉴스/easter-article.pdf";

(async () => {
  // Read HTML and remove slide images
  let html = fs.readFileSync(htmlPath, "utf-8");
  html = html.replace(/<div class="slide-section">[\s\S]*?<\/div>/g, "");

  const browser = await puppeteer.launch({ headless: "new", args: ["--no-sandbox"] });
  const page = await browser.newPage();

  await page.setContent(html, { waitUntil: "networkidle0", timeout: 30000 });

  await page.pdf({
    path: pdfPath,
    format: "A4",
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
    printBackground: true,
    preferCSSPageSize: false
  });

  await browser.close();

  const stats = fs.statSync(pdfPath);
  console.log(`PDF saved: ${pdfPath}`);
  console.log(`Size: ${(stats.size / 1024).toFixed(0)} KB`);
})();
