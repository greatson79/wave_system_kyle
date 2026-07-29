import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const scriptPath = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "create_ruth_retreat_form.gs",
);

assert.ok(fs.existsSync(scriptPath), "Apps Script 파일이 있어야 한다");

const createdForms = [];
const createdSheets = [];
const userProperties = new Map();

class FakeItem {
  constructor(type) {
    this.type = type;
    this.title = "";
    this.helpText = "";
    this.required = false;
    this.choices = [];
    this.other = false;
    this.navigation = null;
  }
  setTitle(value) { this.title = value; return this; }
  setHelpText(value) { this.helpText = value; return this; }
  setRequired(value) { this.required = value; return this; }
  setChoiceValues(values) { this.choices = Array.from(values, (value) => ({ value })); return this; }
  showOtherOption(value) { this.other = value; return this; }
  createChoice(value, destination) { return { value, destination }; }
  setChoices(values) { this.choices = Array.from(values); return this; }
  setGoToPage(value) { this.navigation = value; return this; }
}

class FakeForm {
  constructor(title, published) {
    this.id = `form-${createdForms.length + 1}`;
    this.title = title;
    this.published = published;
    this.items = [];
    this.settings = {};
    this.destination = null;
  }
  setDescription(value) { this.description = value; return this; }
  setCollectEmail(value) { this.settings.collectEmail = value; return this; }
  setLimitOneResponsePerUser(value) { this.settings.limitOne = value; return this; }
  setAllowResponseEdits(value) { this.settings.allowEdits = value; return this; }
  setPublishingSummary(value) { this.settings.publishSummary = value; return this; }
  setShowLinkToRespondAgain(value) { this.settings.respondAgain = value; return this; }
  setShuffleQuestions(value) { this.settings.shuffle = value; return this; }
  setProgressBar(value) { this.settings.progress = value; return this; }
  setConfirmationMessage(value) { this.settings.confirmation = value; return this; }
  setDestination(type, id) { this.destination = { type, id }; return this; }
  setPublished(value) { this.published = value; return this; }
  setAcceptingResponses(value) { this.settings.accepting = value; return this; }
  addTextItem() { return this._add("text"); }
  addParagraphTextItem() { return this._add("paragraph"); }
  addCheckboxItem() { return this._add("checkbox"); }
  addMultipleChoiceItem() { return this._add("multipleChoice"); }
  addPageBreakItem() { return this._add("pageBreak"); }
  addSectionHeaderItem() { return this._add("sectionHeader"); }
  _add(type) { const item = new FakeItem(type); this.items.push(item); return item; }
  getId() { return this.id; }
  getEditUrl() { return `https://forms.example/${this.id}/edit`; }
  getPublishedUrl() { return `https://forms.example/${this.id}/view`; }
}

const FormApp = {
  DestinationType: { SPREADSHEET: "SPREADSHEET" },
  PageNavigationType: { SUBMIT: "SUBMIT" },
  create(title, published) {
    const form = new FakeForm(title, published);
    createdForms.push(form);
    return form;
  },
  openById(id) {
    const form = createdForms.find((candidate) => candidate.id === id);
    if (!form) throw new Error("missing form");
    return form;
  },
};

const SpreadsheetApp = {
  create(title) {
    const sheet = {
      id: `sheet-${createdSheets.length + 1}`,
      title,
      getId() { return this.id; },
      getUrl() { return `https://sheets.example/${this.id}`; },
    };
    createdSheets.push(sheet);
    return sheet;
  },
  openById(id) {
    const sheet = createdSheets.find((candidate) => candidate.id === id);
    if (!sheet) throw new Error("missing sheet");
    return sheet;
  },
};

const PropertiesService = {
  getUserProperties() {
    return {
      getProperty(key) { return userProperties.get(key) ?? null; },
      setProperties(values) {
        Object.entries(values).forEach(([key, value]) => userProperties.set(key, value));
      },
      deleteAllProperties() { userProperties.clear(); },
    };
  },
};

let lockHeld = false;
const LockService = {
  getUserLock() {
    return {
      tryLock() {
        if (lockHeld) return false;
        lockHeld = true;
        return true;
      },
      releaseLock() { lockHeld = false; },
    };
  },
};

const Logger = { log() {} };
const context = { FormApp, SpreadsheetApp, PropertiesService, LockService, Logger };
vm.createContext(context);
vm.runInContext(fs.readFileSync(scriptPath, "utf8"), context, { filename: scriptPath });

assert.equal(typeof context.createRuthRetreatForm, "function");
const result = context.createRuthRetreatForm();
assert.equal(createdForms.length, 1);
assert.equal(createdSheets.length, 1);

const form = createdForms[0];
assert.equal(form.published, true);
assert.equal(
  form.title,
  "디딤교회 2026 여름수련회 · 룻기\n「가장 어두운 시대, 가장 조용한 은혜」",
);
assert.equal(
  form.description,
  [
    "8월 2일(주일) · 8월 9일(주일) 오후 2시 ~ 6시 · 교회 강당",
    "",
    "이번 수련회는 온 교우가 함께하는 전교인 수련회입니다.",
    "아이부터 어른까지 한자리에서 같은 말씀을 나눕니다.",
    "",
    "두 번의 주일 오후가 하나로 이어지는 흐름이라,",
    "가능하시면 두 주 모두 함께하시기를 권해 드립니다.",
    "",
    "다만 사정이 있어 한 주만 오셔도 좋습니다.",
    "신청하지 않고 오셔도 자리는 늘 준비되어 있습니다.",
    "이 신청서는 자리를 제한하려는 것이 아니라,",
    "자료와 자리를 넉넉히 준비하려고 여쭙는 것입니다.",
    "",
    "── 텅 빈 채로 오셔도 됩니다. 먼저 채워서 올 필요는 없습니다.",
  ].join("\n"),
);
assert.deepEqual(form.settings, {
  collectEmail: false,
  limitOne: false,
  allowEdits: false,
  publishSummary: false,
  respondAgain: false,
  shuffle: false,
  progress: true,
  confirmation: "신청이 접수되었습니다.",
  accepting: true,
});
assert.deepEqual(form.destination, { type: "SPREADSHEET", id: "sheet-1" });

