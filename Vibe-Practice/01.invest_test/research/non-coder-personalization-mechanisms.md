# Deep Research: Non-Coder User System Personalization Mechanisms

> **Role**: UX Researcher (Non-Technical User Persona Specialist)
> **Date**: 2026-03-28
> **Context**: InvestScan Scenario B (BALANCED), solo user = pastor (non-coder)
> **Constraint**: Zero coding ability. YAML editing = coding-level barrier.
> **Deliverable**: User journey analysis across "Initial Setup -> In-Use Changes -> Troubleshooting" with concrete dialogue examples

---

## Executive Summary

InvestScan의 사용자는 코드를 작성할 수 없는 목사이다. `investscan.yaml` 설정 파일은 10개 섹터 선택, 투자 성향, 관심/제외 종목, 리포트 언어/길이, Telegram bot token, Gmail app password, 실행 스케줄 등을 포함한다. 이 조사는 YAML 직접 편집 없이 시스템을 개인화하는 메커니즘을 **4가지 조사 항목** 기준으로 분석하고, "처음 설정 -> 사용 중 변경 -> 문제 해결" 3단계의 **구체적 사용자 여정**을 제시한다.

**핵심 결론**: InvestScan은 Claude Code 위에서 동작하므로, **Claude Code 자체가 최적의 설정 인터페이스**다. 별도의 CLI wizard를 만들 필요가 없다. 사용자가 자연어로 "IT 섹터만 보고 싶어"라고 말하면 Claude Code가 YAML을 수정하고 확인을 요청한다. 이 패턴은 Home Assistant Configuration Agent가 2025년에 검증한 접근법과 동일하며, InvestScan은 추가 개발 없이 이를 활용할 수 있다.

---

## 1. Non-Coder Friendly Configuration Interface Patterns

### 1.1 Available Patterns: Three Tiers

| Tier | Pattern | Examples | InvestScan Fit |
|------|---------|----------|---------------|
| **Tier 1** | Conversational AI (natural language -> config) | Home Assistant Configuration Agent, Claude Code native | **Best fit** -- zero additional development |
| **Tier 2** | Interactive CLI Wizard (guided menu) | InquirerPy, Python Click/Rich, GPT4All model picker | Moderate -- requires 200-400 LOC |
| **Tier 3** | Web GUI (browser-based form) | OpenBB Workspace, LM Studio settings | Overkill -- requires web server infrastructure |

### 1.2 Tier 1: Conversational AI Pattern (Recommended)

**Home Assistant Configuration Agent (2025)** 가 검증한 패턴: YAML 직접 편집 대신, 자연어로 원하는 것을 설명하면 AI가 기술적 세부사항을 처리한다. OpenAI Agent SDK 기반으로, 비기술 사용자가 자연어를 통해 Home Assistant의 YAML 설정을 관리할 수 있게 한다.

**InvestScan에의 적용**: Claude Code는 이미 이 역할을 수행할 수 있다. InvestScan은 Claude Code 워크플로우 안에서 실행되므로, 사용자는 이미 Claude Code와 대화하고 있다. 별도 도구가 필요 없다.

```
사용자: "다음 주부터 IT랑 헬스케어만 보고 싶어"
Claude Code: investscan.yaml의 sectors 항목을 다음과 같이 변경합니다:

  변경 전: [IT, Healthcare, Energy, Finance, Materials, ...]
  변경 후: [IT, Healthcare]

  나머지 8개 섹터(Energy, Finance, Materials, Industrials,
  Consumer, Utilities, Real Estate, Communication)는 제외됩니다.

  이렇게 변경할까요?
사용자: "응"
Claude Code: [Edit tool로 investscan.yaml 수정] 완료했습니다.
  다음 실행부터 IT와 Healthcare 섹터만 분석합니다.
```

**장점**:
- 추가 개발 비용: 0 LOC (Claude Code 내장 기능 활용)
- 학습 곡선: 0 (이미 Claude Code와 대화하는 사용자)
- 오류 방지: Claude Code가 YAML syntax 검증을 자동 수행
- 맥락 인지: Claude Code가 현재 설정을 읽고 변경의 영향을 설명 가능

**한계**:
- Claude Code 세션이 활성화되어 있어야 함 (오프라인 불가)
- API 비용 발생 (간단한 설정 변경에도 LLM 호출)

### 1.3 Tier 2: Interactive CLI Wizard Pattern (Fallback)

Claude Code 없이 독립 실행이 필요한 경우의 대안.

**InquirerPy** (Python port of Inquirer.js): 체크박스, 드롭다운, 텍스트 입력 등을 제공하는 인터랙티브 CLI 라이브러리. prompt_toolkit 기반으로 macOS에서 안정적으로 동작한다.

