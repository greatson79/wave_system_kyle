# 프로젝트: {{PROJECT_NAME}}

## 기술 스택
<!-- 이 프로젝트에서 사용하는 기술을 나열하세요 -->
- (예: Python 3.12, FastAPI, PostgreSQL)
- (예: Google Apps Script, HTML Service)
- (예: Next.js 15, TypeScript, Vercel)

## 아키텍처 규칙
<!-- CRITICAL 접두사가 붙은 규칙은 어떤 상황에서도 예외 없이 적용됩니다 -->
- CRITICAL: {{가장 중요한 불변 규칙}}
- CRITICAL: {{두 번째 불변 규칙}}
- {{일반 규칙}}

## 개발 프로세스
- CRITICAL: 코드 변경 전 의도 파악 → 영향 범위 분석 → 변경 설계 3단계 수행
- 커밋 메시지: conventional commits (feat:, fix:, docs:, refactor:)

## 명령어
```bash
# 빌드
{{BUILD_COMMAND}}

# 테스트
{{TEST_COMMAND}}

# 배포
{{DEPLOY_COMMAND}}
```

## 참조 문서
| 문서 | 경로 | 내용 |
|------|------|------|
| PRD | `docs/PRD.md` | 기능 명세, 엣지케이스, 에러 핸들링 |
| 아키텍처 | `docs/ARCHITECTURE.md` | 파일 구조, 데이터 흐름, 스키마 |
| ADR | `docs/ADR.md` | 아키텍처 결정 기록 |
