# t4 Verification & Quality Coder — Raw

- **차수/축**: 3차 / 코딩·구현 / **Teammate**: t4
- **생성**: 2026-04-29
- **원본 질문**: 검증을 모든 노드에 박을 것인가, 핵심 노드에만 박을 것인가. 신학 정확성·SOT 무결성·번역 정확성을 어디서 어떻게 자동화할 것인가.
- **근거 출처**: AgenticWorkflow `docs/protocols/quality-gates.md` (L0-L2 4계층 + P1 14항목), 부모 11 validator, 사용자 메모리(`/주간현황 텍스트 출력 금지` 등 UX 비용 회피 시그널).

---

## Branch 4.1 — Strict Verification (전 노드 자동 검증)

### 패턴 (구조 예시)

```yaml
# 모든 노드에 강제 부착
node:
  validators:
    - val/pacs        (출력 형식)
    - val/translation (영→한 일치)
    - val/domain      (도메인 규칙)
    - val/sot-pin     (sermon-plan-2026.json 핀)
  retry_budget: 3
  on_fail: re-run-with-correction
```

### 전제
- 사용자가 토큰 비용 흡수 가능.
- LLM-as-judge 의 false-positive 를 사용자 컨펌 단계로 흡수.

### 트레이드오프
- (+) 회귀 즉시 포착. SOT drift 위험 최소.
- (−) 묵상 15 × 검증 3종 = 45 LLM call. 토큰 비용 큼.
- (−) UX 비용도 큼 — 검증 결과를 어디에 보여줄지(텍스트 출력 vs dashboard) 미결정 시 사용자 피로.

### 한계
- 신학 정확성 LLM 검증은 false-positive 율 무시할 수 없음. 결국 *사용자 컨펌* 단계가 들어가야 함 → 완전 자동 불가.

### 반증
- 사용자 메모리 "주간현황 텍스트 출력 금지, dashboard.html 갱신" 은 *검증 결과의 UX 비용* 도 품질 일부임을 보여줌. Strict 단독은 UX 비용 폭발.

### `[LOCAL-OK]`
- LLM 호출은 Claude Code 내부. 외부 SaaS 없음.

### 🅿️ 파킹 로트
- LLM-judge false-positive 를 사용자 피드백으로 학습 — 본 축 범위 밖.

---

## Branch 4.2 — Selective Verification (L0/L1/L2 게이트)

### 패턴 (구조 예시)

```
모든 노드:
  L0 (Anti-Skip Guard):
    - 빈 파일 차단
    - 산출 경로 존재 확인
    - 비결정 산출도 *경로* 는 결정적
  L1 (Verification Gate):
    - 파일 형식 검증 (HTML well-formed, JSON schema)
    - 키 필드 존재 (sermon-context.md 의 title/scripture/key_message)

핵심 노드만:
  L2 (Calibration):
    - 설교 4.5 단계: title 일치, sermon-plan-2026.json SOT-pin
    - 신학 정확성: skill/sermon/theology_filter
    - 번역: val/translation (영문 원본이 있는 경우)
```

### 전제
- "어디가 회귀 시 치명적인가" 가 PRD 에 라벨링되어 있음.
- L0/L1 은 빠른 정적 검사 → 토큰 비용 거의 0.

### 트레이드오프
- (+) 토큰 절약. UX 비용 낮음.
- (+) L0 가 *모든* 노드에 박혀 silent 빈 산출 차단.
- (−) 비검증 노드에서 silent semantic drift 가능 (형식은 맞는데 내용이 틀림).
- (−) "어디가 치명적" 라벨링 자체가 PRD 작업 부담.

### 한계
- SOT 무결성(sermon-plan-2026.json 의 필드를 AI 가 *기억* 으로 재구성) 은 L0/L1 만으로 못 잡음 → SOT-pin checker(JSONPath + hash) 별도 의무.
- 비결정 산출(카드뉴스 PNG) 은 hash 비교로 회귀 검출 어려움 → 별도 정책 필요(parking-lot 항목 #6).

### 반증
- 부모 게놈 `quality-gates` 가 이미 L0/L1/L2 4계층 채택 → 본 패턴이 부모 정합성 우위.

### `[LOCAL-OK]`

### 🅿️ 파킹 로트
- 비결정 산출 회귀 검출 (parking-lot #6).

---

## 최종 정리 (Branch 4.1 vs 4.2)

| 기준 | 4.1 엄격 | 4.2 선택적 |
|---|---|---|
| 토큰 비용 | 높음 | 낮음 |
| UX 비용 | 높음 | 낮음 |
| 회귀 포착 | 최고 | 라벨링에 의존 |
| 부모 게놈 정합 | 부분 | 완전 |

**권고 좌표**: **L0 전면 + L1 산출 형식 전면 + L2 핀포인트(설교 4.5, 신학 정확성, 번역, SOT-pin)**.
- SOT-pin checker 는 *모든* 설교 노드에 의무.
- 비결정 산출 회귀 검출은 PRD Open Questions 로 남김.
- `[LOCAL-OK]`.
