# AI 개발 인수인계 스킬 — 컨텍스트 릴레이 (Context Relay)

> 여러 AI 코딩 도구를 오가도 프로젝트의 기억이 끊기지 않게 하는 **AI 개발 블랙박스**.
> Claude Code · Cursor · Codex · Antigravity를 넘나들며 작업해도 목표·판단·프롬프트·변경 이력·다음 할 일을 잃지 않는다.

---

## 1. 한 줄 요약

**Context Relay는 AI 코딩 세션의 맥락을 자동으로 기록하고, 다음 세션이 바로 이어 달릴 수 있게 인계서를 만들어주는 Claude Code 스킬입니다.**

프로젝트 시작 시 모든 AI 도구가 공유할 "작업 헌법"을 세우고, 작업 중 흩어지는 기억(프롬프트·결정·변경 파일·리스크)을 SQLite에 모으고, 다음 세션·다음 도구가 읽을 인계 문서와 대시보드로 되돌려줍니다.

---

## 2. 왜 필요한가 — 사라지는 것은 코드가 아니라 기억이다

AI 코딩에서 가장 위험한 것은 코드가 틀리는 것이 아니라 **프로젝트의 기억이 사라지는 것**입니다.

파일은 남습니다. 하지만—

- **왜** 이 라이브러리를 선택했는지
- 어떤 파일은 **건드리면 안 되는지**
- 어떤 프롬프트가 **효과적이었는지**
- 지금 **어디까지 했고**, 다음 세션에서 **무엇부터** 해야 하는지

이런 것들은 세션이 끝나면 증발합니다. 도구를 바꾸면(Claude Code → Cursor → Codex) 더 심해집니다. 매번 프로젝트를 처음부터 다시 설명하고, 같은 실수를 반복하고, "내가 어제 왜 이렇게 짰더라"를 되짚느라 시간을 씁니다.

**AI 코딩 도구는 점점 많아지지만, 프로젝트의 기억은 흩어집니다.** Context Relay는 그 기억을 붙잡아 다음 세션으로 릴레이하는 도구입니다.

### 이런 분께

- Claude Code, Cursor, Codex, Antigravity를 **번갈아 쓰는** 개발자
- 하나의 프로젝트를 **여러 날·여러 세션**에 걸쳐 이어가는 사람
- AI에게 매번 "이 프로젝트는 이런 거고, 여기까지 했고…"를 **다시 설명하는 게 지겨운** 사람
- 팀·클라이언트에게 넘길 **인수인계 문서를 자동으로** 만들고 싶은 사람
- 효과 있었던 **프롬프트를 재사용**하고 싶은 사람

---

## 3. 핵심 개념 — DB는 기억, MD는 인계서

Context Relay는 두 개의 층으로 동작합니다.

| 층 | 정체 | 역할 |
|---|---|---|
| **SQLite DB** | 원천 기억 저장소 | 세션·프롬프트·변경 파일·결정·리스크의 원본 데이터. FTS5 전문 검색 내장. |
| **Markdown 문서** | 사람·AI가 읽는 인계서 | DB에서 생성되는 요약 산출물. handoff·charter·worklog 등. |

**판단은 Claude가, 저장·검색·집계·렌더링은 검증된 스크립트가 합니다.** 덕분에 데이터가 어긋나지 않고, DB에 쌓인 기억이 언제든 검색·시각화됩니다.

### 데이터 흐름

```text
프로젝트 셋업 (공통 작업 헌법 생성)
   → AI 도구로 작업 (Claude Code / Cursor / Codex / Antigravity)
   → 세션 종료 시 Capture (프롬프트·변경 파일·결정·리스크 수집)
   → SQLite 저장 + 검색 인덱스 갱신
   → 인계 문서(handoff) + 대시보드 생성
   → 다음 세션·다음 도구가 handoff 읽고 이어서 작업
```

---

## 4. 주요 기능

### 4.1 프로젝트 셋업 — 모든 AI 도구가 공유할 작업 헌법

`/context-relay setup` 한 번으로 프로젝트에 공통 기준 문서 세트를 세웁니다. 인터뷰(목표·MVP 범위·하지 않을 것·사용 도구·기술 스택·완료 기준·위험 영역)를 거쳐 다음을 생성합니다.

