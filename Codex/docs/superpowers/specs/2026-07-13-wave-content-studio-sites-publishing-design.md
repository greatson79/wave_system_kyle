# Wave Content Studio Sites 게시 확장 설계

- 작성일: 2026-07-13
- 상태: 사용자 설계 승인 완료
- 변경 분류: feature
- 대상 Plugin: `wave-content-studio`
- 고정 게시 대상: WAVE AI Networks Sites 블로그

## 1. 목표

사용자가 주제, 대상 독자, 목적을 말하면 `wave-content-studio`가 기획, 리서치, 독립 출처 검증, 구성·작성, 편집·검수를 수행한다. 검수 통과 후 게시 후보를 사용자에게 보고하고, 사용자가 정확한 승인 문구 `승인 포스팅해줘`를 입력한 경우에만 현재 WAVE AI Networks Sites 블로그에 게시한다.

## 2. 사용자 경험

### 새 글 제작

```text
AI 시대 청소년의 정체성이라는 주제로
중학생을 대상으로 자신과 타인을 존중하게 돕는 글을 작성해줘.
```

Plugin은 필요한 입력을 확정한 뒤 기존 파이프라인을 실행한다.

```text
TOPIC → RESEARCH → VALIDATION → WRITING → EDITING
```

편집 판정이 `PASS`이면 다음 내용을 보고하고 게시 승인을 기다린다.

- 제목, 카테고리, 대상 독자
- 핵심 요약
- 승인된 출처와 검수 판정
- 최종 원고 경로
- 예상 게시 주소
- 남은 주의사항

### 게시 승인

사용자가 정확히 다음 문구를 입력한다.

```text
승인 포스팅해줘
```

Plugin은 승인 대상 원고가 바뀌지 않았는지 다시 확인한 후 게시한다. 다른 승인 표현은 게시 권한으로 해석하지 않고 확인을 요청한다.

## 3. 아키텍처

기존 5개 전문 Skill과 Orchestrator를 유지하고 게시 전용 Skill 하나를 추가한다.

| 구성요소 | 책임 |
|---|---|
| `content-topic-strategist` | 주제, 독자, 목적과 조사 질문 기획 |
| `content-researcher` | 후보 자료와 주장-출처 연결 수집 |
| `source-validator` | 출처 존재, 최신성, 주장 일치 독립 검증 |
| `blog-article-writer` | 승인된 근거만으로 초안 작성 |
| `article-editor` | 구조, 논리, 문체, 근거 표현 검수 |
| `content-studio-orchestrator` | 순서, 승인, 상태 전이, 복구, 보고 |
| `sites-blog-publisher` | 승인 검증, 변환, 중복 검사, 테스트, Sites 게시 |

`sites-blog-publisher`는 기획, 리서치, 글쓰기 또는 편집을 수행하지 않는다. 콘텐츠 문제를 발견하면 직접 고치지 않고 가장 이른 유효 단계로 돌려보낸다.

## 4. 상태 모델

정상 흐름은 다음과 같다.

```text
TOPIC
→ RESEARCH
→ VALIDATION
→ WRITING
→ EDITING
→ AWAITING_PUBLISH_APPROVAL
→ PUBLISHING
→ PUBLISHED
```

분기 상태는 다음과 같다.

- `REVISION_REQUESTED`: 사용자가 수정 요청
- `PUBLISH_BLOCKED`: 승인 조건 불충족
- `PUBLISH_FAILED`: 로컬 검증 또는 Sites 배포 실패
- `ALREADY_PUBLISHED`: 같은 원고 지문이 이미 게시됨

게시 실패 후 재시작은 콘텐츠 파이프라인을 반복하지 않고 `PUBLISHING` 직전 검증부터 수행한다. 단, 최종 원고 또는 검수 보고서가 바뀌면 `AWAITING_PUBLISH_APPROVAL`로 되돌아간다.

## 5. 게시 승인 계약

다음 조건을 모두 만족해야 게시할 수 있다.