const byTitle = (title) => form.items.filter((item) => item.title === title);
assert.equal(byTitle("1. 성함")[0].required, true);
assert.equal(byTitle("2. 함께 오시는 가족 (해당되시면)")[0].required, false);
assert.equal(byTitle("3. 참여하실 일정  (오실 수 있는 날에 표시해 주세요)")[0].required, false);
assert.deepEqual(
  byTitle("3. 참여하실 일정  (오실 수 있는 날에 표시해 주세요)")[0].choices.map((choice) => choice.value),
  [
    "8월 2일(주일) — 룻기 1~3장",
    "8월 9일(주일) — 룻기 4장 + 특강 「이미와 아직」",
    "아직 잘 모르겠습니다 (그래도 편하게 표시해 주세요)",
  ],
);
assert.equal(byTitle("5. 기도제목")[0].helpText, "적어 주신 기도제목은 담임목사만 봅니다.");
assert.equal(byTitle("선택")[0].required, false);
assert.deepEqual(
  byTitle("선택")[0].choices.map((choice) => choice.value),
  ["수련회 중 함께 기도할 수 있도록 나누어도 좋습니다 (원하시는 경우에만 표시)"],
);
assert.equal(byTitle("6. 연락처")[0].required, true);
assert.equal(byTitle("7. 보호자 성함")[0].required, true);
assert.equal(byTitle("참가자와의 관계")[0].required, true);
assert.equal(byTitle("9. 건강 특이사항 (알레르기·복약·기저질환)")[0].required, true);
assert.deepEqual(
  byTitle("10. 귀가 방법")[0].choices.map((choice) => choice.value),
  ["보호자 동반", "본인 귀가(중등부 이상)"],
);
assert.equal(byTitle("10. 귀가 방법")[0].other, true);
assert.deepEqual(
  byTitle("11.")[0].choices.map((choice) => choice.value),
  ["행사 중 응급상황 시 인솔자 판단하에 응급처치 및 병원 이송에 동의합니다"],
);

const minorGate = byTitle("미성년 자녀가 참여합니까?")[0];
const under14Gate = byTitle("참가자 중 만 14세 미만이 있습니까?")[0];
assert.deepEqual(minorGate.choices.map((choice) => choice.value), ["예", "아니요"]);
assert.deepEqual(under14Gate.choices.map((choice) => choice.value), ["예", "아니요"]);

const minorPage = byTitle("미성년 자녀가 참여하는 경우에만")[0];
const adultConsentPage = byTitle("개인정보 동의 및 마무리")[0];
const minorConsentPage = byTitle("미성년 개인정보 동의 및 마무리")[0];
const under14ConsentPage = byTitle("만 14세 미만 개인정보 동의 및 마무리")[0];
assert.equal(minorGate.choices[0].destination, minorPage);
assert.equal(minorGate.choices[1].destination, adultConsentPage);
assert.equal(under14Gate.choices[0].destination, under14ConsentPage);
assert.equal(under14Gate.choices[1].destination, minorConsentPage);
assert.equal(minorConsentPage.navigation, "SUBMIT");
assert.equal(under14ConsentPage.navigation, "SUBMIT");

const generalConsents = byTitle("12. 개인정보 수집·이용 동의");
const healthConsents = byTitle("건강 특이사항(알레르기·복약·기저질환) 수집·이용 동의");
const guardianConsents = byTitle("만 14세 미만 법정대리인 확인");
assert.equal(generalConsents.length, 3);
assert.ok(generalConsents.every((item) => item.required));
assert.equal(healthConsents.length, 2);
assert.ok(healthConsents.every((item) => item.required));
assert.equal(guardianConsents.length, 1);
assert.ok(guardianConsents.every((item) => item.required));
assert.equal(byTitle("법정대리인 성명 ______________________ (서명)")[0].required, true);
assert.equal(
  byTitle("안내")[0].helpText,
  [
    "준비물은 성경 한 권이면 충분합니다.",
    "",
    "신청은 7월 31일(금) 밤까지 받습니다.",
    "그 뒤에 마음이 정해지셔도 그냥 오시면 됩니다.",
  ].join("\n"),
);

assert.equal(result.editUrl, "https://forms.example/form-1/edit");
assert.equal(result.responderUrl, "https://forms.example/form-1/view");
assert.equal(result.responseSheetUrl, "https://sheets.example/sheet-1");

const secondResult = context.createRuthRetreatForm();
assert.equal(createdForms.length, 1, "재실행은 중복 Form을 만들면 안 된다");
assert.equal(createdSheets.length, 1, "재실행은 중복 Sheet를 만들면 안 된다");
assert.deepEqual(secondResult, result);

console.log("PASS: Form schema, privacy settings, branching, idempotency");
