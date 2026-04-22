# Step 5: Assignment & Grade

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md` — 과제_정의/과제_현황 스키마, 데이터 흐름 2(과제 체크), 데이터 흐름 3(학점 계산)
- `/docs/PRD.md` — F3(과제 관리), F4(학점 계산), 관련 엣지케이스
- `/docs/ADR.md` — ADR-004(동적 과제 관리)
- `/gas/src/` — step0~4 전체 산출물

이전 step에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업

### 5-1. AssignmentManager.js

과제 정의 CRUD + 과제 현황 체크 모듈.

```javascript
// 시그니처
const AssignmentManager = {
  // 과제 정의 CRUD
  listDefs(filters) { ... },         // filters: { category, class_level }
  addDef(data) { ... },              // 과제 정의 추가
  updateDef(defId, data) { ... },    // 과제 정의 수정
  deleteDef(defId) { ... },          // soft delete

  // 과제 현황
  getStudentAssignments(studentId) { ... },  // 특정 수강생의 과제 현황 목록
  check(studentId, assignmentId, status) { ... },  // 과제 완료/미완료 체크
  bulkCheck(assignmentId, studentIds, status) { ... },  // 일괄 체크

  // 통계
  getCompletionRate(studentId) { ... }  // weight 기반 가중 완료율 계산
};
```

핵심 규칙:
- 과제 정의 변경 시 기존 현황 데이터는 보존 (orphan 현황은 경고 로그만)
- weight 합이 100%가 아니어도 허용 — 비례 계산
- check() 후 자동으로 수강생_마스터의 assignment_completion_rate 재계산
- CRITICAL: 쓰기 시 LockService 사용
- bulkCheck는 BatchRunner 활용 (다수 수강생 일괄 처리)

### 5-2. GradeCalculator.js

이수 판정 모듈.

```javascript
// 시그니처
const GradeCalculator = {
  calculate(studentId) { ... },
  // 이수 판정 로직:
  // 1. assignment_completion_rate >= PASS_THRESHOLD (기본 80%)
  // 2. AND course_completed == true
  // 3. AND payment_status == true
  // → 모두 충족: Pass
  // → payment 미확인: '진행중' (입금 확인 대기)
  // → course_completed false: '진행중'
  // → completion_rate < threshold: Fail (과정 종료 후) 또는 '진행중' (과정 중)
  // 반환: { grade, reason }

  calcAll(filters) { ... },
  // 필터 조건에 맞는 전체 수강생 학점 일괄 계산
  // BatchRunner 활용

  getPassThreshold() { ... }
  // _config에서 PASS_THRESHOLD 조회
};
```

핵심 규칙:
- 학점 계산은 비파괴적 — 이전 grade를 덮어쓰되 변경 이력은 _log에 기록
- calcAll은 BatchRunner 사용 (대량 수강생)
- 계산 후 관련 캐시 무효화

### 5-3. Router.js 라우트 추가

step4에서 stub으로 남긴 라우트를 연결:
- getAssignments → AssignmentManager.listDefs
- addAssignment → AssignmentManager.addDef (admin)
- updateAssignment → AssignmentManager.updateDef (admin)
- checkAssignment → AssignmentManager.check (admin)
- calculateGrades → GradeCalculator.calcAll (admin)

### 5-4. Jest 테스트 작성

`test/GradeCalculator.test.js`:
- Pass 조건 충족 (rate >= 80, completed, paid)
- Fail (rate < 80, 과정 종료)
- 진행중 (rate >= 80 but not completed)
- 진행중 (completed but not paid)
- 경계값 (rate = 80 정확히)
- PASS_THRESHOLD 변경 시 동작

## Acceptance Criteria

```bash
cd gas && npm test 2>&1 | tail -10   # GradeCalculator 포함 전체 테스트 PASS
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

- 과제 완료율을 단순 개수 비율로 계산하지 마라. 이유: weight(배점 비중)에 따른 가중 평균 사용.
- 학점을 자동으로 Fail로 변경하지 마라 (과정 진행 중일 때). 이유: 아직 과제 제출 기회가 남아있을 수 있음. '진행중' 유지.
- GradeCalculator에서 직접 시트에 쓰지 마라. 이유: StudentManager.update()를 통해 쓰기. 단일 쓰기 경로 유지.
