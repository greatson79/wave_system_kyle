# 아키텍처: Wave Academy 수강관리 시스템 (Python)

## 기술 스택

| 레이어 | 기술 | 비고 |
|--------|------|------|
| 런타임 | Python 3.12+ | 로컬 CLI 실행 |
| Google Drive 연동 | google-api-python-client | OAuth2 인증, 파일 다운로드 |
| Excel 읽기/쓰기 | openpyxl | .xlsx 파일 처리 |
| 데이터 처리 | pandas | 정리·분석·필터링 |
| 테스트 | pytest | 단위 + 통합 |
| 결과물 | .xlsx 마스터 스프레드시트 | Google Drive에 업로드 |

## 디렉토리 구조

```
src/
├── main.py                 # CLI 진입점
├── config.py               # 설정 (폴더 ID, 분류 체계 등)
├── drive/
│   ├── client.py           # Google Drive API 클라이언트 (인증, 다운로드, 업로드)
│   └── scanner.py          # wave_수강신청 폴더 스캔, 파일 목록 반환
├── parsers/
│   ├── filename_parser.py  # 파일명 패턴 파싱 (6 패턴 A-F)
│   ├── column_mapper.py    # 헤더 텍스트 기반 컬럼 매핑
│   └── normalizer.py       # 불린/공백/전화번호 정규화
├── processors/
│   ├── student_processor.py    # 수강생 데이터 통합 (중복 제거, upsert)
│   ├── assignment_manager.py   # 과제 정의/현황 관리
│   └── grade_calculator.py     # 학점/이수 계산 (Pass/Fail/진행중)
├── exporters/
│   └── excel_exporter.py   # 마스터 스프레드시트 생성 (.xlsx)
└── utils/
    ├── error_handler.py    # 에러 분류/로깅
    └── constants.py        # 상수 정의
tests/
├── test_filename_parser.py
├── test_column_mapper.py
├── test_normalizer.py
├── test_grade_calculator.py
└── test_student_processor.py
credentials/
└── .gitignore              # OAuth credentials here (gitignored)
requirements.txt
pyproject.toml
```

## 데이터 모델

### 수강생 마스터 (DataFrame / Excel 시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | str | ✅ | UUID |
| timestamp | datetime | ✅ | 원본 폼 제출 시각 |
| email | str | ✅ | 이메일 |
| name | str | ✅ | 성함 |
| phone | str | ✅ | 연락처 |
| church | str | ✅ | 교회/기관명 |
| position | str | ⬜ | 직분 |
| category | str | ✅ | 교회강의/Wave Academy/자격증과정/외부강의 |
| class_level | str | ✅ | Class #1/2/3 |
| target | str | ✅ | 목회자/일반 |
| region | str | ⬜ | 부산/충남/꿈별 등 |
| cohort | str | ✅ | 기수 (2026-04) |
| payment_status | bool | ✅ | 입금 여부 |
| course_completed | bool | ✅ | 수강완료 여부 |
| grade | str | ✅ | Pass/Fail/진행중 |
| assignment_completion_rate | float | ✅ | 과제 완료율 (0~100) |
| source_file | str | ✅ | 원본 파일명 |
| is_active | bool | ✅ | 활성 여부 |
| created_at | datetime | ✅ | 생성 시각 |
| updated_at | datetime | ✅ | 수정 시각 |

### 과제 정의 (Excel 시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | str | ✅ | 과제 ID |
| category | str | ✅ | 카테고리 |
| class_level | str | ✅ | 대상 클래스 |
| week | int | ✅ | 주차 |
| title | str | ✅ | 과제 제목 |
| weight | float | ✅ | 배점 비중 (%) |
| is_active | bool | ✅ | 활성 여부 |

### 과제 현황 (Excel 시트)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| student_id | str | ✅ | 수강생 ID (FK) |
| assignment_id | str | ✅ | 과제 ID (FK) |
| status | str | ✅ | 완료/미완료/지각 |
| submitted_at | datetime | ⬜ | 제출 시각 |

## 데이터 흐름

### 전체 파이프라인

```
[Google Drive: wave_수강신청/ 폴더]
    │ Drive API로 파일 목록 조회
    ▼
[scanner.py: .xlsx/.gsheet 파일 다운로드]
    │ 로컬 temp 디렉토리에 저장
    ▼
[filename_parser.py: 파일명 파싱]
    │ category, class_level, target, region 추출
    ▼
[openpyxl: 시트 데이터 읽기]
    │ 헤더 + 행 데이터
    ▼
[column_mapper.py: 헤더→필드 매핑]
    │ 정규화된 딕셔너리 리스트
    ▼
[normalizer.py: 불린/공백 정규화]
    │ 클린 데이터
    ▼
[student_processor.py: 중복 제거 + 통합]
    │ email+class_level+cohort 기준 upsert
    ▼
[grade_calculator.py: 학점 계산]
    │ Pass/Fail/진행중
    ▼
[excel_exporter.py: 마스터 .xlsx 생성]
    │ 수강생_마스터 + 과제_정의 + 과제_현황 시트
    ▼
[Google Drive: Wave/행정/수강관리/ 에 업로드]
```

## ColumnMapper 필드 매핑

원본 폼마다 헤더 텍스트가 다를 수 있으므로 키워드 기반 매핑을 사용한다.

| 필드명 | 매칭 키워드 (contains, case-insensitive) |
|--------|----------------------------------------|
| timestamp | 타임스탬프, timestamp |
| email | 이메일, email |
| name | 성함, 이름, name |
| phone | 연락처, 전화, phone |
| church | 교회, 기관, church |
| position | 직분, position |
| class_level | 클래스, class, 희망 |
| payment_status | 입금여부, payment |
| payment_name | 입금자, payer |
| privacy_agreed | 개인정보, privacy |

**매칭 우선순위:** 정확 일치 > contains 일치 > 첫 번째 매칭
**매칭 실패 시:** 해당 필드 None + 로그 기록 (경고, 에러 아님)

## Boolean 정규화

| 입력값 | 결과 |
|--------|------|
| "예", "네", "Yes", "Y", "TRUE", "1", "O", "확인" | True |
| "아니오", "아니요", "No", "N", "FALSE", "0", "X" | False |
| "", None, NaN | False |

## 에러 처리

| 심각도 | 처리 | 예시 |
|--------|------|------|
| CRITICAL | 즉시 중단 + 로그 | Drive API 인증 실패 |
| HIGH | 해당 작업 중단 + 로그 | 파일 읽기 실패 |
| MEDIUM | 항목 스킵 + 경고 | 파일명 파싱 실패, 컬럼 매핑 불일치 |
| LOW | 로그만 | 선택 필드 누락 |

**핵심 원칙:** 개별 파일/항목 실패가 전체 프로세스를 중단시키면 안 된다. HIGH 이하 에러는 해당 항목만 스킵하고 나머지를 계속 처리한다.

## Google Drive API 인증

- OAuth2 Client ID (Desktop application)
- `credentials.json` → 최초 실행 시 브라우저 인증 → `token.json` 저장
- Scopes: `drive.readonly` (읽기), `drive.file` (결과 업로드)
