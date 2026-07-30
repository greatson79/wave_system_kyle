# Wave Content Studio 설치 및 사용 안내

## 1. 소개

**Wave Content Studio**는 근거 기반 블로그 콘텐츠를 다음 순서로 제작하는 AI 워크플로우 플러그인입니다.

```text
콘텐츠 기획
→ 자료 조사
→ 출처 검증
→ 초안 작성
→ 편집 및 최종 원고
```

각 단계는 자동으로 끝까지 진행되지 않습니다. 플러그인이 실행 전에 사용자의 방향을 확인하고, 결과를 파일로 저장한 뒤 검토를 요청합니다.

```text
방향 확인
→ 현재 단계 실행
→ 결과 파일 저장
→ 사용자 검토
   ├─ 승인: 다음 단계
   └─ 수정 요청: 현재 단계 재실행
```

## 2. 관련 링크

- [Wave Content Studio GitHub 저장소](https://github.com/greatson79/wave-content-studio)
- [Claude Code 플러그인 공식 문서](https://code.claude.com/docs/en/plugins)
- [Claude Code 플러그인 마켓플레이스 공식 문서](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code 플러그인 설치 공식 문서](https://code.claude.com/docs/en/discover-plugins)

## 3. 지원 현황

| 기능 | Codex | Claude Code |
|---|---:|---:|
| 콘텐츠 기획 | 지원 | 지원 |
| 자료 조사 | 지원 | 지원 |
| 출처 검증 | 지원 | 지원 |
| 초안 작성 | 지원 | 지원 |
| 편집 및 최종 원고 | 지원 | 지원 |
| OpenAI Sites 게시 | 지원 | 제외 |

> GitHub 공개본에 Codex용과 Claude Code용 듀얼 배포가 모두 반영되어 있습니다(2026-07-30). 아래 Claude 설치 명령을 그대로 사용할 수 있습니다. OpenAI Sites 게시는 Codex 배포본에만 있습니다.

---

# Codex 설치

## 4. 저장소 내려받기

터미널에서 다음 명령을 실행합니다.

```bash
git clone https://github.com/greatson79/wave-content-studio.git
cd wave-content-studio
```

## 5. 플러그인 마켓플레이스 등록

```bash
codex plugin marketplace add .
```

## 6. 플러그인 설치

```bash
codex plugin add wave-content-studio@wave-content-studio
```

설치가 끝나면 **새 Codex 작업**을 열어야 플러그인의 스킬이 정상적으로 로드됩니다.

## 7. Codex에서 시작하기

새 작업에서 다음과 같이 요청합니다.

```text
$content-studio-orchestrator를 사용해 블로그 콘텐츠 제작을 시작해줘.
각 단계 전에 내 방향을 확인하고, 결과 저장 후 검토를 기다려줘.
```

주제·독자·목적을 함께 입력하면 더 빠르게 시작할 수 있습니다.

```text
$content-studio-orchestrator를 사용해 글을 작성해줘.

주제: 소형 교회의 AI 행정 자동화
독자: 목회자와 교회 행정 담당자
목적: 반복 업무를 줄일 수 있는 실용적인 방법 소개
```

## 8. 단계별 승인과 수정

결과가 마음에 들면 자연스럽게 승인합니다.

```text
좋아, 다음 단계로 진행해.
```

```text
이대로 진행해.
```

수정이 필요하면 원하는 방향을 구체적으로 말합니다.

```text
독자를 담임목사가 아니라 교회 행정 간사로 바꿔줘.
```

```text
전문 용어를 줄이고 비전문가도 이해할 수 있게 수정해줘.
```

수정 요청이 있으면 플러그인은 다음 단계로 넘어가지 않고 현재 단계의 결과를 다시 작성합니다.

## 9. 중단한 작업 재개

기존 프로젝트 폴더를 다시 열고 다음처럼 요청합니다.

```text
$content-studio-orchestrator를 사용해
현재 workspace의 사용자 확인 상태를 읽고 이어서 진행해줘.
```

플러그인은 `workspace/pipeline-run-report.md`를 읽고 검토 대기, 수정 요청, 다음 단계 또는 게시 승인 상태를 판단합니다.

## 10. 주요 결과 파일

모든 결과는 현재 프로젝트의 `workspace/` 폴더에 저장됩니다.

```text
workspace/
├── content-brief.md
├── research-dossier.md
├── source-map.json
├── research-validation.md
├── article-draft.md
├── final-article.md
├── editorial-report.md
└── pipeline-run-report.md
```

---

# Claude Code 설치

## 11. Claude Code 지원 범위

Claude Code용 배포본에는 다음 6개 콘텐츠 스킬이 포함되어 있습니다.

- 콘텐츠 기획
- 자료 조사
- 출처 검증
- 초안 작성
- 최종 편집
- 전체 단계 오케스트레이션

Claude Code용 배포본에서는 **OpenAI Sites 게시 기능을 제외**합니다. 최종 편집 결과가 승인되면 Markdown 원고를 제공하고 `COMPLETE_NO_PUBLISH` 상태로 종료합니다.

## 12. Claude Code 설치 명령

Claude Code 안에서 다음 명령을 순서대로 실행합니다.

```text
/plugin marketplace add greatson79/wave-content-studio
/plugin install wave-content-studio-claude@wave-content-studio-claude
/reload-plugins
```

Claude Code는 GitHub 저장소에 있는 `.claude-plugin/marketplace.json`을 읽어 플러그인을 설치합니다.

## 13. Claude Code에서 시작하기

플러그인 스킬을 직접 호출합니다.

```text
/wave-content-studio-claude:content-studio-orchestrator
```

또는 다음처럼 요청합니다.

```text
/wave-content-studio-claude:content-studio-orchestrator를 사용해서
교회 리더를 위한 AI 자동화 글을 한 단계씩 작성하자.
각 결과를 저장한 뒤 내 검토를 기다려줘.
```

### Ai_works 저장소 전용 단축 명령 `/콘텐츠`

이 저장소(`~/Desktop/Ai_works`)에서는 아래 한 단어로 실행합니다.

```text
/콘텐츠
```

정본 = `.claude/commands/콘텐츠.md`. 플러그인 기본 계약과 두 가지가 다릅니다.

| 항목 | 플러그인 기본 | `/콘텐츠` |
|---|---|---|
| 산출물 위치 | 프로젝트 루트 `workspace/` | `output/WaveAI/크리에이티브본부/projects/{주제}_{날짜}/workspace/` (산출물 단일 정본 규약) |
| 시작 방식 | 입력을 받아 진행 | 인자가 있어도 확정으로 받지 않고 **주제·독자·목적을 먼저 확인** |

나머지(한 턴에 한 단계, 승인 전 진행 금지, 재개 자동 판정, `COMPLETE_NO_PUBLISH`)는 플러그인 계약과 같습니다. 이 단축 명령은 Ai_works 저장소 전용이며 플러그인 배포본에는 포함되지 않습니다.

## 14. Claude Code의 최종 결과

Claude Code에서는 최종 편집 승인 후 다음 자료를 제공합니다.

- `workspace/final-article.md`
- `workspace/editorial-report.md`
- 제목과 요약
- 추천 slug
- 카테고리·태그 제안
- 검증된 출처 목록
- 복사 가능한 Markdown 원고

Claude Code 플러그인은 OpenAI Sites를 생성하거나 게시하지 않습니다.

---

# 업데이트와 제거

## 15. 저장소 업데이트

저장소 폴더에서 다음 명령을 실행합니다.

```bash
git pull
```

Codex에서는 마켓플레이스와 플러그인을 업데이트하거나 다시 설치해야 새 버전이 반영될 수 있습니다. 업데이트 후에는 새 작업을 여는 것이 안전합니다.

Claude Code에서는 다음 명령으로 마켓플레이스를 갱신합니다.

```text
/plugin marketplace update wave-content-studio-claude
/reload-plugins
```

## 16. 보안 주의사항

- 플러그인 저장소에 API 키, 비밀번호, 토큰을 저장하지 마세요.
- 개인 블로그나 외부 서비스 인증은 각 사용자가 자신의 계정으로 진행해야 합니다.
- 외부 게시 전에는 대상 사이트, 제목, 공개 상태와 최종 원고를 반드시 확인하세요.
- 출처가 검증되지 않은 주장이나 `NEEDS_REVIEW` 상태의 자료는 최종 원고 근거로 사용하지 않습니다.

## 17. 라이선스와 문의

최신 배포 상태와 변경 내역은 [GitHub 저장소](https://github.com/greatson79/wave-content-studio)에서 확인할 수 있습니다.
