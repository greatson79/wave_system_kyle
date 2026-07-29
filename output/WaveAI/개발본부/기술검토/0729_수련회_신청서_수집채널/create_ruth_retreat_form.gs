/**
 * 디딤교회 2026 여름수련회 Google Form을 현재 로그인한 계정 소유로 생성합니다.
 * script.google.com에서 새 프로젝트를 만든 뒤 이 파일 전체를 붙여넣고
 * createRuthRetreatForm을 한 번 실행하십시오.
 */
function createRuthRetreatForm() {
  const lock = LockService.getUserLock();
  if (!lock.tryLock(30000)) {
    throw new Error("다른 생성 작업이 진행 중입니다. 잠시 후 다시 실행하십시오.");
  }

  try {
    const properties = PropertiesService.getUserProperties();
    const existingFormId = properties.getProperty("RUTH_RETREAT_FORM_ID");
    const existingSheetId = properties.getProperty("RUTH_RETREAT_SHEET_ID");
    const status = properties.getProperty("RUTH_RETREAT_STATUS");

    if (existingFormId && status === "COMPLETE") {
      const existingForm = FormApp.openById(existingFormId);
      const existingSheet = SpreadsheetApp.openById(existingSheetId);
      return logResult_(existingForm, existingSheet);
    }

    if (existingFormId && status === "BUILDING") {
      const partialForm = FormApp.openById(existingFormId);
      throw new Error(
        "이전 실행이 중간에 멈췄습니다. 중복 생성을 막았습니다. 부분 Form: " +
          partialForm.getEditUrl(),
      );
    }

    const title =
      "디딤교회 2026 여름수련회 · 룻기\n「가장 어두운 시대, 가장 조용한 은혜」";
    const description = [
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
    ].join("\n");

    const form = FormApp.create(title, false);
    properties.setProperties({
      RUTH_RETREAT_FORM_ID: form.getId(),
      RUTH_RETREAT_STATUS: "BUILDING",
    });

    form
      .setDescription(description)
      .setCollectEmail(false)
      .setLimitOneResponsePerUser(false)
      .setAllowResponseEdits(false)
      .setPublishingSummary(false)
      .setShowLinkToRespondAgain(false)
      .setShuffleQuestions(false)
      .setProgressBar(true)
      .setConfirmationMessage("신청이 접수되었습니다.");

    form.addTextItem().setTitle("1. 성함").setRequired(true);

    form
      .addParagraphTextItem()
      .setTitle("2. 함께 오시는 가족 (해당되시면)")
      .setHelpText("이름 / 나이(또는 학년)")
      .setRequired(false);

    form
      .addCheckboxItem()
      .setTitle("3. 참여하실 일정  (오실 수 있는 날에 표시해 주세요)")
      .setChoiceValues([
        "8월 2일(주일) — 룻기 1~3장",
        "8월 9일(주일) — 룻기 4장 + 특강 「이미와 아직」",
        "아직 잘 모르겠습니다 (그래도 편하게 표시해 주세요)",
      ])
      .setRequired(false);

    form
      .addParagraphTextItem()
      .setTitle("4. 이번 수련회에서 기대하시는 것, 바라시는 점")
      .setHelpText("(한 줄이어도 좋고, 비워두셔도 괜찮습니다)")
      .setRequired(false);

    form
      .addParagraphTextItem()
      .setTitle("5. 기도제목")
      .setHelpText("적어 주신 기도제목은 담임목사만 봅니다.")
      .setRequired(false);

    form
      .addCheckboxItem()
      .setTitle("선택")
      .setChoiceValues([
        "수련회 중 함께 기도할 수 있도록 나누어도 좋습니다 (원하시는 경우에만 표시)",
      ])
      .setRequired(false);

    form.addTextItem().setTitle("6. 연락처").setRequired(true);

    const minorGate = form
      .addMultipleChoiceItem()
      .setTitle("미성년 자녀가 참여합니까?")
      .setRequired(true);

    const minorPage = form
      .addPageBreakItem()
      .setTitle("미성년 자녀가 참여하는 경우에만");

    form.addTextItem().setTitle("7. 보호자 성함").setRequired(true);
    form.addTextItem().setTitle("참가자와의 관계").setRequired(true);

    form
      .addTextItem()
      .setTitle("8. 비상 연락처")
      .setHelpText("(행사 중 연결 가능한 번호)")
      .setRequired(true);

    form
      .addParagraphTextItem()
      .setTitle("9. 건강 특이사항 (알레르기·복약·기저질환)")
      .setHelpText('해당 없으면 "없음"')
      .setRequired(true);

    form
      .addMultipleChoiceItem()
      .setTitle("10. 귀가 방법")
      .setChoiceValues(["보호자 동반", "본인 귀가(중등부 이상)"])
      .showOtherOption(true)
      .setRequired(true);

    form
      .addCheckboxItem()
      .setTitle("11.")
      .setChoiceValues([
        "행사 중 응급상황 시 인솔자 판단하에 응급처치 및 병원 이송에 동의합니다",
      ])
      .setRequired(true);

    const under14Gate = form
      .addMultipleChoiceItem()
      .setTitle("참가자 중 만 14세 미만이 있습니까?")
      .setRequired(true);

    const adultConsentPage = form
      .addPageBreakItem()
      .setTitle("개인정보 동의 및 마무리");
    addGeneralConsent_(form);
    addClosing_(form);

    const minorConsentPage = form
      .addPageBreakItem()
      .setTitle("미성년 개인정보 동의 및 마무리");
    addGeneralConsent_(form);
    addHealthConsent_(form);
    addClosing_(form);

    const under14ConsentPage = form
      .addPageBreakItem()
      .setTitle("만 14세 미만 개인정보 동의 및 마무리");
    addGeneralConsent_(form);
    addHealthConsent_(form);
    addGuardianConsent_(form);
    addClosing_(form);

    minorGate.setChoices([
      minorGate.createChoice("예", minorPage),
      minorGate.createChoice("아니요", adultConsentPage),
    ]);
    under14Gate.setChoices([
      under14Gate.createChoice("예", under14ConsentPage),
      under14Gate.createChoice("아니요", minorConsentPage),
    ]);

    // PageBreakItem의 이동 설정은 그 page break 바로 앞 페이지에 적용됩니다.
    // adultConsentPage 뒤에는 minorConsentPage가 있으므로 여기서 제출시킵니다.
    minorConsentPage.setGoToPage(FormApp.PageNavigationType.SUBMIT);
    // minorConsentPage 뒤에는 under14ConsentPage가 있으므로 여기서 제출시킵니다.
    under14ConsentPage.setGoToPage(FormApp.PageNavigationType.SUBMIT);

    const responseSheet = SpreadsheetApp.create(
      "디딤교회 2026 여름수련회 · 룻기 — 응답",
    );
    properties.setProperties({
      RUTH_RETREAT_SHEET_ID: responseSheet.getId(),
    });
    form.setDestination(
      FormApp.DestinationType.SPREADSHEET,
      responseSheet.getId(),
    );

    form.setPublished(true).setAcceptingResponses(true);

    properties.setProperties({
      RUTH_RETREAT_STATUS: "COMPLETE",
    });

    return logResult_(form, responseSheet);
  } finally {
    lock.releaseLock();
  }
}