```python
# 예시 코드 (실제 구현 아님 -- 패턴 참조용)
from InquirerPy import inquirer

sectors = inquirer.checkbox(
    message="분석할 섹터를 선택하세요 (Space로 선택, Enter로 확인):",
    choices=["IT", "Healthcare", "Energy", "Finance", "Materials",
             "Industrials", "Consumer", "Utilities", "Real Estate",
             "Communication"],
    default=["IT", "Healthcare", "Energy", "Finance"],
).execute()

style = inquirer.select(
    message="투자 성향을 선택하세요:",
    choices=["공격적 (높은 변동성 수용)", "보수적 (안정성 우선)"],
).execute()
```

**비코더 사용자 경험**:
- 터미널에서 `investscan setup` 실행
- 화살표 키 + Space 바로 선택
- 텍스트 직접 입력은 종목 이름 정도만
- 완료 시 YAML 자동 생성

**개발 비용**: ~200-400 LOC, InquirerPy + PyYAML 의존성
**적합 시나리오**: Claude Code 없이 독립 실행 가능한 설정 도구가 필요한 경우

### 1.4 Tier 3: Web GUI Pattern (Not Recommended)

OpenBB는 비기술 사용자를 위해 **OpenBB Workspace**라는 별도 웹 GUI를 제공하지만, 이는 기업 규모의 투자이다. LM Studio는 GUI-first 접근으로 비기술 사용자에게 강점을 보이지만, InvestScan에서 Streamlit/Gradio 기반 설정 페이지를 만드는 것은 과잉 엔지니어링이다.

**결론**: InvestScan은 Tier 1 (Claude Code 대화형)을 기본으로, Tier 2 (CLI wizard)를 선택적 fallback으로 설계하는 것이 최적이다.

---

## 2. Similar Local AI Tool Configuration UX Cases

### 2.1 OpenBB Terminal (25,000+ GitHub stars)

**설정 방식**: `~/.openbb_platform/user_settings.json`에 API 키를 직접 입력하거나, Python 코드로 `obb.user.credentials.fred_api_key = "..."` 형태로 설정. 비기술 사용자를 위해서는 별도의 **OpenBB Workspace** (엔터프라이즈 웹 UI)를 제공한다.

**InvestScan 시사점**: OpenBB조차 CLI만으로는 비기술 사용자를 만족시키지 못해 별도 GUI를 만들었다. 그러나 InvestScan은 Claude Code라는 자연어 인터페이스가 이미 존재하므로, 별도 GUI 없이 동일한 접근성을 달성할 수 있다.

### 2.2 LM Studio (GUI-First Approach)

**설정 방식**: 데스크톱 앱 내에서 모든 설정을 GUI로 처리. 모델 다운로드, 파라미터 조정, 서버 설정 등이 모두 클릭/드래그로 가능하다. "커맨드 라인 없이 로컬 AI를 사용하고 싶은 사람에게 최적"이라는 평가를 받는다.

**InvestScan 시사점**: LM Studio의 성공은 "비기술 사용자는 텍스트 편집이 아니라 선택(selection)을 원한다"는 원칙을 보여준다. Claude Code 대화에서도 선택지를 제시하는 패턴이 중요하다.

### 2.3 GPT4All (Zero-Decision Onboarding)

**설정 방식**: "모든 결정 지점을 제거"하는 접근. 양자화 수준을 선택하지 않고, GGUF 파일을 관리하지 않고, 앱을 다운받아 큐레이션된 모델 목록에서 고르면 바로 시작. 커뮤니티 평점과 사람이 읽을 수 있는 설명이 포함된다.

**InvestScan 시사점**: 초기 설정에서 결정의 수를 최소화해야 한다. 10개 섹터 전부 선택하게 하는 대신, "기본 추천 프리셋"을 제공하고 나중에 조정하도록 유도.

### 2.4 Jan AI (ChatGPT-Style Desktop)

**설정 방식**: ChatGPT 스타일의 데스크톱 인터페이스로, 2026년 현재 MCP(Model Context Protocol)를 지원하여 로컬 파일/데이터베이스에 직접 연결 가능. 설정은 앱 내 GUI에서 처리.

### 2.5 Pattern Synthesis: What Works for Non-Coders

| Pattern | Tools Using It | Non-Coder Effectiveness |
|---------|---------------|------------------------|
| Zero-decision defaults + later customization | GPT4All, LM Studio | **Highest** -- 사용자가 즉시 시작 가능 |
| Curated presets with descriptions | GPT4All 모델 선택 | **High** -- 선택은 하되 복잡성 최소화 |
| Natural language configuration | Home Assistant Agent, Claude Code | **High** -- 기술 용어 회피 |
| GUI with visual feedback | LM Studio, OpenBB Workspace | **Medium-High** -- 개발 비용이 높음 |
| JSON/YAML direct editing | OpenBB, Ollama advanced config | **Low** -- 비코더에게는 코딩과 동일 |

