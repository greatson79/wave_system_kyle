# agent-reach CLI 복구 및 채널 계정요건 보고

## 1. 최종 결과

- CLI 복구: **완료**
- 버전: `Agent Reach v1.5.0`
- 전용 런타임: `/Users/kylechoi/.local/share/agent-reach/venv`
- PATH 진입점: `/Users/kylechoi/.local/bin/agent-reach`
- 심링크 대상: `/Users/kylechoi/.local/share/agent-reach/venv/bin/agent-reach`
- 설치 방식: 검증 wheel의 **non-editable 설치**
- `agent-reach doctor --json`: exit `0`, 유효 JSON 15채널
- 전체 테스트: `196 passed in 12.51s`
- 정본 소스 변경: 0건
- 중복 폴더 삭제·정리: 0건
- 자격증명 조회·입력: 0건

## 2. 정본 폴더 판정

| 후보 | 실측 | 판정 |
|---|---|---|
| `_workflowhome/Agent-Reach` | 유일한 실제 Git worktree, HEAD `e87bcdb`, 추적 파일 93개, 핵심 소스·테스트 완비 | **정본** |
| `개발본부/Agent-Reach` | 정본을 가리키는 심볼릭 링크, realpath 동일 | 별도 사본 아님 |
| `개발본부/Agent-Reach 2` | `/Users/kylechoi/Desktop/Ai_works/Agent-Reach`를 가리키지만 대상이 없는 끊긴 심볼릭 링크 | 비정본·정리 승인 대기 |

정본의 로컬 `origin/main` 추적값은 `e87bcdb`이고, 원격 live HEAD는 `b4d52c4`다. 로컬 정본은 upstream 최신보다 뒤처져 있으나, 이번 과제는 CLI 설치 복구이므로 pull·merge·소스 갱신을 수행하지 않았다.

## 3. 장애 원인

### 직접 원인

기존 CLI는 다음 경로를 가리켰다.

`~/.local/bin/agent-reach` → `_workflowhome/Agent-Reach/.venv/bin/agent-reach`

해당 프로젝트 venv에는 `agent-reach`가 editable로 등록돼 있었지만 `.pth`가 소스 루트가 아니라 `.../Agent-Reach/agent_reach` 자체를 넣었다. 그 결과 `import agent_reach`는 `__file__ = None`인 namespace로만 잡히고 `agent_reach.cli`를 찾지 못했다.

재현 오류:

`ModuleNotFoundError: No module named 'agent_reach.cli'`

### 재발 원인

정본 `uv.lock`은 프로젝트를 `source = { editable = "." }`로 선언한다. 따라서 프로젝트 venv를 CLI 런타임으로 계속 쓰면 해당 폴더에서 `uv sync` 또는 동기화를 포함한 `uv run`이 실행될 때 editable 설치로 되돌아간다.

실제로 첫 non-editable 복구 직후 fresh shell 검증은 통과했으나, 약 30초 뒤 uv metadata가 editable 설치를 다시 기록하면서 CLI가 재파손됐다. 실행 주체는 현재 증거로 특정하지 못했지만 다음 사실은 확인했다.

- 되돌아간 dist-info의 `INSTALLER`는 `uv`
- `RECORD`에는 `_editable_impl_agent_reach.pth`만 등록
- 실제 `agent_reach/cli.py`는 다시 사라짐

따라서 프로젝트 venv를 계속 수선하는 방식은 영구 복구가 아니다.

## 4. 영구 복구

1. 프로젝트와 분리된 전용 런타임 `~/.local/share/agent-reach/venv` 생성
2. 정본 소스에서 wheel 생성
3. wheel SHA-256 검증
4. 전용 런타임에 실제 파일을 non-editable 설치
5. `~/.local/bin/agent-reach` 심링크를 전용 런타임 CLI로 원자 교체
6. 프로젝트 소스·기존 `.venv`·세 후보 폴더는 무변경 유지

설치 wheel SHA-256:

`81e0fe27e1353092c8966d3f2d8eedcb460dde77cad57f4490c837a5ed16b74d`

전용 런타임 검증:

- `agent_reach.__file__` → 전용 venv의 `site-packages/agent_reach/__init__.py`
- `agent_reach.cli.__file__` → 전용 venv의 `site-packages/agent_reach/cli.py`
- `Editable project location` 없음
- editable `.pth` 0개
- `direct_url.json`은 wheel archive hash 기록

## 5. 안정성 검증

`/tmp` fresh shell 기준으로 `agent-reach doctor --json`을 30초 간격 2회 실행했고 모두 통과했다. 본부장 독립 3차 실행도 통과했다.

