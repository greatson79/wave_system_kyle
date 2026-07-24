# Harness Framework Template

Claude Code 기반 자동 구현 하네스. 기획 문서를 작성하면, step 단위로 분할된 구현 계획을 Claude가 순차 실행한다.

## 빠른 시작

### 1. 템플릿 복사

```bash
cp -r harness-template my-project
cd my-project
git init
```

### 2. 기획 문서 작성

`{{placeholder}}`를 프로젝트에 맞게 채운다:

| 파일 | 용도 | 작성 순서 |
|------|------|----------|
| `CLAUDE.md` | 기술 스택, 불변 규칙, 빌드/테스트 커맨드 | 1번째 |
| `docs/PRD.md` | 기능 명세, 엣지케이스, 에러 핸들링 | 2번째 |
| `docs/ARCHITECTURE.md` | 디렉토리 구조, 데이터 모델, 데이터 흐름 | 3번째 |
| `docs/ADR.md` | 기술 선택의 이유와 트레이드오프 | 4번째 |
| `docs/UI_GUIDE.md` | 색상, 레이아웃, 컴포넌트 (UI 없으면 삭제) | 선택 |

### 3. Step 설계

```
claude> /harness
```

Claude가 문서를 읽고 step 초안을 제시한다. 피드백 후 승인하면 `phases/` 아래에 실행 파일이 생성된다.

### 4. 실행

```bash
python3 scripts/execute.py 0-mvp          # step 순차 실행
python3 scripts/execute.py 0-mvp --push   # 완료 후 자동 push
```

## 구조

```
my-project/
├── CLAUDE.md                    # 프로젝�� 규칙 (AI가 매 step마다 읽음)
├── docs/
│   ├── PRD.md                   # 기능 명세
│   ├── ARCHITECTURE.md          # 아키텍처
│   ├── ADR.md                   # 결정 기록
│   └── UI_GUIDE.md              # UI 가이드 (선택)
├── phases/
│   ├── index.json               # 전체 phase 현황
│   └── 0-mvp/                   # phase별 디렉토리 (자동 생성)
│       ├── index.json           # step 목록 + 상태
│       ├── step0.md             # 각 step 지시서
│       ├── step1.md
│       └── ...
├── scripts/
│   ├── execute.py               # 하네스 실행기
│   └─��� test_execute.py          # 실행기 테스트
└── .claude/
    ├── commands/
    │   ├── harness.md           # /harness 커맨드
    │   └── review.md            # /review 커맨드
    └── settings.json            # hooks (안전장치)
```

## 하네스가 자동으로 하는 것

| 기능 | 설명 |
|------|------|
| 브랜치 관리 | `feat-{phase}` 브랜치 자동 생성/checkout |
| 가드레일 주입 | CLAUDE.md + docs/*.md를 매 step 프롬프트에 포함 |
| 컨텍스트 누적 | 완료된 step의 summary를 다음 step�� 전달 |
| 자가 교정 | 실패 시 최대 3회 재시도 (에러 메시지 피드백) |
| 2단계 커밋 | 코드(`feat`)와 메타데이터(`chore`) 분리 |
| 타임스탬프 | started_at, completed_at 등 자동 기록 |

## Hooks (안전장치)

| Hook | 대상 | 동작 |
|------|------|------|
| PreToolUse/Bash | 위험 명령 | `rm -rf`, `git push --force`, `git reset --hard`, `DROP TABLE` 차단 |
| PreToolUse/Write | 큰 파일 | 800줄 초과 파일 쓰기 차단 |
| Stop | 세션 종료 | 안내 메시지 출력 |

프로젝트에 맞게 `.claude/settings.json`을 수정하세요:
- Stop hook에 빌드 검증 커맨드 추가
- PreToolUse에 프로젝트별 위험 명령 추가

## 에러 복구

```bash
# step이 error로 끝난 경우:
# 1. phases/{phase}/index.json에서 해당 step의 status → "pending"
# 2. error_message 삭제
# 3. 재실행
python3 scripts/execute.py {phase}

# step이 blocked인 경우:
# 1. blocked_reason 확인 후 사유 해결
# 2. status → "pending", blocked_reason 삭제
# 3. 재실행
```

## 요구사항

- Python 3.10+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- Git
- Node.js (Write hook용)
