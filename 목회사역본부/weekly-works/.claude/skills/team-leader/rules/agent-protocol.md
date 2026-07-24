# Agent Protocol — 서브에이전트 소환 규칙

Team Leader가 Agent 도구로 서브에이전트를 소환할 때 사용하는 3가지 패턴.
모든 에이전트 정의는 `agent-registry.md`에서 조회한다.

---

## 공통 소환 절차

```
1. agent-registry.md에서 ID로 에이전트 조회
2. Read(source) → 에이전트 정의(SKILL.md 또는 agent .md) 로드
3. type 확인:
   - auto / research → Agent(prompt, run_in_background=true)
   - interactive → 메인 대화에서 직접 해당 SKILL로 역할 전환
4. 완료 시 output 경로에서 결과 확인
5. status.md 업데이트
```

---

## 패턴 A: 자동 에이전트 (auto type)

매일묵상, 기도카드, 소그룹나눔지, 카드뉴스 등 대화 없이 자동 완료되는 작업.

### 프롬프트 구성

```
Agent(
  prompt = """
  [SKILL.md 전문 — Read로 로드한 내용]

  ## 작업 지시
  - 프로젝트 루트: {weekly_works_path}
  - 주차: {week_number}주차
  - 출력 경로: {output_path}/{작업폴더}/
  - [입력 데이터가 있으면 여기에 포함]

  위 SKILL의 모든 규칙을 준수하여 산출물을 생성하라.
  완료 시 생성된 파일 목록을 보고하라.
  """,
  run_in_background = true,
  description = "{에이전트명} {간단 설명}"
)
```

### 핵심 규칙

- SKILL.md **전문**을 프롬프트에 포함한다 (참조가 아닌 주입)
- 출력 경로를 **절대적으로** 지정한다 (에이전트가 추측하지 않도록)
- 입력 데이터(JSON, CSV 내용 등)가 있으면 프롬프트에 직접 포함한다
- `run_in_background = true`로 메인 대화를 차단하지 않는다

### 예시: 매일묵상 (WK-B)

```
skill_content = Read(".claude/skills/weekly-devotion/SKILL.md")
devotion_data = Read(".claude/skills/weekly-devotion/devotion-data.json")

Agent(
  prompt = f"""
  {skill_content}

  ## 작업 지시
  - 프로젝트 루트: {weekly_works_path}
  - 주차: {week_number}주차
  - 출력 경로: {output_path}/매일묵상/
  - devotion-data.json 내용:
  {devotion_data}

  위 SKILL의 모든 규칙을 준수하여 15개 HTML 파일을 생성하라.
  완료 시 생성된 파일 목록을 보고하라.
  """,
  run_in_background = True,
  description = "매일묵상 15개 HTML 생성"
)
```

---

## 패턴 B: 크로스 폴더 연구 에이전트 (research type)

Sermon-Assistant 11개 에이전트처럼, **다른 프로젝트에 정의된** 에이전트를 소환하는 패턴.

### 프롬프트 구성

```
Agent(
  prompt = """
  [에이전트 정의 .md 전문 — Read로 로드]

  ## 분석 대상
  본문: {scripture} (예: 이사야 53:1-6)

  ## 출력 규칙 (GRA-Lite)
  - 모든 주장에 출처를 명시하라 (학자명, 사전명, 페이지)
  - "모든 학자가 동의" 같은 절대적 표현 금지
  - 확신도가 낮은 주장은 "likely", "possibly" 등으로 표현
  - 최종 결과를 한국어로 작성하되, 원어(히/헬)와 학술 용어는 원문 유지

  ## 출력 형식
  마크다운으로 다음 구조:
  1. 요약 (3-5문장)
  2. 상세 분석 (에이전트 Tasks 순서대로)
  3. 설교 적용 제안 (2-3개)

  ## 저장
  결과를 {output_path}/설교/research/{파일명} 에 저장하라.
  """,
  run_in_background = true,
  description = "@{에이전트명} {본문} 분석"
)
```

### 핵심 규칙

