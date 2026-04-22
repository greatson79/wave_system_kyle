# Step 3: Scanners & Parsers

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 데이터 흐름 1(스캔), ColumnMapper 매핑, _scan_history 스키마
- `/docs/ADR.md` — ADR-005(파일명 패턴 6종 A-F), ADR-006(헤더 매핑), ADR-013(기수=월), ADR-014(불린 정규화)
- `/gas/src/utils/` — Constants.js, ErrorHandler.js, ColumnMapper.js, ResponseNormalizer.js, BatchRunner.js
- `/gas/src/Auth.js`, `/gas/src/Setup.js`

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 3-1. FileNameParser.js

ADR-005의 6가지 파일명 패턴(A-F)을 파싱하는 모듈.

```javascript
// 시그니처
const FileNameParser = {
  parse(fileName) { ... }
  // 반환: { month, category, target, classLevels: [], region, raw: fileName }
  // 파싱 실패 시: { raw: fileName, parseError: true }
};
```

패턴 상세 (실제 Google Drive 파일명 기반):
- **A**: `(4월 목회자 통합신청서)(응답)` → month=4, target=목회자
- **B**: `(4월 일반 Class #1 & 3통합신청서)(응답)` → month=4, target=일반, classLevels=[1,3]
- **C**: `(3월 교회강의 목회자 Class#1 수강신청)(응답)` → month=3, category=교회강의, target=목회자, classLevels=[1]
- **D**: `(3월 교회강의 일반 Class #1 수강신청)(응답)` → month=3, category=교회강의, target=일반, classLevels=[1]
- **E**: `(4월 꿈별 교회강의 신청서)(응답)` → month=4, region=꿈별, category=교회강의
- **F**: `(4월 부산 교회강의 Class#1 수강신청서)(응답)` → month=4, region=부산, category=교회강의, classLevels=[1]

핵심 규칙:
- Class 번호 앞의 `#`과 공백은 있을 수도 없을 수도 있음 (Class#1, Class #1, Class #1 모두 허용)
- `&` 구분으로 멀티 클래스 지원 (예: Class #1 & 3 → [1, 3])
- 파싱 실패 시 MEDIUM 에러 로그 + parseError: true 반환 (전체 중단하지 않음)
- month를 CURRENT_COHORT 연도와 합쳐 cohort 생성 (예: month=3 → "2026-03")

### 3-2. DriveScanner.js

Google Drive 폴더를 스캔하여 응답 스프레드시트 목록을 반환하는 모듈.

```javascript
// 시그니처
const DriveScanner = {
  scan() { ... },
  // _config의 SCAN_FOLDER_IDS에 등록된 폴더들 + 루트 드라이브 스캔
  // 반환: [{ fileId, fileName, folderId, folderName, parsed: FileNameParser.parse(fileName) }]

  scanFolder(folderId) { ... },
  // 단일 폴더 스캔

  getNewFiles(scannedFiles) { ... },
  // _scan_history와 대조하여 신규/변경 파일만 필터링

  recordScanHistory(result) { ... }
  // _scan_history에 스캔 결과 기록
};
```

핵심 규칙:
- CRITICAL: 원본 .gsheet 파일은 읽기 전용. SpreadsheetApp.openById()로 데이터만 읽음.
- MimeType.GOOGLE_SHEETS로 필터링
- 파일명에 "(응답)" 포함된 것만 대상
- BatchRunner를 사용하여 4.5분 타임아웃 대응
- 개별 파일 스캔 실패 시 스킵 + MEDIUM 에러 로그 (전체 중단 금지)

### 3-3. SheetReader.js

스프레드시트에서 데이터를 읽고 ColumnMapper + ResponseNormalizer를 적용하는 모듈.

```javascript
// 시그니처
const SheetReader = {
  readSheet(fileId) { ... },
  // 반환: { headers: [], rows: [{ fieldName: value }], metadata: { fileId, fileName, sheetName } }

  readAndNormalize(fileId, parsedFileName) { ... }
  // readSheet + ColumnMapper + ResponseNormalizer + 파일명 메타데이터 병합
  // 반환: [{ ...normalizedRow, category, class_level, target, region, cohort, source_file, source_sheet_id }]
};
```

핵심 규칙:
- 첫 번째 시트(index 0)만 읽음 (Google Forms 응답은 항상 첫 시트)
- 빈 행 스킵 (이메일이 비어있으면 스킵)
- ColumnMapper 매핑 실패 시 해당 파일 전체 스킵 + HIGH 에러
- 파일명에서 파싱된 category/class_level/target/region을 각 행에 병합
- 멀티 클래스 파일(예: Class #1 & 3)의 경우, 행 내 "희망 클래스" 컬럼 값 우선 사용

### 3-4. Jest 테스트 작성

`test/FileNameParser.test.js`에 6개 패턴 A-F 각각에 대한 테스트를 작성하라:
- 각 패턴 정상 파싱
- Class 번호 변형 (Class#1, Class #1, Class #1)
- 멀티 클래스 (Class #1 & 3)
- 파싱 실패 (패턴 불일치 파일명)
- 빈 문자열, null 입력

## Acceptance Criteria

```bash
cd gas && npm test 2>&1 | tail -10   # FileNameParser 포함 전체 테스트 PASS
cd gas && clasp push --force 2>&1 | tail -5   # 배포 에러 없음
```

## 검증 절차

1. 위 AC 커맨드를 실행한다.
2. 아키텍처 체크리스트를 확인한다:
   - ARCHITECTURE.md 디렉토리 구조를 따르는가?
   - ADR 기술 스택을 벗어나지 않았는가?
   - CLAUDE.md CRITICAL 규칙을 위반하지 않았는가?
3. 결과에 따라 `phases/0-mvp/index.json`의 해당 step을 업데이트한다:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄 요약"`
   - 수정 3회 시도 후에도 실패 → `"status": "error"`, `"error_message": "구체적 에러 내용"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason": "구체적 사유"` 후 즉시 중단

## 금지사항

- 원본 .gsheet 파일에 쓰기 작업을 하지 마라. 이유: CLAUDE.md CRITICAL 규칙 위반.
- DriveScanner에서 하위 폴더를 재귀 탐색하지 마라. 이유: 6분 제한 초과 위험. 등록된 폴더만 1단계 스캔.
- FileNameParser에서 정규식을 하나의 거대한 패턴으로 만들지 마라. 이유: 유지보수 불가. 패턴별 개별 매칭 후 합성.