- `project-charter.md` — 프로젝트 헌법 (목표·범위·완료 기준)
- `PRD.md` / `TASKS.md` — 없으면 생성, **있으면 보존**
- `CLAUDE.md` / `AGENTS.md` — 기존 내용 **덮어쓰지 않고** Context Relay 섹션만 append
- `.cursor/rules/context-relay.mdc` — Cursor용 규칙
- SQLite DB + config + 대시보드 초기 파일

이후 **어떤 AI 도구를 켜든** 같은 기준 문서를 읽고 작업합니다.

### 4.2 Capture — 세션 종료 시 맥락을 통째로 저장

`/context-relay capture` 로 현재 세션을 11단계로 기록합니다.

- git 상태·변경 파일 수집 (diff 요약 포함)
- 사용한 프롬프트 + 결과 요약 + 성공 점수 기록
- 완료/미완료 작업 분리 → task 갱신
- 결정 사항·리스크 추출 → decision-log / risk-notes 갱신
- handoff·worklog 문서 갱신 + 대시보드 재생성

**다른 도구(Cursor·Codex)에서 한 작업도** git diff와 문답으로 사후 캡처해 `tool_name`을 해당 도구로 기록합니다.

### 4.3 Handoff & Resume — 다음 세션이 바로 이어 달리는 인계서

- `/context-relay handoff` — 현재 상태 / 완료·미완료 / 변경 파일과 이유 / 결정 / 위험 파일 / 다음 액션 3~5개를 담은 인계서 생성
- `/context-relay resume` — 다음 AI 도구에 **그대로 붙여 넣을** 세션 프롬프트 생성 (읽을 문서·목표·수정 금지 영역·작업 순서·완료 기준)

### 4.4 Search — 과거 작업 이력 전문 검색

`/context-relay search "질의"` — SQLite FTS5/BM25로 세션·프롬프트·결정·파일 변경을 검색합니다. "그때 그 결정 왜 했더라", "이 파일 언제 왜 바꿨더라"를 즉시 되찾습니다. (FTS5 불가 환경에서는 LIKE 폴백)

### 4.5 Dashboard — 10초 만에 프로젝트 상태 파악

`/context-relay dashboard` — 외부 의존성 없는 **자체완결 정적 HTML**을 생성합니다. 진행 중 task, 병목 task, 위험 파일, 활동 히트맵, 프롬프트·결과 이력을 한눈에 봅니다.

### 4.6 Prompt Library & GitHub Summary

- `/context-relay prompts` — 효과 있었던 프롬프트를 날짜별로 정리한 재사용 라이브러리
- `/context-relay github-summary` — git 상태 기반 Conventional Commits 커밋 메시지·PR 설명 초안 생성

---

## 5. 명령어 한눈에

| 명령 | 하는 일 |
|---|---|
| `/context-relay setup` | 인터뷰 후 공통 작업 헌법 + 도구별 지침 + DB + 대시보드 전체 생성 |
| `/context-relay init` | context/ 폴더와 DB 등 기본 구조만 생성 |
| `/context-relay capture` | 세션 변경 내역·프롬프트·결정·리스크 저장 (세션 종료 전 필수) |
| `/context-relay handoff` | 다음 세션 인계 문서 생성·갱신 |
| `/context-relay resume` | 다음 AI 도구에 붙여 넣을 세션 프롬프트 생성 |
| `/context-relay search "질의"` | 세션·프롬프트·결정·파일 변경 전문 검색 |
| `/context-relay dashboard` | 로컬 정적 HTML 대시보드 생성·갱신 |
| `/context-relay prompts` | 프롬프트 라이브러리 생성·조회 |
| `/context-relay github-summary` | 커밋 메시지·PR 설명 초안 생성 |
| `/context-relay status` | 현재 task·세션·토큰 요약 보고 |

인자 없이 `/context-relay`만 호출하면 초기화된 프로젝트에서는 상태 요약과 메뉴를, 미초기화 프로젝트에서는 셋업을 제안합니다.

---

## 6. 무엇이 다른가

| | 그냥 CLAUDE.md 메모 | 노션·문서 수기 정리 | **Context Relay** |
|---|---|---|---|
| 여러 AI 도구 공통 기준 | ✕ | △ | **✓ (한 번 셋업으로 전 도구 공유)** |
| 세션 맥락 자동 수집 | ✕ | ✕ | **✓ (git diff + 프롬프트 + 결정)** |
| 과거 이력 검색 | ✕ | △ | **✓ (FTS5/BM25 전문 검색)** |
| 다음 세션 인계서 | 수기 | 수기 | **✓ (자동 생성)** |
| 상태 시각화 | ✕ | ✕ | **✓ (정적 HTML 대시보드)** |
| 민감정보 마스킹 | ✕ | ✕ | **✓ (저장 직전 자동)** |

