# Architecture Decision Records

## 철학
심플하되 빠짐없이 — Python CLI로 Google Drive의 수강신청 Excel 파일을 읽고, 정리·분석·내보내기까지 한 번에 처리한다.

---

### ADR-001: Python CLI (GAS에서 전환)

**결정**: Google Apps Script 웹앱 대신 Python CLI 스크립트로 구현한다.

**이유**:
- GAS는 Apps Script API 활성화, clasp 설정 등 환경 의존성이 높음
- Python은 openpyxl, pandas 등 데이터 처리에 강력한 생태계 보유
- 로컬 실행으로 배포/호스팅 불필요
- 사용자가 요청한 "심플 구현"에 부합

**트레이드오프**:
- 웹 대시보드 없음 (Excel 마스터 시트가 대시보드 역할)
- 사용자가 직접 스크립트 실행 필요

**대안 검토**:
| 대안 | 탈락 이유 |
|------|----------|
| GAS 웹앱 | Apps Script API 설정 복잡, iframe 제약 |
| Next.js + Vercel | 외부 서버 필요, 과도한 복잡성 |
| Google Sheets Add-on | 심사 필요, 제한적 |

---

### ADR-002: Google Drive API로 파일 접근

**결정**: Google Drive API (Python client)로 wave_수강신청 폴더의 파일을 다운로드한다.

**이유**:
- 구글드라이브에 이미 파일이 존재
- .gsheet 파일도 .xlsx로 export 가능
- OAuth2로 안전한 인증

**트레이드오프**:
- 최초 1회 OAuth 브라우저 인증 필요
- 네트워크 필요

---

### ADR-003: NotebookLM 직접 연동 제외

**결정**: NotebookLM API 직접 연동은 범위 밖. 정제 Excel 생성까지만.

**이유**:
- 구글드라이브와 NotebookLM 계정 상이
- NotebookLM에 공식 REST API 없음
- Claude Code MCP로 별도 브릿지 가능

---

### ADR-004: 동적 과제 관리

**결정**: 과제를 하드코딩하지 않고 마스터 Excel 내 '과제_정의' 시트에서 관리.

**이유**:
- 카테고리/클래스별 과제가 다름
- 학기 중 과제 추가/수정 필요

---

### ADR-005: 파일명 패턴 기반 자동 분류

**결정**: 파일명을 파싱하여 category, class_level, target, region 자동 추출.

**패턴**:
| 패턴 | 예시 | 추출 |
|------|------|------|
| A | (4월 목회자 통합신청서)(응답) | target=목회자 |
| B | (4월 일반 Class #1 & 3통합신청서)(응답) | target=일반, class=[1,3] |
| C | (3월 교회강의 목회자 Class#1 수강신청)(응답) | category=교회강의, target=목회자, class=1 |
| D | (3월 교회강의 일반 Class #1 수강신청)(응답) | category=교회강의, target=일반, class=1 |
| E | (4월 꿈별 교회강의 신청서)(응답) | region=꿈별, category=교회강의 |
| F | (4월 부산 교회강의 Class#1 수강신청서)(응답) | region=부산, category=교회강의, class=1 |

**트레이드오프**:
- 새 패턴 추가 시 파서 업데이트 필요

---

### ADR-006: 헤더 텍스트 기반 컬럼 매핑

**결정**: 컬럼을 인덱스가 아닌 헤더 텍스트 키워드 매칭으로 매핑.

**이유**:
- 폼마다 컬럼 순서가 다름
- 헤더 텍스트에 한글 키워드 포함

---

### ADR-007: Soft Delete 정책

**결정**: 삭제는 is_active=False. 물리적 행 삭제 금지.

**이유**:
- 실수 삭제 복구 가능
- 감사 추적 용이

---

### ADR-008: openpyxl + pandas 조합

**결정**: Excel 읽기/쓰기는 openpyxl, 데이터 처리는 pandas.

**이유**:
- openpyxl: .xlsx 서식/스타일 제어 가능
- pandas: 필터링, 집계, 중복 제거에 강력
- 둘 다 순수 Python, 추가 바이너리 의존성 없음

---

### ADR-009: 기수 = 월 기반 자동 태깅

**결정**: 기수(cohort)를 파일명의 월 정보에서 YYYY-MM 형식으로 자동 추출.

---

### ADR-010: Boolean 입력 정규화

**결정**: 폼 응답의 예/아니오 계열을 통일된 bool로 정규화.

**매핑**: "예","네","Yes","Y","TRUE","1","O","확인" → True / 나머지 → False

---

<!-- ADR은 번호를 매겨 계속 추가합니다. -->
