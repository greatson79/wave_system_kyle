# Step 0: Project Setup

## 읽어야 할 파일

먼저 아래 파일들을 읽고 프로젝트의 아키텍처와 설계 의도를 파악하라:

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`

## 작업

### 0-1. 기존 GAS 디렉토리 정리

`gas/` 디렉토리가 존재하면 삭제하라 (이전 GAS 접근법의 잔재).

### 0-2. Python 프로젝트 디렉토리 구조 생성

ARCHITECTURE.md의 디렉토리 구조를 따라 생성하라:

```
src/
├── __init__.py
├── main.py
├── config.py
├── drive/
│   ├── __init__.py
│   ├── client.py
│   └── scanner.py
├── parsers/
│   ├── __init__.py
│   ├── filename_parser.py
│   ├── column_mapper.py
│   └── normalizer.py
├── processors/
│   ├── __init__.py
│   ├── student_processor.py
│   ├── assignment_manager.py
│   └── grade_calculator.py
├── exporters/
│   ├── __init__.py
│   └── excel_exporter.py
└── utils/
    ├── __init__.py
    ├── error_handler.py
    └── constants.py
tests/
├── __init__.py
├── test_filename_parser.py
├── test_column_mapper.py
├── test_normalizer.py
├── test_grade_calculator.py
└── test_student_processor.py
credentials/
└── .gitignore
```

각 `.py` 파일에는 모듈 docstring만 넣어라. 예:
```python
"""Google Drive API 클라이언트 — 인증, 다운로드, 업로드."""
```

### 0-3. pyproject.toml

```toml
[project]
name = "wave-academy"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "google-api-python-client>=2.0",
    "google-auth-oauthlib>=1.0",
    "google-auth-httplib2>=0.2",
    "openpyxl>=3.1",
    "pandas>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=5.0"]

[project.scripts]
wave-academy = "src.main:main"
```

### 0-4. requirements.txt

pyproject.toml의 dependencies를 평탄화한 requirements.txt도 생성하라 (pip install -r 호환용).

### 0-5. credentials/.gitignore

```
*.json
!.gitignore
```

### 0-6. .gitignore (프로젝트 루트)

기존 .gitignore가 있으면 Python 관련 항목을 추가하라. 없으면 생성:
```
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
credentials/*.json
.env
node_modules/
gas/
```

### 0-7. 가상환경 생성 및 의존성 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Acceptance Criteria

```bash
source .venv/bin/activate && pytest --collect-only 2>&1 | tail -5   # 테스트 수집 에러 없음
python -c "import openpyxl; import pandas; import googleapiclient; print('OK')"   # 의존성 import 성공
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

- 이 step에서 비즈니스 로직을 구현하지 마라. 이유: 다음 step에서 구현.
- `gas/` 디렉토리 내용을 Python으로 포팅하지 마라. 이유: 완전 새로 작성.
- credentials/ 디렉토리에 실제 인증 파일을 생성하지 마라. 이유: 사용자가 별도 제공.