---

## 3. Credential Management (Non-Coder Perspective)

### 3.1 Three Credentials InvestScan Needs

| Credential | Purpose | Sensitivity | Rotation Frequency |
|-----------|---------|-------------|-------------------|
| Telegram Bot Token | 리포트 전송 | Medium -- 봇 제어 가능 | 거의 없음 (분실 시만) |
| Gmail App Password | 이메일 리포트 발송 | **High** -- 이메일 접근 가능 | 분실/의심 시만 |
| (Future) API Keys | Claude API, 데이터 소스 등 | **High** -- 비용 발생 | 정기적 권장 |

### 3.2 Storage Options Comparison

| Method | Security | Non-Coder Friendliness | InvestScan Fit |
|--------|----------|----------------------|---------------|
| **macOS Keychain** (via `keyring` library) | **Best** -- OS-level 암호화, Touch ID/비밀번호 보호 | **Medium** -- 저장은 쉽지만 개념이 생소할 수 있음 | **Recommended** |
| `.env` file (python-dotenv) | **Low** -- plaintext, 파일 접근만으로 노출 | **Medium** -- 파일 하나에 모아둬서 직관적 | Fallback only |
| `investscan.yaml` 내 직접 저장 | **Worst** -- git commit 시 유출 위험 | **Highest** -- 하나의 파일에 모든 설정 | **Never** |
| Encrypted config (cryptography library) | **High** -- 파일 암호화 | **Low** -- 암호화 키 관리 부담 | Not suitable |

### 3.3 macOS Keychain Integration: The Recommended Approach

Python `keyring` 라이브러리는 macOS Keychain과 네이티브로 통합된다.

**사용자 경험 흐름**:

```
사용자: "텔레그램 봇 토큰 설정해줘"
Claude Code: 텔레그램 봇 토큰을 macOS 키체인에 안전하게 저장하겠습니다.

  토큰을 알려주시면 키체인에 저장합니다.
  (터미널 화면에 잠깐 보이지만 파일로 저장되지 않습니다)

  아직 텔레그램 봇이 없으시면, 만드는 과정을 안내해드릴까요?
사용자: "봇이 없어. 만드는 거부터 알려줘"
Claude Code: 텔레그램 봇 만들기 (3분 소요):

  1. 휴대폰에서 텔레그램 앱을 엽니다
  2. 검색창에 @BotFather 를 입력합니다 (파란 체크마크 확인)
  3. BotFather와 대화를 시작하고 /newbot 을 입력합니다
  4. 봇 이름을 입력합니다 (예: "나의 투자리포트")
  5. 봇 사용자명을 입력합니다 (예: "my_invest_report_bot")
     - 반드시 "bot"으로 끝나야 합니다
  6. BotFather가 API 토큰을 보내줍니다
     예시: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz

  이 토큰을 복사해서 여기에 붙여넣어 주세요.
사용자: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
Claude Code: [keyring.set_password("investscan", "telegram_bot_token", token)]

  토큰을 macOS 키체인에 저장했습니다.
  - 저장 위치: macOS 키체인 (Keychain Access 앱에서 확인 가능)
  - 암호화: macOS가 자동으로 암호화합니다
  - investscan.yaml에는 토큰 대신 "use_keychain: true"만 기록됩니다

  다음으로 봇과 대화방을 연결해야 합니다.
  텔레그램에서 방금 만든 봇을 검색해서 /start 를 눌러주세요.
  누르셨으면 알려주세요.
```

**기술적 구현**:
- `keyring` 라이브러리는 macOS에서 자동으로 Keychain backend를 사용
- `keyring.set_password("investscan", "telegram_bot_token", value)` 한 줄로 저장
- `keyring.get_password("investscan", "telegram_bot_token")`으로 런타임에 조회
- investscan.yaml에는 `credentials: source: keychain`만 기록 (토큰 자체는 없음)

### 3.4 Gmail App Password: Step-by-Step Guided Flow

Gmail App Password는 비기술 사용자에게 특히 어려운 과정이다. 2단계 인증 활성화가 선행 조건이기 때문이다.

