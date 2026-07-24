# 프로젝트: Wave Academy 수강관리 시스템

## 기술 스택
- Python 3.12+
- Google Drive API (google-api-python-client, oauth2client)
- openpyxl (Excel 읽기/쓰기)
- pandas (데이터 정리·분석)
- pytest (테스트)

## 아키텍처 규칙
- CRITICAL: 원본 업로드 파일은 **읽기 전용**. 절대 수정하지 않는다.
- CRITICAL: 모든 데이터 원천은 구글드라이브 `wave_수강신청/` 폴더. AI가 데이터를 "기억"으로 생성하지 않는다.
- CRITICAL: NotebookLM 연동은 이 시스템 범위 밖. 정제 스프레드시트 생성까지가 범위.
- CRITICAL: 코드 변경 전 의도 파악 → 영향 범위 분석 → 변경 설계 3단계 수행.
- 컬럼 매핑은 인덱스가 아닌 **헤더 텍스트 키워드** 기반.
- 에러 처리는 중앙 처리. 개별 파일 실패가 전체를 중단시키면 안 됨.

## 데이터 원천
- 구글드라이브 계정: `waveainetworks@gmail.com`
- 수강신청 파일: `내 드라이브/wave_수강신청/` (.xlsx, .gsheet)
- 파일명 패턴: `({월} {대상} Class#{N}) {강의명}(응답)` (변형 6종 — ADR-005)
- NotebookLM 계정: 별도 (Claude Code MCP로 연동)
- 결과물 위치: `내 드라이브/Wave/행정/수강관리/` 하위

## 분류 체계
- 카테고리: 교회강의 / Wave Academy / 자격증과정 / 외부강의
- 클래스: Class#1(파운데이션) / Class#2(심화) / Class#3(활용)
- 대상: 목회자 / 일반 / 교회(성도)
- 지역: 본부 / 부산 / 충남 / 꿈별 등

## 개발 프로세스
- 커밋 메시지: conventional commits (feat:, fix:, docs:, refactor:)

## 명령어
```bash
# 실행 (전체 파이프라인)
python src/main.py

# 테스트
pytest

# 특정 기능
python src/main.py --scan-only     # 파일 스캔만
python src/main.py --export-only   # 내보내기만
```

## 참조 문서
| 문서 | 경로 | 내용 |
|------|------|------|
| PRD | `docs/PRD.md` | 기능 명세, 엣지케이스, 에러 핸들링 |
| 아키텍처 | `docs/ARCHITECTURE.md` | 파일 구조, 데이터 흐름, 스키마 |
| ADR | `docs/ADR.md` | 아키텍처 결정 기록 |
