# t3 Skills & Hooks Developer — Raw

- **차수/축**: 3차 / 코딩·구현 / **Teammate**: t3
- **생성**: 2026-04-29
- **원본 질문**: skill·hook·command 를 범용 라이브러리로 둘 것인가, 워크플로우 특화로 둘 것인가. 신학 정확성·SOT 무결성 같은 churchTeam 고유 검증을 어디에 박을 것인가.
- **근거 출처**: `AI_churhteam/.claude/hooks/scripts/validate_*.py` (11종, 부모 게놈), `Claude_skills/weekly-works/.claude/skills/sermon/rules/{original_language,research-bridge,sermon-title}.md`.

---

## Branch 3.1 — General-Purpose Skills

### 패턴 (구조 예시)

```
.claude/hooks/scripts/   ← 도메인 무관 hook (general)
  ├─ validate_pacs.py            (PA1-PA7 + L0)
  ├─ validate_traceability.py    (CT1-CT5)
  ├─ validate_translation.py     (T1-T9)
  ├─ output_secret_filter.py
  ├─ block_destructive_commands.py
  └─ ...

.claude/skills/          ← 도메인 무관 skill
  ├─ workflow-runner/
  └─ doc-formatter/
```

각 워크플로우는 위 hook/skill 을 *합성* 만 한다.

### 전제
- 파일명·경로·메타 규약이 일관 → hook 분기 불필요.

### 트레이드오프
- (+) 코드 1번 작성·여러 도메인 재사용. 부모 게놈의 11 validator 가 그 증거.
- (+) 회귀 테스트(`_test_*.py`) 가 도메인 독립 → 단위 테스트 작성 쉬움.
- (−) 신학 검증·sermon-plan-2026.json SOT 매칭 같은 도메인 특화 규칙은 General 에 못 들어감.

### 한계
- 신학 정확성(개혁주의 필터)을 General 에 넣으면 의미 누수 — 다른 도메인이 쓸 수 없는 코드를 끌고 다님.

### 반증
- 부모의 11 validator 는 모두 도메인 무관. 도메인 검증을 여기에 추가하면 부모 게놈을 오염.

### `[LOCAL-OK]`
- 파일 시스템 + Python 표준 라이브러리만 사용.

### 🅿️ 파킹 로트
- General hook 의 버전 호환성 정책 — 본 축 범위 밖.

---

## Branch 3.2 — Workflow-Specific Skills

### 패턴 (구조 예시)

```
.claude/skills/sermon/
  ├─ sermon_SKILL.md
  └─ rules/
      ├─ original_language.md     ← 원어 검증 규칙
      ├─ research-bridge.md       ← 연구→설교 다리
      ├─ sermon-title.md          ← 4.5 단계 잠금 규칙
      └─ theology_filter.md       ← (신규) 개혁주의 신학 필터

.claude/skills/weekly-devotion/
  └─ rules/
      └─ devotion-card-spec.md    ← 묵상 카드 형식 검증
```

도메인 검증은 skill 안의 rules 파일 + skill 전용 validator 로.

### 전제
- 워크플로우당 유지보수 책임자 명확 (사용자 1인).
- skill 변경이 다른 skill 에 파급 없음.

### 트레이드오프
- (+) 정확도 최고. 토큰 효율 좋음 (skill 안에 도메인 컨텍스트 박힘).
- (+) 신학 필터·SOT-pin 같은 churchTeam 고유 규칙을 자연스럽게 수용.
- (−) "묵상 템플릿 변경" 같은 운영 변경이 다중 skill 동시 수정으로 번질 수 있음.
- (−) 특화 skill 13+ 시 agent-registry.md 자체가 메타-SOT 가 됨.

### 한계
- 특화 skill 간 *공통 헬퍼* (예: HTML 캡쳐, JSON 검증) 가 중복 구현될 위험. 이는 General 에서 다시 빼와야 함.

### 반증
- weekly-works 가 이미 7 skill × 자체 rules 구조로 운영. 부담 폭발 사례 없음 (현재 메모리 기준).

### `[LOCAL-OK]`
- 로컬 파일 + skill 시스템.

### 🅿️ 파킹 로트
- skill 패키징·버전 관리 정책 — *parking-lot.md 미해결 항목 (3)* 으로 이관.

---

## 최종 정리 (Branch 3.1 vs 3.2)

| 기준 | 3.1 범용 | 3.2 특화 |
|---|---|---|
| 재사용성 | 높음 | 낮음 |
| 정확도/토큰 효율 | 보통 | 높음 |
| 도메인 검증 수용 | 못함 | 자연스러움 |
| 변경 파급 | 적음 | 다중 skill 동시 수정 위험 |
| 메타-SOT 부담 | 적음 | agent-registry.md 비대화 |

**권고 좌표**: **레이어 분리** (이름공간 prefix 로 충돌 방지)
- `val/*` ← 부모 게놈 11 validator + secret/sensitive guard. churchTeam 도 그대로 사용.
- `skill/sermon/*`, `skill/weekly-devotion/*`, … ← 도메인 검증 + rules.
- `cmd/주간총괄`, `cmd/주간현황`, `cmd/설교` ← 사용자 인터페이스.
- 신학 필터·SOT-pin checker(sermon-plan-2026.json JSONPath) 는 *skill/sermon* 안에 둔다. PRD 명시.
- 모두 `[LOCAL-OK]`.