```
사용자: "Gmail로 리포트 받고 싶어"
Claude Code: Gmail 이메일 발송을 설정하겠습니다. 3단계가 필요합니다.

  [1단계] 2단계 인증 확인
  Google 계정에 2단계 인증이 켜져 있어야 합니다.

  확인 방법:
  1. 브라우저에서 myaccount.google.com 접속
  2. "보안" 탭 클릭
  3. "2단계 인증"이 "사용" 상태인지 확인

  켜져 있나요?
사용자: "아직 안 켜져 있어"
Claude Code: 2단계 인증을 먼저 켜겠습니다.

  1. myaccount.google.com -> 보안 -> 2단계 인증 -> "시작하기"
  2. 비밀번호 입력
  3. 휴대폰 번호 입력 -> 문자로 코드 받기
  4. 받은 코드 입력 -> "사용 설정" 클릭

  완료되면 알려주세요.
사용자: "됐어"
Claude Code: [2단계] 앱 비밀번호 생성

  1. myaccount.google.com -> 보안 -> "앱 비밀번호" 검색
     (또는 직접 URL: myaccount.google.com/apppasswords)
  2. 앱 이름에 "InvestScan" 입력
  3. "만들기" 클릭
  4. 16자리 비밀번호가 표시됩니다 (예: abcd efgh ijkl mnop)

  이 16자리를 공백 없이 복사해서 알려주세요.
사용자: "abcdefghijklmnop"
Claude Code: [keyring.set_password("investscan", "gmail_app_password", password)]

  Gmail 앱 비밀번호를 macOS 키체인에 저장했습니다.

  [3단계] 발송 이메일 주소 설정
  리포트를 보낼 Gmail 주소를 알려주세요.
사용자: "pastor.kim@gmail.com"
Claude Code: [investscan.yaml 수정]

  설정 완료:
  - 발신: pastor.kim@gmail.com (앱 비밀번호 = 키체인에 저장)
  - 수신: pastor.kim@gmail.com (본인에게 발송)

  수신 주소를 다른 곳으로 바꾸고 싶으시면 말씀해 주세요.
```

### 3.5 Credential Storage Decision Matrix

| Criterion | .env | Keychain | YAML Direct |
|-----------|------|----------|-------------|
| Git leak risk | Medium (.gitignore 필수) | **None** | **Critical** |
| macOS native encryption | No | **Yes** | No |
| Touch ID / password protection | No | **Yes** | No |
| Claude Code integration ease | Easy | Easy (`keyring` lib) | Easiest but dangerous |
| Offline access without Claude | Easy | Easy | Easy |
| Backup/migration | Copy file | Export keychain | Copy file |

**최종 권장**: macOS Keychain (`keyring` 라이브러리) 사용. investscan.yaml에는 `credentials.source: keychain`만 기록. Fallback으로 `.env` 지원 (CI/자동화 환경용).

---

## 4. Configuration Change Reflection Mechanism

### 4.1 "Next Week, IT Only" -- Change Flow via Claude Code

**설정 변경의 두 가지 경로**:

| 경로 | 트리거 | 적합 상황 |
|------|--------|----------|
| **A. Claude Code 대화** | 사용자가 자연어로 요청 | 모든 일반적 변경 |
| **B. CLI 명령** | `investscan config set sectors IT,Healthcare` | Claude Code 세션 없이 빠른 변경 |

**경로 A 상세 흐름**:

```
사용자: "다음 주부터 IT만 봐줘"
Claude Code: investscan.yaml의 sectors를 변경하겠습니다.

  현재 설정: [IT, Healthcare, Energy, Finance, Materials, Industrials,
             Consumer, Utilities, Real Estate, Communication]
  변경 후:   [IT]

  7개 섹터가 제외됩니다. 이렇게 하면 리포트에 IT 관련 시그널만
  포함되어 다른 섹터의 중요한 변화를 놓칠 수 있습니다.

  진행할까요?
사용자: "응 IT만 보면 돼"
Claude Code: [Edit investscan.yaml: sectors: [IT]]
  변경 완료. 변경 이력을 config-history에 기록했습니다.
  다음 investscan run 실행 시 IT 섹터만 분석합니다.
```

### 4.2 Hot Reload vs. Restart

**InvestScan의 실행 특성**:
- 주간 배치 실행 (weekly batch) -- 실시간 서비스가 아님
- `investscan run` 실행 시마다 YAML 파일을 새로 읽음
- 따라서 **hot reload가 필요 없음** -- 다음 실행 시 자동 반영

**결론**: 설정 변경 후 재시작이 필요하지 않다. 다음 `investscan run` 시 자동 반영된다. 이 점을 사용자에게 명시적으로 알려주는 것이 중요하다.

```
Claude Code: 설정을 변경했습니다.
  다음에 investscan run을 실행하면 자동으로 적용됩니다.
  지금 바로 실행해볼까요, 아니면 다음 예정된 실행 때 적용할까요?
```

만약 향후 launchd 스케줄 실행이 추가되면:
- YAML 변경 -> 다음 예약 실행 시 자동 반영 (재시작 불필요)
- 스케줄 자체를 변경하는 경우만 launchd plist 재로드 필요

### 4.3 "Undo" / Configuration History

**비코더 사용자가 "원래대로 돌려줘"라고 할 때의 메커니즘**:

#### 4.3.1 Git-Based History (Already Available)

