---
name: health-dashboard
description: FR-22 6칸 자가 검증 카드 렌더링 스킬
---

# Health Dashboard Skill (FR-22)

Renders the churchTeam 6-signal health verification card in Korean.

## 6 Signals

| Signal | Key | Green | Yellow | Red |
|--------|-----|-------|--------|-----|
| DNA 상속 | dna_inheritance | manifest.json 존재 + SHA 일치 | manifest 존재, SHA 미검증 | manifest 없음 |
| SOT 무결성 | sot_integrity | state.yaml 유효 + 쓰기 권한 정상 | state.yaml 존재, 검증 미완 | state.yaml 손상 |
| 신학 필터 | theology_filter | 시드 ≥20 + 차단 활성 | 시드 < 20 (경고만) | 필터 오류 |
| 외부 인증 | external_auth | Telegram/Gmail 응답 정상 | 인증 만료 임박 | 인증 실패 |
| 자기 진화 이력 | self_evolution_history | ADR 기록 정상 | ADR 없음 | 진화 게이트 오류 |
| didim 도달성 | didim_reachability | CLAUDE.md + 7 agents 존재 | 일부 에이전트 없음 | CLAUDE.md 없음 |

## Composite Score

```
사역 가능: 모든 신호 ✅ 또는 ⚠️ 1개 이하
일부 점검: ⚠️ 2개 이상 또는 ❌ 1개
중단:      ❌ 2개 이상
```

## Render Template

```
══════════════════════════════════════
  churchTeam 자가 검증 카드 (FR-22)
══════════════════════════════════════
  DNA 상속          {dna_inheritance}
  SOT 무결성        {sot_integrity}
  신학 필터         {theology_filter}
  외부 인증         {external_auth}
  자기 진화 이력    {self_evolution_history}
  didim 도달성      {didim_reachability}
══════════════════════════════════════
  종합 상태: {overall}
══════════════════════════════════════
```
