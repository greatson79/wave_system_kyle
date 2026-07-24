---
description: ax_church prompt-runner 실행 (110개 프롬프트 순차 자동 실행)
argument-hint: "[verify|dry-run|run|resume|from <N>|status|stop]"
---

# /ax-church-run

`~/ax_church/prompt-runner/`의 110개 프롬프트를 Claude Code에서 자동 순차 실행합니다.

## 인자: $ARGUMENTS

다음 규칙으로 동작합니다:

- 인자가 없거나 `run` → 백그라운드 신규 실행
- `verify` → 프롬프트 파일 무결성 검증
- `dry-run` → 실행 순서 미리보기 (실제 호출 없음)
- `resume` → state.json 기준 중단 지점부터 재개
- `from <N>` → N번부터 새 세션으로 시작
- `status` → state.json + 최근 로그 출력
- `stop` → 실행 중인 run.py 프로세스 종료

## 실행 절차

1. `cd ~/ax_church/prompt-runner` 로 이동
2. 인자에 따라 아래 명령을 Bash로 실행:

```bash
# verify
python3 run.py --verify

# dry-run
python3 run.py --dry-run

# run (백그라운드, 로그는 execution.log)
nohup python3 run.py > execution.log 2>&1 &
echo "PID=$!"

# resume
nohup python3 run.py --resume > execution.log 2>&1 &

# from N
nohup python3 run.py --from <N> > execution.log 2>&1 &

# status
cat state.json | python3 -m json.tool | head -30
echo "---"
tail -40 execution.log

# stop
pkill -f "run.py" && echo "stopped" || echo "no running process"
```

3. 실행 시작/재개 시 다음 정보를 한눈에 보고:
   - 시작 시각, PID
   - `state.json`의 `current_step`, `status`, `rate_limit_state`
   - 다음 단계: 진행 모니터링은 `/ax-church-run status`

## 주의

- 실제 작업 디렉토리(CWD)는 `~/ax_church` (= `Vibe-Practice/AI_churhteam`)에서 Claude가 호출되어야 프롬프트가 그 폴더 컨텍스트로 작동.
- Rate-limit 시 자동 5분 대기·최대 60회 재시도 (state.json `rate_limit_state` 추적).
- 강제 중단이 필요하면 `stop` 후 `resume`으로 이어가기.