InvestScan 프로젝트가 Git 레포지토리 안에 있으므로, investscan.yaml의 모든 변경 이력이 Git에 자동 기록된다. Claude Code는 Git 히스토리를 읽을 수 있다.

```
사용자: "설정 원래대로 돌려줘"
Claude Code: investscan.yaml의 최근 변경 이력입니다:

  [3일 전] sectors: 전체 10개 -> IT만
  [1주 전] style: conservative -> aggressive
  [2주 전] exclude_tickers: [] -> [삼성전자]

  어떤 시점으로 돌릴까요?
  1) 3일 전 (섹터 변경 전)
  2) 1주 전 (투자 성향 변경 전)
  3) 2주 전 (제외 종목 추가 전)
  4) 처음 상태 (기본값)
사용자: "1번"
Claude Code: [git show로 이전 버전 확인 -> Edit로 복원]

  3일 전 상태로 복원했습니다:
  - sectors: [IT, Healthcare, Energy, Finance, Materials, Industrials,
              Consumer, Utilities, Real Estate, Communication]
  - 나머지 설정은 현재와 동일합니다.
```

#### 4.3.2 Dedicated Config History (Lightweight Alternative)

Git에 의존하지 않는 독립적 방법으로, 설정 변경 시마다 타임스탬프 백업을 생성:

```
~/.investscan/
  config.yaml              <- 현재 설정 (SOT)
  config-history/
    2026-03-21_config.yaml <- 변경 전 스냅샷
    2026-03-25_config.yaml
    2026-03-28_config.yaml
```

**개발 비용**: ~30-50 LOC (변경 전 복사 + 타임스탬프 명명)
**비코더 경험**: "원래대로"가 항상 가능하다는 심리적 안전감 제공

#### 4.3.3 Recommended: Git + 변경 확인 프롬프트

**두 겹의 안전장치**:

1. **변경 전 확인 프롬프트** (방어 1선): Claude Code가 항상 변경 전후 diff를 보여주고 확인을 요청
2. **Git 이력** (방어 2선): 모든 변경이 자동 기록되어 어느 시점이든 복원 가능

추가 전용 히스토리 시스템은 과잉이다. Git이 이미 완벽한 이력 관리를 제공한다.

---

## 5. Complete User Journey: Three Stages

### Stage 1: Initial Setup (첫 설정)

**사용자 컨텍스트**: Claude Code를 처음 열고 InvestScan을 설정하려는 목사. 터미널은 사용할 수 있지만 YAML/JSON 편집은 불가.

#### Step 1.1: Minimal Viable Setup (5분)

```
사용자: "InvestScan 처음 설정해야 해"
Claude Code: InvestScan 초기 설정을 시작하겠습니다.
  몇 가지만 여쭤볼게요.

  1. 어떤 분야에 관심이 있으세요?
     a) 전체 (10개 섹터 모두 분석)  <- 추천
     b) 기술/IT 중심 (IT, Communication)
     c) 직접 선택할게요

사용자: "a"
Claude Code: 전체 섹터를 분석하도록 설정합니다.

  2. 투자 성향은 어떤 편이세요?
     a) 보수적 (안정적인 방향성 위주)  <- 추천
     b) 공격적 (변동성 높은 기회도 포착)

사용자: "a"
Claude Code: 보수적 성향으로 설정합니다.

  3. 리포트는 어떻게 받고 싶으세요?
     a) 화면에서 바로 읽기 (추가 설정 없음)  <- 추천
     b) 텔레그램으로 받기 (봇 설정 필요, ~5분)
     c) 이메일로 받기 (Gmail 설정 필요, ~10분)

사용자: "a"
Claude Code: [investscan.yaml 생성]

  기본 설정이 완료되었습니다!

  생성된 설정:
  - 분석 섹터: 전체 10개
  - 투자 성향: 보수적
  - 리포트 언어: 한국어
  - 리포트 길이: 표준 (2,000-5,000자)
  - 알림: 화면 출력만

  investscan run 으로 첫 실행을 해볼까요?
  (텔레그램/이메일 알림은 나중에 언제든 추가할 수 있습니다)
```

**설계 원칙** (GPT4All의 "Zero-Decision Onboarding"에서 차용):
- 질문은 최대 3개 (P4 규칙: 최대 4개 질문)
- 각 질문에 "추천" 선택지를 표시
- 고급 설정(종목 필터, 스케줄 등)은 첫 설정에서 묻지 않음
- "나중에 변경 가능"을 명시적으로 안내

#### Step 1.2: Credential Setup (필요 시, 5-10분)

텔레그램/이메일을 선택한 경우에만 진행. Section 3.3, 3.4의 가이드 흐름을 따른다.

