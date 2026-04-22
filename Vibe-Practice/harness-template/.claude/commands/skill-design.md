# /skill-design — 설계 단계

기획서(`docs/skill-brief.md`)를 바탕으로 스킬의 구조를 설계하고 하네스 문서 5종을 작성한다.
실행 전 반드시 **설계 계획을 먼저 보고**한 뒤 승인을 받아 진행한다.

---

## 전제 확인

시작 전 아래를 확인한다:

```bash
# 기획서 존재 확인
ls docs/skill-brief.md
```

기획서가 없으면: "먼저 /skill-plan 으로 기획을 완료하세요." 출력 후 중단.

---

## Step 1: 설계 계획 보고 (실행 전 필수)

아래 형식으로 보고한 뒤 사용자 승인을 기다린다.

```
## 설계 계획 보고

**기획서 요약:** [skill-brief.md 핵심 3줄]

**작성할 문서 목록:**
- [ ] CLAUDE.md — 기술 스택, 절대 규칙
- [ ] docs/PRD.md — 기능 명세, 엣지케이스
- [ ] docs/ARCHITECTURE.md — 디렉토리 구조, 데이터 흐름
- [ ] docs/ADR.md — 기술 결정 근거
- [ ] docs/UI_GUIDE.md — UI 있을 경우 (없으면 생략)

**Step 분할 초안 (실행 계획):**
- Step 0: [기반 세팅]
- Step 1: [핵심 로직]
- Step 2: [...]
- Step N: [통합 검증]

**설계 시 확인할 핵심 판단:**
1. [기획서에서 모호한 부분]
2. [기술 결정이 필요한 부분]

승인하시면 문서 작성을 시작합니다.
```

---

## Step 2: 보완 질문

설계 계획 보고 후, 기획서만으로 불명확한 부분을 질문한다.
**최대 3개**만 묻는다. 더 많으면 먼저 합리적인 가정을 세우고 ADR에 기록한다.

```
설계를 위해 확인이 필요한 사항:

1. [질문 — 이 결정이 구조에 미치는 영향 명시]
   → 제 가정: [대안 제시]

2. [질문]
   → 제 가정: [대안 제시]
```

---

## Step 3: 문서 작성

승인 후 순서대로 작성한다. 각 문서 완료 후 다음으로 넘어간다.

**각 문서는 `prompts/` 폴더의 해당 프롬프트 파일을 먼저 읽은 후 양식에 맞게 작성한다:**
- `prompts/prd-prompt.md` → `docs/PRD.md`
- `prompts/architecture-prompt.md` → `docs/ARCHITECTURE.md`
- `prompts/adr-prompt.md` → `docs/ADR.md`
- `prompts/ui-guide-prompt.md` → `docs/UI_GUIDE.md` (UI 없으면 생략)

### CLAUDE.md
```markdown
# 프로젝트: [스킬명]

## 기술 스택
- [기술 1]
- [기술 2]

## 절대 규칙
- CRITICAL: [가장 중요한 불변 규칙]
- CRITICAL: [두 번째 불변 규칙]

## 개발 프로세스
- 코드 변경 전: 의도 파악 → 영향 범위 → 변경 설계
- 커밋: conventional commits (feat:, fix:, docs:, refactor:)

## 명령어
\`\`\`bash
[BUILD_COMMAND]
[TEST_COMMAND]
\`\`\`
```

### docs/PRD.md
```markdown
# PRD: [스킬명]

## 기능 목록
### F1: [기능명]
**정상 시나리오**
- 상황: ...
- 시스템 처리: ...
- 결과: ...

**엣지케이스**
| 상황 | 처리 | 사용자 메시지 |
|------|------|--------------|
| ... | ... | ... |

**에러 처리**
| 에러 | 원인 | 처리 |
|------|------|------|
| ... | ... | ... |
```

### docs/ARCHITECTURE.md
```markdown
# 아키텍처: [스킬명]

## 설계 철학
[한 줄]

## 디렉토리 구조
\`\`\`
[스킬명]/
├── SKILL.md
├── scripts/   (자동화 스크립트)
└── references/ (참조 문서)
\`\`\`

## 데이터 모델
| 엔티티 | 필드 | 타입 | 설명 |
|--------|------|------|------|

## 데이터 흐름
\`\`\`
[입력] → [처리 모듈] → [출력]
\`\`\`

## API / 인터페이스 목록
| 함수명 | 입력 | 출력 | 설명 |
|--------|------|------|------|
```

### docs/ADR.md
```markdown
# Architecture Decision Records

## ADR-001: [결정 제목]

**결정**: [무엇을 결정했는가]

**이유**:
- [이유 1]
- [이유 2]

**트레이드오프**:
- [포기한 것 / 감수하는 비용]

**대안 검토**:
| 대안 | 탈락 이유 |
|------|----------|
| ... | ... |
```

---

## Step 4: Step 파일 생성

문서 작성 완료 후 `/harness` 커맨드를 안내하거나,
직접 `phases/0-mvp/` 아래 step 파일 초안을 생성한다.

각 step 파일(`step0.md`, `step1.md` ...)의 구조:

```markdown
# Step N: [제목]

## 목표
[이 step이 완료되면 무엇이 존재하는가]

## 컨텍스트
[이전 step에서 만들어진 것 중 이 step에서 사용할 것]

## 구현 지시
[Claude에게 주는 구체적 지시]

## Acceptance Criteria
- [ ] [grep / 테스트로 확인 가능한 항목]
- [ ] [파일 존재 확인]
- [ ] [기능 동작 확인]

## 주의사항
- [CLAUDE.md의 절대 규칙 중 이 step과 관련된 것]
```

---

## 완료 후 안내

```
설계 완료.

생성된 문서:
- CLAUDE.md
- docs/PRD.md
- docs/ARCHITECTURE.md
- docs/ADR.md
- phases/0-mvp/index.json + step*.md

다음: /skill-review 1차 점검으로 문서 완성도를 확인하세요.
```
