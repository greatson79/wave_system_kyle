# T4 Sustainability Strategist — 원본 산출 (Round-01)

## 메타데이터
- 조사 차수: 1
- Teammate: Sustainability Strategist (t4)
- 조사 축: 지속 가능성·확장 조건
- 가정 축: Claude Code 단독 완결(Branch A) vs 외부 연동(Branch B) 지속가능성 비교
- 생성일: 2026-04-29
- 근거 출처: AGENT_PROMPTS_ADVANCED.md / Claude Code Max 구독 구조 기준

---

## Branch A: Claude Code 단독 완결

### 토큰 소비 효율 추정

| 파이프라인 | 에이전트 수 | 회당 토큰 추정 |
|-----------|-----------|--------------|
| 설교 파이프라인 1회 | Exegesis(~2K) + Structure(~1.5K) + Filter(~1K) + Application(~1.5K) | ~6~8K tokens |
| 행정 문서 1건 | Operations(~1K) | ~1K tokens |
| 양육 커리큘럼 1회 | Learner+Curriculum+Content+Filter(~5K) | ~5K tokens |

- 주 1회 설교 + 묵상 + 행정 ≈ **월 50~80K tokens** 추정
- Claude Code Pro/Max 기준: 충분한 여유 (한도 명시적 수치 없으나 일반적 사용 범위 내)
- 양육 커리큘럼까지 추가 시: 빡빡해질 수 있음

### 유지보수 복잡도
- **Claude Code 업데이트 리스크**: `.claude/agents/` 구조와 Agent() 호출 방식이 변경될 경우 파이프라인 전체 영향
- **Theology Filter 프롬프트**: 핵심 품질 보증 장치인데, 이 프롬프트 자체의 버전 관리 체계 없음 → 출력 일관성 저하 시 목사가 매번 검토해야 하는 상황 발생
- **state.yaml 스키마 변경**: 에이전트 추가 시 스키마 변경이 기존 파이프라인에 영향

### 확장 한계
- 에이전트 수 증가 시: 파이프라인 실행 시간 증가, 컨텍스트 누적
- 멀티 사용자 지원 시: state.yaml 동시 쓰기 충돌 위험
- 프로젝트 수 증가 시: 별도 프로젝트별 `.claude/` 구조 필요

### Branch A 결론
- 지속 가능성: **중간**
- 최대 위험: Theology Filter 프롬프트 신뢰도 저하 (버전 관리 없을 시)
- 6개월 후 유지보수 부담: 중간 (Claude Code 업데이트 대응 필요)

### 파킹 로트
- Theology Filter 프롬프트 회귀 테스트 방법
  - 카테고리: 구조적 리스크
  - 이유: 프롬프트 변경 시 이전 버전과 동일한 출력 보장 방법 없음
- state.yaml 스키마 버전 관리 전략
  - 카테고리: 구조적 리스크

---

## Branch B: 외부 연동 전제

### 토큰 소비 효율
- Python Hook 기반 Theology Filter는 토큰 소비 없음 → **토큰 효율 향상**
- 원어 DB 조회는 로컬이므로 토큰 소비 없음

### 유지보수 복잡도
- Python Hook: 유지보수 가능하나 Python 버전·라이브러리 의존성 관리 부담 추가
- 원어 DB: 업데이트·버전 관리 필요 (성경 본문 DB는 변경이 드물어 부담 낮음)
- 전체적으로 Branch A보다 유지보수 항목이 많지만 각각의 신뢰성은 높음

### Branch B 결론
- 지속 가능성: **중간~높음** (신뢰성↑, 관리 항목↑)
- 트레이드오프: 신뢰성 vs 관리 복잡도

---

## Branch A vs B 비교 정리

| 항목 | Branch A (단독) | Branch B (연동) |
|------|----------------|----------------|
| 토큰 효율 | 중간 | 높음 (Hook은 토큰 없음) |
| Theology Filter 신뢰성 | 변동 가능 | 높음 (규칙 기반) |
| 유지보수 항목 수 | 적음 | 많음 |
| 6개월 후 부담 | 중간 | 중간 (다른 이유로) |

### 결론 (Sustainability Strategist)
- **state.yaml + Theology Filter 버전 관리**가 지속가능성의 핵심
- 토큰 효율 관점에서 Python Hook Theology Filter가 장기적으로 유리
- 가장 큰 구조적 병목: Theology Filter 프롬프트 신뢰도 관리

### 미해결 / 후속 조사 필요
- Theology Filter 프롬프트 회귀 테스트 자동화 방법
- state.yaml 스키마 버전 관리 전략 (에이전트 추가 시 하위 호환성)
- 월간 토큰 소비 실측 (초기 운용 후 데이터 필요)