**핵심**: 자격증명 설정이 초기 설정의 필수 단계가 아니다. 리포트를 먼저 화면에서 확인하고, 가치를 체감한 후 알림 채널을 추가하는 것이 사용자 이탈을 방지한다.

### Stage 2: In-Use Changes (사용 중 변경)

**사용자 컨텍스트**: 4주간 InvestScan을 사용하고 나서, 분석 범위를 조정하거나 새로운 기능을 추가하고 싶어짐.

#### Scenario 2.1: Sector Adjustment

```
사용자: "에너지 섹터가 요즘 관심 없어. 빼줘"
Claude Code: sectors에서 Energy를 제거하겠습니다.

  변경 전: [IT, Healthcare, Energy, Finance, Materials, Industrials,
           Consumer, Utilities, Real Estate, Communication]
  변경 후: [IT, Healthcare, Finance, Materials, Industrials,
           Consumer, Utilities, Real Estate, Communication]

  Energy 섹터의 시그널은 다음 리포트부터 제외됩니다.
  변경할까요?
사용자: "응"
Claude Code: 완료. 다음 실행부터 적용됩니다.
```

#### Scenario 2.2: Add Specific Stock Interest

```
사용자: "삼성전자랑 SK하이닉스 관련 뉴스는 특별히 주목해줘"
Claude Code: 관심 종목에 삼성전자와 SK하이닉스를 추가하겠습니다.

  이 종목들 관련 시그널은 리포트에서 별도 섹션으로 강조됩니다.
  기존 섹터 분석은 그대로 유지됩니다.

  추가할까요?
사용자: "응"
Claude Code: [Edit investscan.yaml: watch_tickers 추가]
  완료. 다음 리포트에 "관심 종목 동향" 섹션이 추가됩니다.
```

#### Scenario 2.3: Add Telegram Notification (Deferred from Initial Setup)

```
사용자: "이제 텔레그램으로 리포트 받고 싶어"
Claude Code: 텔레그램 알림을 설정하겠습니다.
  텔레그램 봇이 이미 있으신가요, 아니면 새로 만들어야 하나요?
사용자: "새로 만들어야 해"
Claude Code: [Section 3.3의 단계별 안내 흐름 실행]
```

#### Scenario 2.4: Change Investment Style

```
사용자: "요즘 시장이 좋으니까 좀 더 공격적으로 분석해줘"
Claude Code: 투자 성향을 '보수적'에서 '공격적'으로 변경합니다.

  변경 효과:
  - 변동성 높은 섹터/시그널도 리포트에 포함
  - 약한 시그널(L1-L2)도 기회로 분석
  - 리스크 레이더에서 경고 임계값 상향

  "시장이 좋을 때"의 성향 변경은 흔한 패턴이지만,
  시장 반전 시 복원을 잊기 쉽습니다.
  1개월 후 "보수적으로 돌아갈까요?" 리마인더를 설정할까요?
사용자: "그래 리마인더 설정해줘"
Claude Code: [config 변경 + reminder 날짜 기록]
  완료. 4주 후(2026-04-25) 리포트에 성향 복원 리마인더가 포함됩니다.
```

### Stage 3: Troubleshooting (문제 해결)

**사용자 컨텍스트**: 설정이 꼬이거나 예상과 다른 결과가 나올 때.

#### Scenario 3.1: "Something's Wrong with the Report"

```
사용자: "리포트에 IT 시그널이 하나도 없어"
Claude Code: 현재 설정을 확인하겠습니다.

  [investscan.yaml 읽기]

  원인을 찾았습니다:
  exclude_tickers에 IT 관련 주요 종목들이 포함되어 있습니다:
  - 삼성전자, SK하이닉스, 네이버, 카카오

  2주 전(3월 14일)에 이 종목들을 제외 목록에 추가하셨습니다.
  이 제외 설정을 해제하면 IT 시그널이 다시 포함됩니다.

  해제할까요?
사용자: "아 맞다 그때 잠깐 빼놓은 거였어. 해제해줘"
Claude Code: [제외 목록에서 4개 종목 제거]
  완료. 다음 실행부터 IT 시그널이 다시 포함됩니다.
```

#### Scenario 3.2: "Reset Everything"

```
사용자: "설정이 너무 복잡해졌어. 처음부터 다시 하고 싶어"
Claude Code: 두 가지 방법이 있습니다:

  1) 기본값으로 초기화 (모든 설정을 처음 상태로)
  2) 특정 시점으로 복원 (최근 변경 이력에서 선택)

  변경 이력:
  - 3월 28일: 투자 성향 공격적으로 변경
  - 3월 25일: Energy 섹터 제외
  - 3월 21일: 관심 종목 추가 (삼성전자, SK하이닉스)
  - 3월 14일: 제외 종목 추가
  - 3월 7일: 초기 설정 완료

  어떻게 할까요?
사용자: "1번. 처음부터"
Claude Code: 현재 설정을 백업하고 기본값으로 초기화합니다.

  [기존 config -> config-history/2026-03-28_config.yaml 백업]
  [기본 config 생성]

  초기화 완료. 처음 설정할 때처럼 몇 가지 여쭤볼까요?
사용자: "응"
Claude Code: [Stage 1의 초기 설정 흐름 재실행]
```