1. `workspace/final-article.md`가 존재한다.
2. `workspace/editorial-report.md` 최종 판정이 `PASS`다.
3. `workspace/pipeline-run-report.md`가 완료된 편집 단계와 일치한다.
4. `workspace/publication-request.json` 상태가 `AWAITING_PUBLISH_APPROVAL`이다.
5. 승인 요청에 기록된 원고 SHA-256 지문이 현재 원고 지문과 일치한다.
6. 사용자가 정확한 승인 문구 `승인 포스팅해줘`를 입력했다.
7. 같은 원고 지문이 이전 게시 기록에 존재하지 않는다.
8. 게시 주소가 다른 원고에 사용 중이지 않다.

승인 보고 후 제목, 본문, 출처, 카테고리, 요약 또는 대표 이미지가 바뀌면 원고 지문을 다시 계산하고 기존 승인을 무효화한다.

## 6. 산출물 계약

기존 `workspace/` 계약에 다음 두 파일을 추가한다.

```text
workspace/
├── final-article.md
├── editorial-report.md
├── pipeline-run-report.md
├── publication-request.json
└── publication-report.md
```

### `publication-request.json`

```json
{
  "schema_version": 1,
  "status": "AWAITING_PUBLISH_APPROVAL",
  "site": {
    "name": "WAVE AI Networks",
    "project_id": "appgprj_6a54f82761348191a9b1da66f9053c7a"
  },
  "article": {
    "title": "Example title",
    "slug": "example-title",
    "category": "youth-identity",
    "audience": "중학생",
    "summary": "Example summary",
    "source_count": 8,
    "editorial_verdict": "PASS",
    "content_sha256": "64-character-lowercase-hex"
  },
  "approval": {
    "required_phrase": "승인 포스팅해줘",
    "approved": false
  }
}
```

Project ID는 게시 대상을 고정하고 잘못된 사이트 배포를 차단하기 위한 공개 식별자다. 인증 토큰이나 자격 증명은 어떤 산출물에도 저장하지 않는다.

### `publication-report.md`

다음 항목을 기록한다.

- 게시 요청 생성 시각
- 승인 문구와 승인 시각
- 승인된 원고 지문
- 게시 전 검증 결과
- 게시 버전과 공개 URL
- 배포 결과와 실패 원인
- 중복 또는 주소 충돌 판정
- 재시작 지점

## 7. Sites 게시 어댑터

게시 어댑터는 고정된 WAVE AI Networks 블로그 저장소의 콘텐츠 계약으로 Markdown을 변환한다.

필수 게시 필드:

- 제목
- 고유 slug
- 4개 허용 카테고리 중 하나
- 대상 독자
- 요약
- 읽기 시간
- 공개 날짜
- 구조화된 본문
- 승인된 출처 링크
- 상태 `published`

허용 카테고리:

- `ai-automation`
- `church-ministry`
- `era-analysis`
- `youth-identity`

카테고리가 불명확하거나 허용 목록 밖이면 게시하지 않고 사용자 결정을 요청한다.

## 8. 게시 실행 순서

1. 게시 승인 계약을 검증한다.
2. 기존 게시 지문과 slug를 검사한다.
3. 최종 Markdown을 블로그 콘텐츠 계약으로 변환한다.
4. 콘텐츠 계약 테스트를 실행한다.
5. 주요 화면 렌더링 테스트를 실행한다.
6. 생산 빌드와 코드 검사를 실행한다.
7. 검증된 소스를 Sites 전용 저장소에 전송한다.
8. 새 Sites 버전을 저장한다.
9. 공개 배포한다.
10. 배포 성공 상태와 공개 URL을 확인한다.
11. `publication-report.md`와 파이프라인 보고서를 갱신한다.

단계 4~6 중 하나라도 실패하면 Sites 도구를 호출하지 않는다.

## 9. 중복과 충돌 방지

- 원고 SHA-256 지문이 기존 게시 기록과 같으면 `ALREADY_PUBLISHED`로 중단한다.
- 동일 slug가 같은 원고 지문을 가리키면 기존 URL을 반환하고 재배포하지 않는다.
- 동일 slug가 다른 지문을 가리키면 자동 덮어쓰지 않고 `PUBLISH_BLOCKED`로 중단한다.
- 수정 발행은 기존 게시물 수정이라는 사용자의 명시적 요청과 새 승인을 요구한다.

## 10. 오류와 복구