function addGeneralConsent_(form) {
  form
    .addCheckboxItem()
    .setTitle("12. 개인정보 수집·이용 동의")
    .setHelpText(
      "수집 목적: 수련회 준비 및 비상연락 / 보유 기간: 수련회 종료 후 1개월 내 폐기",
    )
    .setChoiceValues(["(필수) 위 정보의 수집·이용에 동의합니다"])
    .setRequired(true);
}

function addHealthConsent_(form) {
  form
    .addCheckboxItem()
    .setTitle(
      "건강 특이사항(알레르기·복약·기저질환) 수집·이용 동의",
    )
    .setHelpText(
      "— 응급 상황 대응 목적으로만 사용하며, 수련회 종료 후 1개월 내 폐기합니다",
    )
    .setChoiceValues([
      "(필수 · 민감정보 별도 동의) 건강 특이사항(알레르기·복약·기저질환) 수집·이용에 동의합니다",
    ])
    .setRequired(true);
}

function addGuardianConsent_(form) {
  form
    .addCheckboxItem()
    .setTitle("만 14세 미만 법정대리인 확인")
    .setChoiceValues([
      "(참가자가 만 14세 미만인 경우) 법정대리인이 위 내용을 확인하고 동의합니다",
    ])
    .setRequired(true);

  form
    .addTextItem()
    .setTitle("법정대리인 성명 ______________________ (서명)")
    .setRequired(true);
}

function addClosing_(form) {
  form
    .addSectionHeaderItem()
    .setTitle("안내")
    .setHelpText(
      [
        "준비물은 성경 한 권이면 충분합니다.",
        "",
        "신청은 7월 31일(금) 밤까지 받습니다.",
        "그 뒤에 마음이 정해지셔도 그냥 오시면 됩니다.",
      ].join("\n"),
    );
}

function logResult_(form, responseSheet) {
  const result = {
    editUrl: form.getEditUrl(),
    responderUrl: form.getPublishedUrl(),
    responseSheetUrl: responseSheet.getUrl(),
  };

  Logger.log("FORM_EDIT_URL=%s", result.editUrl);
  Logger.log("FORM_RESPONDER_URL=%s", result.responderUrl);
  Logger.log("RESPONSE_SHEET_URL=%s", result.responseSheetUrl);
  return result;
}