#### Scenario 3.3: Telegram/Gmail Credential Issues

```
사용자: "텔레그램 알림이 안 와"
Claude Code: 텔레그램 설정을 진단하겠습니다.

  [1] 봇 토큰 확인: 키체인에 저장된 토큰 존재 확인
  [2] 봇 활성 상태: Telegram API로 getMe 호출
  [3] 채팅 ID 확인: 대화방 연결 상태 확인

  진단 결과:
  - 봇 토큰: 유효 (키체인에 저장됨)
  - 봇 상태: 활성
  - 채팅 ID: 없음 <- 문제 발견

  봇과 대화방이 연결되지 않았습니다.
  텔레그램에서 봇을 검색해서 /start 를 눌러주세요.
  누르셨으면 알려주세요.
사용자: "눌렀어"
Claude Code: [chat_id 자동 감지 및 저장]
  채팅 연결 완료. 테스트 메시지를 보내볼까요?
사용자: "응"
Claude Code: [테스트 메시지 발송]
  "InvestScan 테스트 메시지입니다" -- 텔레그램에서 받으셨나요?
사용자: "왔어!"
Claude Code: 텔레그램 알림 설정이 정상 작동합니다.
```

---

## 6. Implementation Recommendations for InvestScan

### 6.1 Development Priority

| Priority | Feature | LOC Estimate | Rationale |
|----------|---------|-------------|-----------|
| **P0 (M1)** | investscan.yaml 기본 구조 + 기본값 프리셋 | 50 LOC | 모든 설정의 기반 |
| **P0 (M1)** | Claude Code 대화형 초기 설정 흐름 | 0 LOC (대화 패턴만) | Claude Code 내장 기능 활용 |
| **P1 (M1)** | `keyring` 통합 (Telegram token, Gmail password) | 30 LOC | 자격증명 보안 |
| **P1 (M2)** | Config validation (YAML 파싱 + 필수값 검증) | 80 LOC | 잘못된 설정 조기 발견 |
| **P2 (M2)** | `investscan config show` (현재 설정 표시) | 30 LOC | 진단용 |
| **P2 (M3)** | CLI wizard fallback (`investscan setup`) | 200 LOC | Claude Code 없이도 설정 가능 |
| **P3 (M3)** | Config history snapshots | 50 LOC | "원래대로" 기능 보험 |

**총 추가 개발 비용**: ~440 LOC (M1-M3 전체), 이 중 M1 필수는 ~80 LOC

### 6.2 investscan.yaml Recommended Structure

```yaml
# InvestScan Configuration
# 이 파일은 Claude Code 대화로 자동 관리됩니다.
# 직접 편집하셔도 되지만, "investscan 설정 변경해줘"라고
# Claude Code에 말씀하시면 더 쉽습니다.

# --- 분석 설정 ---
sectors:                    # 분석할 섹터 (10개 중 선택)
  - IT
  - Healthcare
  - Energy
  - Finance
  - Materials
  - Industrials
  - Consumer
  - Utilities
  - Real_Estate
  - Communication

investment_style: conservative  # conservative | aggressive

watch_tickers: []           # 관심 종목 (별도 섹션으로 강조)
exclude_tickers: []         # 제외 종목

# --- 리포트 설정 ---
report:
  language: ko              # ko | en
  length: standard          # brief | standard | detailed
  format: markdown          # markdown | html (future)

# --- 알림 설정 ---
notifications:
  telegram:
    enabled: false
    # token은 macOS 키체인에 저장 (keyring: investscan/telegram_bot_token)
    chat_id: ""
  email:
    enabled: false
    sender: ""
    recipient: ""
    # app_password는 macOS 키체인에 저장 (keyring: investscan/gmail_app_password)

# --- 실행 설정 ---
schedule:
  enabled: false
  cron: "0 20 * * 0"       # 매주 일요일 오후 8시 (기본값)

# --- 자격증명 ---
credentials:
  source: keychain          # keychain | env | manual
```

### 6.3 Core Design Principles

1. **Claude Code = Primary Interface**: YAML은 내부 표현(internal representation)이다. 사용자가 직접 편집할 필요가 없다. Claude Code가 모든 변경을 중재한다.

2. **Sensible Defaults First**: 초기 설정에서 질문 최소화. GPT4All의 "Zero-Decision Onboarding" 패턴 적용. 고급 설정은 사용자가 필요를 느낄 때 추가.