- 최종 원고 없음: `EDITING`으로 복귀
- 편집 판정 미통과: 원인에 따라 `TOPIC`, `RESEARCH`, `VALIDATION`, `WRITING` 중 가장 이른 단계로 복귀
- 원고 지문 불일치: 승인 무효화 후 새 승인 보고
- 카테고리 불명확: 사용자 결정 요청
- 로컬 테스트 실패: `PUBLISH_FAILED`, Sites 호출 금지
- 소스 전송 실패: 승인과 게시 요청 보존, 전송 단계부터 재시도
- Sites 저장 실패: 저장 단계부터 재시도
- Sites 배포 실패: 승인과 저장 버전을 보존하고 배포 단계부터 재시도
- 같은 게시 단계가 두 번 연속 실패: 자동 반복 중단 후 사용자 보고

## 11. 보안과 권한

- 게시 대상 Project ID는 고정한다.
- Sites 자격 증명은 단기 메모리에서만 사용한다.
- 토큰을 파일, Git 원격 URL, 설정, 실행 보고서에 저장하지 않는다.
- 공개 배포는 정확한 승인 문구 이후에만 허용한다.
- Plugin은 Sites 배포와 관련 없는 외부 시스템에 쓰지 않는다.
- 승인 문구는 특정 원고 지문 한 개에만 유효하며 다른 글에 재사용하지 않는다.

## 12. Plugin 변경 범위

예상 변경:

- `.codex-plugin/plugin.json`: 버전, 설명, capabilities, 기본 프롬프트 갱신
- `skills/content-studio-orchestrator/SKILL.md`: 게시 상태와 승인 게이트 추가
- `skills/sites-blog-publisher/SKILL.md`: 신규 게시 전용 Skill
- `skills/sites-blog-publisher/agents/openai.yaml`: 신규 Skill UI 메타데이터
- `shared/policies/workflow-gates.md`: 게시 승인 게이트 추가
- `shared/policies/workspace-contract.md`: 게시 산출물 추가
- `shared/templates/pipeline-run-report.template.md`: 게시 단계와 승인 기록 추가
- `shared/templates/publication-report.template.md`: 신규 게시 보고 템플릿
- `docs/content-workflow.md`: 전체 상태 흐름 갱신
- `README.md`: 새 사용법과 범위 갱신
- `tests/`: 게시 승인, 지문, 중복, 충돌, 실패 복구 계약 테스트 추가
- `scripts/validate-workflow-contract.sh`: 새 파일과 계약 검증 추가

기존 전문 Skill의 단일 책임은 유지한다. 게시 기능을 기존 Writer 또는 Editor에 넣지 않는다.

## 13. 검증 기준

### Plugin 계약

- 기존 전체 파이프라인 계약 테스트가 유지된다.
- 정확한 승인 문구가 없으면 게시 단계로 전이하지 않는다.
- 검수 `PASS`가 아니면 게시 요청을 만들지 않는다.
- 원고 변경 후 이전 승인이 무효화된다.
- 동일 지문 중복 게시를 차단한다.
- slug 충돌을 차단한다.
- 게시 실패 후 올바른 단계에서 재시작한다.
- 자격 증명이 파일이나 Git 설정에 남지 않는다.

### 블로그 계약

- 승인된 제목, 본문, 카테고리, 대상 독자와 출처가 보존된다.
- 새 게시물 경로가 정상 렌더링된다.
- 콘텐츠 테스트, 렌더링 테스트, 생산 빌드와 코드 검사가 통과한다.
- Sites 배포 성공 후 공개 URL이 기록된다.

### Plugin 검증 도구

- `bash tests/run-contract-tests.sh`
- `bash scripts/validate-workflow-contract.sh`
- Plugin validator
- 각 Skill validator

## 14. 완료 조건

- 새 `sites-blog-publisher` Skill이 기존 Plugin에서 발견된다.
- Orchestrator가 편집 완료 후 `AWAITING_PUBLISH_APPROVAL`로 멈춘다.
- 승인 보고가 고정 형식으로 생성된다.
- 정확한 승인 문구 이후에만 게시 실행이 가능하다.
- 현재 WAVE AI Networks Sites 블로그 외 다른 대상은 거부된다.
- 성공 시 공개 URL, 실패 시 재시작 지점이 보고된다.
- Plugin과 기존 콘텐츠 파이프라인의 모든 검증이 통과한다.

