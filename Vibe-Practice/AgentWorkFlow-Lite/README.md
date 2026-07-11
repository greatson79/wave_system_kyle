# AgentWorkFlow-Lite

**나만의 AI 업무 자동화 시스템을 설계하는 프레임워크**

AgenticWorkflow의 핵심 DNA를 이어받은 경량 버전입니다.
비개발자도 30분 안에 첫 번째 워크플로우를 완성할 수 있습니다.

---

## 10분 시작 가이드

### 1단계. 이 폴더에서 Claude 실행
```bash
cd AgentWorkFlow-Lite
claude --dangerously-skip-permissions
```

### 2단계. 워크플로우 설계 시작
```
/new-workflow
```
Claude가 3가지 질문을 합니다. 답하면 workflow.md가 자동 생성됩니다.

### 3단계. 설계도 검토 후 실행
workflow.md를 확인하고 승인하면 구현이 시작됩니다.

---

## 폴더 구조

```
AgentWorkFlow-Lite/
├── CLAUDE.md              ← Claude 지시서 (자동 로드)
├── AGENTS.md              ← 에이전트 설계 원칙
├── soul.md                ← 이 프레임워크의 핵심 가치
├── workflow-template.md   ← 워크플로우 작성 템플릿
│
├── workflow-examples/     ← 직군별 완성 예시
│   ├── 목사-설교준비.md
│   ├── 사역자-행사기획.md
│   └── 크리에이터-콘텐츠파이프라인.md
│
├── prompt-templates/      ← 단계별 프롬프트 템플릿
│   ├── 01-research-prompt.md
│   ├── 02-planning-prompt.md
│   ├── 03-implementation-prompt.md
│   └── 04-claude-md-templates.md
│
└── .claude/
    ├── skills/workflow-generator/  ← 핵심 스킬
    └── commands/new-workflow.md    ← /new-workflow 커맨드
```

---

## 핵심 개념 3가지

### 1. 3단계 구조
모든 워크플로우는 이 순서를 따릅니다:
```
Research → Planning → Implementation
(수집)     (설계·승인)   (실행·산출)
```

### 2. SOT (단일 진실 원천)
중요한 데이터는 반드시 **하나의 파일**에 집중합니다.
같은 정보가 두 곳에 있으면 하나는 반드시 거짓입니다.

### 3. workflow.md 먼저
코드나 자동화를 시작하기 전에 **설계도를 먼저** 작성합니다.
설계 없는 실행은 시간 낭비입니다.

---

## 프롬프트 템플릿 활용법

`prompt-templates/` 폴더에 단계별 프롬프트가 있습니다.
`{}`로 표시된 부분을 내 상황에 맞게 채워서 사용하세요.

| 템플릿 | 사용 시점 |
|--------|---------|
| 01-research | 정보 수집 시작 |
| 02-planning | 계획 수립·승인 요청 |
| 03-implementation | 실제 실행 |
| 04-claude-md | CLAUDE.md 작성·개선 |

---

## 예시 참고

`workflow-examples/` 폴더에서 완성된 예시를 확인하세요.
자신의 직군과 가장 비슷한 예시를 참고해서 수정하면 빠릅니다.

---

## 팀 시스템으로 확장하기

개인 워크플로우가 완성되면 팀 시스템으로 확장할 수 있습니다:

1. `workflow.md`의 에이전트 구성 섹션에 팀원 역할 추가
2. `CLAUDE.md`에 팀 공통 규칙 추가
3. Git으로 팀원과 공유

---

*AgentWorkFlow-Lite는 AgenticWorkflow(idoforgod/AgenticWorkflow)의 DNA를 이어받은 교육용 경량 버전입니다.*