| 검증 | 결과 |
|---|---|
| `agent-reach --version` | `Agent Reach v1.5.0` |
| import 실제 파일 | PASS |
| editable artifact 부재 | PASS |
| doctor JSON 파싱 | PASS |
| 채널 수 | 15 |
| doctor 상태 | `ok 6 / warn 3 / off 6` |
| 전체 pytest | `196 passed` |
| 정본 tracked 변경 | 0건 |

증거 JSON:

- `/tmp/agent-reach-doctor-2026-07-29-pass1.json`
- `/tmp/agent-reach-doctor-2026-07-29-pass2.json`
- `/tmp/agent-reach-doctor-2026-07-29-pass3.json`

## 6. 채널별 계정·API 요구

| 채널 | 현재 상태·backend | 즉시 사용 | 주인님 연결 필요 | 계정 없이 필요한 설정 |
|---|---|---:|---|---|
| GitHub | `ok` · gh CLI | 예, 전체 기능 | 없음·현재 인증됨 | 없음 |
| Twitter/X | `warn` · twitter-cli | 아니오 | X 로그인 세션 또는 `TWITTER_AUTH_TOKEN` + `TWITTER_CT0` | 없음 |
| YouTube | `ok` · yt-dlp | 예 | 없음 | 없음 |
| Reddit | `warn` · rdt-cli | 아니오 | 브라우저 Reddit 로그인 후 `rdt login` 또는 `reddit_session` Cookie | 없음 |
| Facebook | `off` | 아니오 | Chrome Facebook 로그인 | OpenCLI·Chrome 확장 설치 |
| Instagram | `off` | 아니오 | Chrome Instagram 로그인 | OpenCLI·Chrome 확장 설치 |
| Bilibili | `ok` · 공개 검색 API | 예, 검색만 | 없음 | 전체 기능은 bili-cli, 자막은 OpenCLI 추가 |
| 小红书 | `off` | 아니오 | Chrome 로그인 또는 서버 MCP QR 로그인 | OpenCLI·확장 또는 xiaohongshu-mcp |
| LinkedIn | `off` | 제한적 공개 URL만 Jina로 가능 | 완전 기능은 LinkedIn 로그인 세션 | linkedin-scraper-mcp 설치·mcporter 등록 |
| 小宇宙 | `off` | 아니오 | 전사 기능에 Groq 무료 API 키 | 전사 스크립트 설치 |
| V2EX | `ok` · 공개 API | 예 | 없음 | 없음 |
| 雪球 | `warn` | 아니오 | Chrome 雪球 로그인 Cookie | 없음 |
| RSS | `ok` · feedparser | 예 | 없음 | 없음 |
| Exa 전역검색 | `off` | 아니오 | **계정·API 키 없음** | mcporter에 Exa URL 등록만 필요 |
| 웹 | `ok` · Jina Reader | 예 | 없음 | 없음 |

### 주인님 조치 기준

지금 바로 쓸 수 있는 채널은 6개다.

- GitHub
- YouTube
- Bilibili 공개 검색
- V2EX
- RSS
- 웹

주인님 로그인·Cookie가 필요한 채널은 다음 6개다.

- Twitter/X
- Reddit
- Facebook
- Instagram
- 小红书
- 雪球

별도 구분:

- LinkedIn: 완전 기능에 로그인 필요
- 小宇宙: 플랫폼 계정이 아니라 Groq API 키 필요
- Exa: 계정·API 키 없이 mcporter 등록만 필요

## 7. 재발 방지 규칙

1. 전역 CLI는 프로젝트 `.venv`를 직접 가리키지 않는다.
2. 설치는 정본에서 wheel을 빌드한 뒤 전용 런타임에 non-editable로 수행한다.
3. `pip install -e .`, `uv sync`, `uv run`으로 전역 CLI 런타임을 만들지 않는다.
4. 설치 후 반드시 프로젝트 밖 `/tmp` 새 셸에서 아래를 확인한다.
   - `agent_reach.__file__`이 전용 venv 실제 파일인지
   - `agent_reach.cli.__file__`이 존재하는지
   - editable `.pth`가 없는지
   - `agent-reach --version`이 정상인지
   - `agent-reach doctor --json`이 exit 0·15채널인지
5. PATH 심링크는 `~/.local/share/agent-reach/venv/bin/agent-reach`만 가리킨다.
6. 업스트림 갱신 시에도 새 wheel을 만든 뒤 전용 런타임에 교체하고 동일 검증을 반복한다.

## 8. 결정 대기

- `개발본부/Agent-Reach 2` 끊긴 심볼릭 링크 삭제 여부
- 로컬 정본을 upstream `b4d52c4`로 갱신할지 여부
- 계정 연결 대상 채널 선택
- 계정 불필요한 Exa mcporter 등록 실행 여부