- 에이전트 정의 파일(.md)을 **절대 경로**로 Read하여 프롬프트에 주입
- **GRA-Lite 규칙**을 항상 포함 (환각 방지)
- 출력 파일명은 `agent-registry.md`의 output 컬럼을 따른다
- 에이전트 정의가 변경되면 다음 소환 시 자동으로 최신 버전 반영

### 소스 경로 해석

agent-registry.md의 Sermon-Assistant 소스 경로는 기본 경로 이하의 상대경로이다.
소환 시 절대 경로로 조합:

```
기본 경로: /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main/.claude/agents/
파일: original-text-analyst.md
→ 절대 경로: {기본 경로}/original-text-analyst.md
```

---

## 패턴 C: 의존성 있는 순차 에이전트

선행 에이전트의 결과를 입력으로 필요로 하는 에이전트. 대표적으로 SA-11 수사학분석가.

### 프롬프트 구성

```
# 1단계: 선행 에이전트 병렬 소환
Agent(SA-9 구조분석, background=true)
Agent(SA-10 평행본문, background=true)
→ 두 에이전트 완료 대기

# 2단계: 선행 결과를 읽어 순차 에이전트 소환
structure_result = Read("{output_path}/설교/research/09-구조분석.md")
parallel_result = Read("{output_path}/설교/research/10-평행본문.md")
literary_result = Read("{output_path}/설교/research/08-문학분석.md")

Agent(
  prompt = f"""
  {rhetorical_agent_def}

  ## 선행 분석 결과 (참고)
  ### 구조 분석:
  {structure_result}

  ### 평행본문 분석:
  {parallel_result}

  ### 문학 분석:
  {literary_result}

  ## 분석 대상
  본문: {scripture}

  ## 출력 규칙 (GRA-Lite)
  [GRA-Lite 규칙 동일]

  ## 저장
  결과를 {output_path}/설교/research/11-수사학분석.md 에 저장하라.
  """,
  run_in_background = false,  # 순차 — 결과를 기다려야 함
  description = "@rhetorical-analyst 수사학 분석"
)
```

### 핵심 규칙

- 선행 에이전트가 **완료된 후에만** 순차 에이전트를 소환한다
- 선행 결과를 Read로 로드하여 프롬프트에 직접 포함한다
- `run_in_background = false`로 결과를 대기한다

---

## GRA-Lite 자기검증 규칙 (연구 에이전트 공통)

| 규칙 | 설명 |
|------|------|
| **출처 필수** | 사실적/언어적 주장은 반드시 출처 명시 (BDB, BDAG, TDNT 등) |
| **절대 표현 금지** | "모든 학자가 동의", "100% 확실" 등 BLOCK |
| **헤지 표현 필수** | 확신도 낮으면 "likely", "arguably", "일부 학자들은" 사용 |
| **시대/지역 명시** | 문화적 주장은 시대와 지역을 특정 |
| **미검증 표시** | 직접 확인 불가한 인용은 [미검증] 태그 |

> GRA-Lite의 한계: 코드 기반 자동 검증(SRCS 점수화)이 없으므로, 에이전트가 자신감 있게 틀린 주장을 할 수 있다.
> 이 한계는 **목사의 신학적 판단력**으로 보완된다.

---

## 결과 수신 및 통합

### 백그라운드 에이전트 결과 수신

- `run_in_background = true`로 소환한 에이전트는 완료 시 자동 알림이 온다
- 알림 수신 후 output 경로의 파일 존재를 확인한다
- 파일이 없으면 에이전트 실패로 판단하고 status.md에 기록한다

### 연구 결과 목사 제시 형식

```
📖 [Research Bridge] 2-N {단계명} 심층 연구 완료

{N}개 전문 에이전트가 분석한 결과를 요약합니다:

━━━ @{에이전트명} ━━━
[요약 3-5문장]
• 핵심 발견 1
• 핵심 발견 2

[반복]

━━━━━━━━━━━━━━━━━━━━━━━━━
전체 연구 원문: research/ 폴더에 저장됨

이 연구 결과를 바탕으로 {단계} 대화를 시작하겠습니다.
특별히 더 깊이 다루고 싶은 부분이 있으신가요?
```
