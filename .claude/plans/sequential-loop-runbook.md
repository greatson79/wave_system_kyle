# Sequential Loop Runbook
# 환경스캐닝 → 투자분석 순차 실행

**패턴:** sequential  
**모드:** safe  
**생성일:** 2026-05-28  
**중단 조건:** 사용자 Ctrl+C 또는 오류 발생 시

---

## 실행 순서

1. **환경스캐닝** — `/env-scan:run` (EnvironmentScan-system-main-v4-main)
2. **투자분석** — `python3 -m investscan.weekly_orchestrator` (01.invest_test)

## 안전 게이트 (safe 모드)

- 각 단계 완료 후 알림 전송
- Human Checkpoint 도달 시 대기
- 오류 발생 시 중단 + 알림

## 실행 명령

```bash
bash ~/.claude/plans/run-sequential-loop.sh
```

## 모니터링

```bash
tail -f /tmp/claude_loop.log
```
