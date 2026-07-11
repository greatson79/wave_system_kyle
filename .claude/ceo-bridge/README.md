# CEO 파일 브리지 (2026-07-02 · 주인님 C안 승인)

background CEO 세션은 cmux 소켓이 차단(launchd 계보·cmuxOnly 라이브 데몬)되어
**수신만 가능·송신 불가**. 이 브리지가 CEO의 실질 outbound를 제공한다.

## 구조
- `outbox/*.sh` — CEO가 떨구는 명령 파일(이름순 실행 — `NNN-설명.sh` 타임스탬프 프리픽스 권장)
- `done/` — 실행 완료 파일 + `.log`(stdout/stderr + exit code)
- `bridge.sh` — 감시 루프(2초 폴링). **cmux 내부 pane에서만 실행**(CSO 기동 소관)
- `STOP` — 이 파일을 만들면 브리지가 자율 종료(생명주기 관리)

## 사용 (CEO)
1. `outbox/`에 `.sh` 작성 (예: `cmux send --workspace ws1 --surface s54 "..." ; cmux send-key --workspace ws1 --surface s54 enter`)
2. 2~4초 후 `done/<파일>.log`에서 결과 확인 (exit code 포함)

## 기동 (CSO — cmux 내부 pane 1개)
```
sh /Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/bridge.sh
```
- 탭명: `ceo-bridge`. 서버 아님(감시 루프 1개) — WORKER_DIRECTIVE 1조 생명주기 관리 대상.
- 종료 필요 시: `touch /Users/kylechoi/Desktop/Ai_works/.claude/ceo-bridge/STOP`

## 보안
- 디렉토리 700 (같은 사용자만 쓰기 가능) — outbox에 쓸 수 있는 주체 = 로컬 사용자 프로세스뿐.
- cmux Automation mode 영구설정 완료 상태이므로 **다음 cmux 재시작 후에는 CEO 직접송신이 복구**되며, 그 시점에 이 브리지는 STOP으로 폐기한다.
