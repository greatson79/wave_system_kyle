# ax_church prompt-runner 실행 가이드

`~/ax_church/prompt-runner/` (= `Vibe-Practice/AI_churhteam/prompt-runner/`)의
110개 프롬프트를 Claude Code에 순차 자동 실행하는 러너 사용법.

---

## 위치

```
~/ax_church/prompt-runner/
├── run.py            # 메인 러너
├── state.json        # 진행 상태 (current_step, sessions, rate_limit_state)
├── prompts/          # 001.txt ~ 110.txt
├── execution.log     # 실행 로그
└── logs/             # 단계별/rate-limit 로그
```

- 총 프롬프트 수: **110**
- `/clear` 위치: 3, 6, 9, 12, 14, 17, 20, 23, 26, 29, 33, 36, 39, 42, 47, 50, 53, 58,
  61, 64, 67, 70, 73, 76, 79, 82, 85, 88, 91, 95, 98, 101, 104, 107, 110
- 새 세션 시작점: 1, 4, 7, 10, 13, 15, 18, 21, 24, 27, 30, 34, 37, 40, 43, 48, 51,
  54, 59, 62, 65, 68, 71, 74, 77, 80, 83, 86, 89, 92, 96, 99, 102, 105, 108

---

## 실행 명령

```bash
cd ~/ax_church/prompt-runner

# 1) 무결성 검증
python3 run.py --verify

# 2) 실행 순서 미리보기 (실제 호출 없음)
python3 run.py --dry-run

# 3) 처음부터 실행 (백그라운드 권장)
nohup python3 run.py > execution.log 2>&1 &
echo "PID=$!"

# 4) 중단 지점부터 재개
nohup python3 run.py --resume > execution.log 2>&1 &

# 5) 특정 번호부터 새 세션으로 시작
nohup python3 run.py --from 34 > execution.log 2>&1 &

# 6) 진행 상황 확인
cat state.json | python3 -m json.tool | head -30
tail -40 execution.log

# 7) 강제 중지
pkill -f "run.py"
```

### 환경 변수 (선택)

```bash
MAX_TURNS=0 TIMEOUT=0 SKIP_PERMISSIONS=1 nohup python3 run.py > execution.log 2>&1 &
```

| 변수 | 의미 | 기본 |
|------|------|------|
| `MAX_TURNS` | 에이전트 최대 턴 수 (0=무제한) | 0 |
| `TIMEOUT` | 프롬프트당 최대 실행 시간 초 (0=무제한) | 0 |
| `SKIP_PERMISSIONS` | 권한 확인 건너뛰기 | 0 |

---

## 동작 원리

1. **첫 프롬프트**: `claude -p --output-format stream-json --verbose < prompt.txt`
   → JSON 응답에서 `session_id` 추출 → `state.json` 저장
2. **같은 세션 후속**: `claude -p --resume <session_id> < prompt.txt`
3. **`/clear` 위치 도달**: session_id 폐기 → 다음 번호에서 새 세션 시작
4. **프로세스 종료** = 작업 완료 (결정론적)

---

## Rate-Limit 자동 재시도

- 감지 키워드: `rate limit`, `quota exceeded`, `429` 등
- **최대 60회 재시도, 5분 간격, 총 5시간 대기**
- 초과 시 정상 종료(exit 0) — `state.json.rate_limit_state` 보존
- `--resume` 시 남은 대기 시간만큼 자동 sleep 후 재개

```bash
# 강제 진행 (권장 안 함)
# state.json의 rate_limit_state 를 null로 수정 후
python3 run.py --resume
```

모니터링:
- `logs/{step}.rate-limit.log` — 대기 이력
- `state.json.rate_limit_state` — 현재 상태(step, attempt_count, next_retry_at)

---

## 권장 시작 순서

1. `python3 run.py --verify`
2. `python3 run.py --dry-run`
3. `nohup python3 run.py > execution.log 2>&1 &`
4. 모니터: `tail -f execution.log` 또는 `cat state.json`

중단 후: `python3 run.py --resume`
