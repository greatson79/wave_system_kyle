# t1 Workflow Script Architect — Raw

- **차수**: 3차 / **축**: 코딩·구현 / **Teammate**: t1
- **생성**: 2026-04-29
- **원본 질문**: workflow.md 를 *선언적* 으로 둘 것인가, *절차적* 으로 둘 것인가. churchTeam(설교 5단계, 묵상 15장, 기도카드, 소그룹·카드뉴스 병렬) 구현에서 어느 표현이 코드 수준에서 적합한가.
- **근거 출처**: `Claude_skills/weekly-works/.claude/skills/team-leader/rules/workflow-dag.md`, weekly-works 운영 메모리(4.5 단계 후 D·E 동시 소환), `Coding_Implementation_DeepDive_PRD_Teammate_Executable.md` Phase1 Branch 1.1/1.2.

---

## Branch 1.1 — Declarative Workflow (intent-only)

### 패턴 (구조 예시)

```yaml
# workflow.md (선언적)
tasks:
  - id: sermon-step-4_5
    intent: "주일설교 4.5단계 — 제목 확정 및 sermon-context.md 갱신"
    inputs: [output/{월}/{주차}/설교/draft-step4.md]
    exit_criteria:
      - file_exists: output/{월}/{주차}/설교/sermon-context.md
      - field_present: title, scripture, key_message
    depends_on: [sermon-step-4]

  - id: small-group
    intent: "소그룹 나눔지 (장년+청소년) 작성"
    depends_on: [sermon-step-4_5]

  - id: sns-cardnews
    intent: "SNS 카드뉴스 7장"
    depends_on: [sermon-step-4_5]
```

team-leader 가 `intent` 와 도메인 지식(CLAUDE.md)을 결합하여 sub-agent 와 skill 을 *선택* 한다.

### 전제
- team-leader 프롬프트가 7개 산출물의 도메인 모델을 이미 학습.
- agent-registry.md 에 `type=interactive|auto`, `writes`, `reads` 가 박혀 있음.
- 도메인 분기 규칙(예: 4.5 → D·E fanout)이 team-leader 프롬프트 안에 글로 박힘.

### 트레이드오프
- (+) workflow.md 짧음, 새 산출물 추가 시 노드 1개만 작성.
- (+) sub-agent 변경에 workflow.md 가 둔감.
- (−) 동일 입력에 다른 실행 경로 → 디버깅 시 "왜 이 sub-agent 가 호출됐지?" 추적 비용 큼.
- (−) 하드 게이트(4.5 후 D·E 동시 소환) 를 *문장* 으로만 강제 → 누락 회귀 위험.

### 한계
- "4.5 단계 시 D·E 반드시 동시 소환" 규칙이 사용자 메모리에 *별도 피드백* 으로 박혀야 했던 사실 자체가 선언적 단독의 약점이다. workflow.md 가 이를 표현 못하기 때문에 외부 메모리로 보강된 것.
- skill 호출 비결정성 → 회귀 테스트 작성 어렵다.

### 반증
- weekly-works 가 이미 절차적 `workflow-dag.md` 로 운영 중이며, 운영 중 학습된 규칙(병렬 강제, 카드뉴스 템플릿 선확인, dashboard.html 갱신 등)이 그 안에 코드처럼 박힘. 선언적 단독으로 회귀하면 이 학습이 흩어진다.

### `[LOCAL-OK]`
- 파일 시스템 + Claude Code 실행만으로 완결. 외부 의존 없음.

### 🅿️ 파킹 로트
- "intent 자체를 LLM이 표준화" 하는 단계가 필요할 수 있는가? — 본 축 범위 밖.

---

## Branch 1.2 — Procedural Workflow (DAG with handlers)

### 패턴 (구조 예시)

```yaml
# workflow.md (절차적)
phases:
  P1_AUTO:
    parallel:
      - node: weekly-devotion
        agent: weekly-devotion
        skill: skill/weekly-devotion
        inputs: [data/devotion-data.json, sermon-plan-2026.json]
        outputs: [output/{월}/{주차}/매일묵상/*.html]
        validators: [val/pacs, val/translation, val/sot-pin]
        retry_budget: 2
      - node: prayer-doc
        agent: prayer-doc
        ...
  P1_INTERACTIVE:
    sequence:
      - node: sermon-1
      - node: sermon-2
      - node: sermon-3
      - node: sermon-4
      - node: sermon-4_5
        gate: title_locked   # phase enum 전이 잠금
        on_pass: lock(sermon-context.md)  # 이후 immutable
  P2_PARALLEL:
    parallel:
      - node: small-group
      - node: sns-cardnews
    depends_on: [P1_INTERACTIVE.sermon-4_5]
  P3_REPORT:
    sequence: [weekly-report]
```

### 전제
- DAG 변경 빈도 < 1회/월. 자주 바뀌면 유지비 폭발.
- 각 node 는 멱등 — 동일 입력이면 동일 출력 경로 보장.
- gate 는 코드 수준에서 phase enum 전이로 강제(상태머신 얇게 결합, t5 와 통합).

### 트레이드오프
- (+) 예측 가능성·재현성 최상.
- (+) 하드 게이트가 **DAG 구조 자체** 가 되어 누락 불가능.
- (−) 새 산출 추가 시 노드·validator·gate 동시 수정.
- (−) 인간 협업 분기(목사가 본문 변경 → root 재계획) 표현이 어려움 → 동적 sub-DAG 생성 노드 필요.

### 한계
- 정적 DAG 는 *동적 재계획* 을 못 다룬다. churchTeam 의 1~4단계 인터랙티브 분기는 사용자 결정이 노드 추가/제거를 유발하므로 sub-DAG generator 가 별도 필요.

### 반증
- round-01 t1 (Workflow Architect) 결과가 절차적 우위 결론. 그러나 t3 Operator Analyst 가 절차적의 "작성 마찰" 을 경고. 운영자 1인(목사) 환경에서 마찰은 실질 비용.

### `[LOCAL-OK]`
- 파일 + 로컬 실행만으로 충분.

### 🅿️ 파킹 로트
- DAG 정적 표현을 어떻게 형상관리(version)하는가 — 본 축 범위 밖, parking-lot.md 로 이관.

---

## 최종 정리 (Branch 1.1 vs 1.2)

| 기준 | 1.1 선언적 | 1.2 절차적 |
|---|---|---|
| workflow.md 길이 | 짧음 | 김 |
| 하드 게이트 강제력 | 약함 (문장) | 강함 (구조) |
| 새 산출 추가 비용 | 낮음 | 중간 |
| 디버깅 추적 | 어려움 | 쉬움 |
| 인간 분기 표현 | 자연스러움 | 동적 sub-DAG 필요 |

**구성 요소별 적합한 접근**
- 설교 4.5 게이트, P2 fanout, P3 보고서: 절차적
- 노드 내부의 "어떤 도구로 할 것인가" 결정: 선언적
- 결론: **상위 절차적 + 노드 내부 선언적** 혼합. workflow.md 는 phase·node·gate 만 절차적으로 박고, 각 노드 내부 `intent`+`exit_criteria` 만 둔다.
