# Step 4: Student Manager

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 수강생_마스터 스키마 (27 컬럼), Router.js 라우팅 테이블, 접근 제어 매트릭스
- `/docs/ADR.md` — ADR-007(soft delete), ADR-009(LockService), ADR-010(마스킹)
- `/gas/src/utils/` — 모든 유틸 파일
- `/gas/src/Auth.js`, `/gas/src/Setup.js`
- `/gas/src/scanners/`, `/gas/src/parsers/` — step3 산출물

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 4-1. StudentManager.js

수강생 CRUD + 중복 체크 + upsert 모듈.

```javascript
// 시그니처
const StudentManager = {
  list(filters, role) { ... },
  // filters: { category, class_level, target, region, cohort, grade, search, page, limit }
  // role이 viewer면 마스킹 적용
  // 반환: { students: [...], total, page, limit }

  get(studentId, role) { ... },
  // 단일 수강생 조회. role이 viewer면 마스킹.

  add(data) { ... },
  // 수동 추가. UUID 생성, created_at/updated_at 설정, is_active=true

  update(studentId, data) { ... },
  // 수정. updated_at 갱신. is_active=false인 레코드는 수정 불가.

  softDelete(studentId) { ... },
  // is_active = false. 물리적 삭제 금지 (CLAUDE.md CRITICAL).

  upsert(rows) { ... },
  // 스캔 결과 일괄 등록. 중복 기준: email + class_level + cohort.
  // 기존 → updated_at 갱신 + 변경 필드만 업데이트.
  // 신규 → add() 호출.

  search(query, role) { ... },
  // 이름, 이메일, 교회명으로 검색

  _findDuplicate(email, classLevel, cohort) { ... },
  // 내부: 중복 확인

  _applyMasking(student, role) { ... }
  // 내부: viewer 역할 마스킹 적용
};
```

핵심 규칙:
- CRITICAL: 쓰기(add, update, softDelete, upsert) 시 반드시 LockService.getScriptLock() 사용
- CRITICAL: softDelete만 허용. deleteRow() 절대 사용 금지.
- upsert의 중복 기준: email + class_level + cohort 조합
- list()는 CacheHelper 활용 (TTL 5분, 필터 조합을 캐시 키에 포함)
- 쓰기 작업 후 관련 캐시 무효화
- is_active=false인 레코드는 기본적으로 목록에서 제외 (필터 옵션으로 포함 가능)

### 4-2. Router.js 뼈대

ARCHITECTURE.md의 라우팅 테이블을 구현하라. 이 step에서는 student 관련 라우트만 연결.

```javascript
// 시그니처
function route(action, params) { ... }
// action → 핸들러 매핑. Auth.withAuth로 권한 체크 래핑.
// 미등록 action → { error: 'Unknown action', code: 404 }
```

이 step에서 연결할 라우트:
- getStudents → StudentManager.list
- getStudent → StudentManager.get
- addStudent → StudentManager.add (admin)
- updateStudent → StudentManager.update (admin)
- deleteStudent → StudentManager.softDelete (admin)
- searchStudents → StudentManager.search
- getFilterOptions → 카테고리/클래스/대상/지역/기수 목록 반환

나머지 라우트(getDashboard, assignments, scan, export 등)는 stub으로 남겨둬라:
```javascript
// TODO: step5에서 구현
```

### 4-3. 스캔 통합 연결

DriveScanner.scan() 결과를 StudentManager.upsert()로 연결하는 전체 스캔 플로우 함수:

```javascript
function runFullScan() {
  // 1. DriveScanner.scan()
  // 2. 신규 파일 필터링
  // 3. 각 파일 SheetReader.readAndNormalize()
  // 4. StudentManager.upsert()
  // 5. DriveScanner.recordScanHistory()
}
```

이 함수를 Router.js의 `runScan` 액션에 연결하라 (admin only).

## Acceptance Criteria

```bash
cd gas && npm test 2>&1 | tail -10   # 기존 테스트 PASS 유지
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

- 물리적 행 삭제(sheet.deleteRow)를 구현하지 마라. 이유: CLAUDE.md CRITICAL — soft delete만 허용.
- LockService 없이 시트에 쓰지 마라. 이유: 동시성 충돌 위험 (ADR-009).
- upsert에서 기존 레코드의 source_file, source_sheet_id를 덮어쓰지 마라. 이유: 최초 등록 원본 추적 필요.
