# Wave Content Studio Claude Code 배포 설계

## 목표

공개 GitHub 저장소 `greatson79/wave-content-studio`에서 Codex용과 Claude Code용 플러그인을 함께 배포한다. Claude용 배포본은 OpenAI Sites 기능을 완전히 제외하고 기획·조사·검증·작성·편집의 사용자 참여형 루프만 제공한다.

## 저장소 구조

```text
wave-content-studio/
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── wave-content-studio/
│   │   ├── .codex-plugin/plugin.json
│   │   ├── skills/
│   │   └── ...
│   └── wave-content-studio-claude/
│       ├── .claude-plugin/plugin.json
│       ├── skills/
│       ├── shared/
│       ├── docs/
│       ├── scripts/
│       └── tests/
└── README.md
```

두 마켓플레이스의 이름은 충돌을 피하도록 구분한다.

- Codex: `wave-content-studio`
- Claude Code: `wave-content-studio-claude`

## Claude용 포함 스킬

- `content-studio-orchestrator`
- `content-topic-strategist`
- `content-researcher`
- `source-validator`
- `blog-article-writer`
- `article-editor`

Claude용 폴더에는 `sites-blog-publisher`를 복사하지 않는다.

## Claude용 완료 흐름

편집 결과가 `PASS`이고 사용자가 최종 결과를 승인하면 다음을 수행한다.

1. `workspace/final-article.md`와 `workspace/editorial-report.md`를 보존한다.
2. 제목, 요약, slug 제안, 카테고리·태그, 검증 근거를 제공한다.
3. 실행 보고서의 최종 상태를 `COMPLETE_NO_PUBLISH`로 기록한다.
4. 외부 사이트 생성, OpenAI Sites 도구 호출, 게시 요청 파일 생성 또는 배포를 수행하지 않는다.

Claude 사용자가 개인 블로그 연결을 별도로 요청하면 현재 Claude 환경에서 실제로 제공되는 연결 수단만 확인할 수 있다. 연결이 없으면 플랫폼에 붙여넣을 최종 원고만 제공한다. 이는 기본 콘텐츠 플러그인의 자동 게시 기능으로 간주하지 않는다.

## Claude 매니페스트

`plugins/wave-content-studio-claude/.claude-plugin/plugin.json`은 Claude 공식 스키마의 최소 필드만 사용한다.

- `name`
- `version`
- `description`
- `author`

Codex 전용 `interface`, `capabilities`, `defaultPrompt`, `skills` 경로 선언은 Claude 매니페스트에 넣지 않는다. Claude는 플러그인 루트의 `skills/`를 자동 발견한다.

## Claude 마켓플레이스

루트 `.claude-plugin/marketplace.json`은 다음 플러그인을 상대 경로로 가리킨다.

```json
{
  "name": "wave-content-studio-claude",
  "owner": {
    "name": "Wave AI Networks"
  },
  "plugins": [
    {
      "name": "wave-content-studio-claude",
      "source": "./plugins/wave-content-studio-claude",
      "description": "User-reviewed sourced article workflow for Claude Code without Sites publishing"
    }
  ]
}
```

## Claude 전용 정책 변경

- `content-studio-orchestrator`에서 Sites 게시 단계, 고정 Project ID, 게시 승인 문구와 `sites-blog-publisher` 참조를 제거한다.
- `workflow-gates.md`에서 Sites 게시 게이트와 게시 상태를 제거한다.
- `workspace-contract.md`에서 `publication-request.json`과 `publication-report.md`를 기본 산출물에서 제거한다.
- `pipeline-run-report.template.md`에 `COMPLETE_NO_PUBLISH`를 허용한다.
- 문서와 README에서 Claude의 마지막 단계가 편집 승인 후 최종 원고 제공임을 명시한다.

출처 검증, 이중 승인 근거, 덮어쓰기 승인과 사용자 참여 루프는 Codex용과 동일하게 유지한다.

## 동기화 원칙

Claude용 배포본은 Codex 원본의 6개 공통 스킬과 공통 정책을 기반으로 생성하되, Claude 전용 수정이 필요한 파일은 명시적으로 별도 관리한다. 재배포 전 다음을 검사한다.

- 공통 6개 스킬 이름과 핵심 출처 정책이 일치한다.
- Claude 폴더에 `sites-blog-publisher`가 없다.
- Claude 폴더 전체에 `appgprj_`, `승인 포스팅해줘`, `AWAITING_PUBLISH_APPROVAL`, `OpenAI Sites`가 없다.
- Claude 문서가 존재하지 않는 스킬을 참조하지 않는다.

## 검증

- `claude plugin validate .`
- Claude 마켓플레이스 JSON 파싱
- Claude 플러그인 JSON 파싱
- 6개 `SKILL.md` frontmatter 검증
- Sites 금지 문자열 검사
- Claude 전용 계약 테스트
- Codex 기존 전체 계약 테스트
- Codex 플러그인 검증
- 비밀값 검사
- Git 작업 트리와 원격 커밋 일치 확인

로컬에 Claude CLI가 없거나 인증이 필요한 경우 구조·JSON·스킬·계약 검증을 먼저 완료하고, 실행 검증의 제한을 보고한다.

## README

루트 README는 다음 순서로 작성한다.

1. 프로젝트 개요
2. Codex와 Claude Code 기능 비교
3. Codex 설치
4. Claude Code 설치
5. 플랫폼별 호출 예
6. 사용자 참여형 단계 루프
7. 출력 파일
8. 업데이트·제거 방법
9. 보안과 외부 게시 정책
10. 개발자 검증 명령

Claude Code 설치 명령:

```text
/plugin marketplace add greatson79/wave-content-studio
/plugin install wave-content-studio-claude@wave-content-studio-claude
/reload-plugins
```

Claude 호출:

```text
/wave-content-studio-claude:content-studio-orchestrator
```

## 비목표

- Claude Code에서 OpenAI Sites 게시 지원
- Claude용 비공식 브라우저 자동 게시
- Codex와 Claude 매니페스트를 하나의 파일로 통합
- 사용자 승인 없는 외부 게시