---

## 7. 보안 — 전부 로컬, 외부 전송 없음

- **로컬 우선**: 모든 데이터는 프로젝트 안의 `context-relay/context-relay.sqlite` 한 파일에만 저장됩니다. 외부 서버 전송이 없습니다.
- **자동 마스킹**: 저장 직전 API 키·토큰·비밀번호·GitHub/AWS/Slack 키·Bearer 헤더·JWT·PEM 블록·.env 값 등을 `[MASKED:<종류>]`로 자동 치환합니다.
- **외부 반출은 명시적 export만**: 사용자가 직접 export를 실행할 때만 JSON 덤프가 생성됩니다.

---

## 8. 요구사항 & 설치

**요구사항**

- Claude Code
- `python3` (3.9 이상) — **표준 라이브러리만 사용**하므로 pip 등 외부 의존성 설치가 전혀 필요 없습니다.

**설치**

```bash
# 전역 설치 (모든 프로젝트에서 사용)
cp -r context-relay ~/.claude/skills/context-relay

# 또는 특정 프로젝트에만 설치
cp -r context-relay <project>/.claude/skills/context-relay
```

**빠른 시작**

1. 프로젝트 루트에서 `/context-relay setup` → 공통 작업 헌법·DB·대시보드 생성
2. 평소처럼 Claude Code·Cursor·Codex로 작업
3. 세션 종료 시 `/context-relay capture` → 맥락 저장
4. 다른 도구를 켜면 handoff·next-session-prompt를 읽고 이어서 작업

---

## 9. 구성물

- **결정론 엔진** `cr.py` — DB init/CRUD/검색/마스킹/git/통계 (표준 라이브러리 Python)
- **대시보드 생성기** `cr_dashboard.py` — 자체완결 정적 HTML
- **10개 서브커맨드** 워크플로우 (`SKILL.md`)
- **9종 상세 절차서** (`references/`) — architecture · capture-protocol · handoff-guide · db-schema · search-guide · dashboard-guide · setup-guide · github-guide · PRD
- **13종 템플릿** (`templates/`) — charter · handoff · worklog · decision-log · risk-notes · prompt-library · Cursor Rules 등
- **원클릭 배포 패키지** (`dist/` — install.sh 포함)

---

## 10. 가격

| 구성 | 가격 |
|---|---|
| **정가** | **33,000원** |
| 얼리버드 / 런칭 프로모션 | 24,900원 |

> Context Relay는 프로젝트당 **매 세션 반복 사용**되는 개발 생산성 인프라입니다. 한 번의 맥락 손실로 날리는 시간을 생각하면, 첫 프로젝트에서 회수됩니다.

---

## 11. FAQ

**Q. Cursor나 Codex 세션도 자동으로 기록되나요?**
도구 내부 로그 자동 수집은 범위 밖입니다. 대신 **사후 캡처**를 씁니다 — 다른 도구로 작업한 뒤 Claude Code로 돌아와 `capture`를 실행하면 git diff와 문답으로 그 세션을 재구성해 해당 도구로 기록합니다.

**Q. 기존 CLAUDE.md가 있는데 덮어쓰나요?**
아니요. `CLAUDE.md`·`AGENTS.md`는 마커 블록(`<!-- context-relay:begin -->` … `<!-- context-relay:end -->`)만 append 하고 기존 내용은 보존합니다. `PRD.md`·`TASKS.md`·`README.md`는 이미 있으면 건드리지 않습니다.

**Q. 데이터는 어디로 가나요?**
전부 로컬입니다. 프로젝트 안 SQLite 한 파일에 저장되고 외부 전송이 없습니다.

**Q. SQLite DB를 직접 열어도 되나요?**
읽기는 자유입니다. 다만 **쓰기는 반드시 `cr.py`를 경유**해야 합니다 — 직접 INSERT/UPDATE 하면 검색 인덱스 동기화와 마스킹이 건너뛰어져 데이터가 어긋납니다.

**Q. 설치가 복잡한가요?**
폴더를 스킬 디렉터리에 복사하면 끝입니다. Python 표준 라이브러리만 쓰므로 별도 설치가 없습니다.