3. **Credentials Never in Config**: 토큰, 패스워드는 반드시 macOS Keychain에 저장. YAML 파일에는 참조(pointer)만 기록. git push 시 유출 불가.

4. **Change Confirmation Always**: Claude Code가 설정 변경 시 반드시 변경 전후 diff를 보여주고 확인을 요청. "실수로 전체 섹터를 삭제"하는 사고 방지.

5. **Next-Run Reflection**: 주간 배치 특성상 hot reload 불필요. "다음 실행 시 자동 적용"을 명확히 안내.

6. **History via Git**: 별도 버전 관리 시스템 불필요. Git이 이미 완벽한 설정 이력을 제공. Claude Code가 `git log --follow investscan.yaml`로 이력 조회 가능.

---

## 7. Reference Cases Summary

| Case | Key Insight for InvestScan |
|------|---------------------------|
| **Home Assistant Configuration Agent** | AI가 자연어로 YAML을 관리하는 패턴이 2025년에 이미 검증됨 |
| **GPT4All** | "Zero-Decision Onboarding" -- 초기 설정 질문 최소화 |
| **LM Studio** | 비기술 사용자는 "텍스트 편집"이 아닌 "선택(selection)"을 원함 |
| **OpenBB** | CLI만으로는 부족해서 별도 GUI를 만듦 -> Claude Code가 이 역할 대체 |
| **Python keyring** | macOS Keychain과 3줄의 코드로 통합 가능 |
| **Telegram BotFather** | 단계별 안내로 비기술 사용자도 5분 안에 봇 생성 가능 |

---

## Sources

- [InquirerPy Documentation](https://inquirerpy.readthedocs.io/en/latest/)
- [InquirerPy GitHub](https://github.com/kazhala/InquirerPy)
- [Building Modern CLI with Python](https://www.zuhaibahmad.com/building-cli-with-python/)
- [OpenBB Financial Analysis Guide](https://dasroot.net/posts/2026/02/openbb-financial-analysis-python-data-retrieval/)
- [OpenBB Documentation](https://docs.openbb.co/)
- [OpenBB GitHub](https://github.com/OpenBB-finance/OpenBB)
- [Home Assistant Configuration Agent](https://community.home-assistant.io/t/introducing-ha-configuration-agent-ai-powered-home-assistant-configuration-assistant-with-approval-workflow/944620)
- [AI Agent HA](https://github.com/sbenodiz/ai_agent_ha)
- [Home Assistant AI Blog](https://www.home-assistant.io/blog/2025/09/11/ai-in-home-assistant/)
- [Ollama vs LM Studio vs GPT4All 2026 Comparison](https://dasroot.net/posts/2026/03/ollama-lm-studio-gpt4all-local-llm-comparison-2026/)
- [Run AI Locally 2026](https://yuv.ai/learn/local-ai)
- [GPT4All Official](https://gpt4all.io/index.html)
- [Python keyring PyPI](https://pypi.org/project/keyring/)
- [Keychain Access Python](https://github.com/max-muoto/keychain-access)
- [Securely Storing Credentials with Keyring](https://medium.com/@forsytheryan/securely-storing-credentials-in-python-with-keyring-d8972c3bd25f)
- [Password Management in Python](https://medium.com/@aarhar/password-management-in-python-keyring-and-credential-manager-29fa4ccc919e)
- [Secure Credentials Best Practices](https://systemweakness.com/securing-sensitive-data-in-python-best-practices-for-storing-api-keys-and-credentials-2bee9ede57ee)
- [Python Secrets Management](https://blog.gitguardian.com/how-to-handle-secrets-in-python/)
- [Telegram Bot Tutorial](https://core.telegram.org/bots/tutorial)
- [Telegram Bot Creation Guide 2026](https://anthemcreation.com/en/artificial-intelligence/create-bot-telegram-complete-guide/)
- [Telegram Bot for Beginners 2026](https://telegram-group.com/en/blog/telegram-bot-creation-for-beginners-complete-guide-2026/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833?hl=en)
- [Gmail 2-Step Verification](https://support.google.com/accounts/answer/185839?hl=en&co=GENIE.Platform%3DDesktop)
- [Config Hot Reload in Python](https://oneuptime.com/blog/post/2026-01-22-config-hot-reload-python/view)
- [Configuration Hot-Reload Pattern](https://oneuptime.com/blog/post/2025-12-11-configuration-hot-reload/view)
- [Investment Platform UI/UX Best Practices](https://rondesignlab.com/blog/design-news/most-sucessful-practices-for-investment-platform-ui-ux)
- [Personal Finance Apps 2025 Review](https://bountisphere.com/blog/personal-finance-apps-2025-review)
- [Claude Code Settings Documentation](https://code.claude.com/docs/en/settings)
