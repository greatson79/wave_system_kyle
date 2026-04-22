# /approve-hitl — HITL (Human-in-the-Loop) Gate Approval

Approve a HITL gate to allow InvestScan to proceed to the next phase.
Three gates exist at key decision points requiring human confirmation.

## Usage
```
/approve-hitl 1    — Approve HITL-1 (API keys + watchlist configuration)
/approve-hitl 2    — Approve HITL-2 (Phase 2 cost acknowledgment + proceed choice)
/approve-hitl 3    — Approve HITL-3 (Korean report review + Telegram dispatch)
```

## HITL-1 (Step 6 — Infrastructure setup approval)
**Trigger**: After `personalizer.py --hello-test` Telegram message confirmed
**Required from user**:
  - Telegram Bot Token registered in Keychain
  - Telegram chat_id confirmed
  - DART API key registered (optional but recommended)
  - FRED API key registered
  - Target sectors confirmed (list)
  - Platform: "Mac" or other
  - Custom watchlist (optional)
**Action**: Write to `state.yaml`:
  ```yaml
  hitl_1:
    completed: true
    telegram_bot_token_registered: true
    telegram_chat_id_registered: true
    dart_api_key_registered: [true|false]
    fred_api_key_registered: true
    sectors_confirmed: [...]
    completed_at: "[ISO8601]"
  ```
→ Proceed to Step 7 (package installation)

## HITL-2 (Step 8 — Phase 2 cost acknowledgment)
**Trigger**: After M0.5 Done Gates pass + cost estimate presented
**Required from user**:
  - Acknowledge estimated monthly Claude API cost (M1 phase)
  - Choose: "continue" | "pause_2weeks"
**Action**: Write to `state.yaml`:
  ```yaml
  hitl_2:
    completed: true
    choice: "continue"
    m1_cost_acknowledged: true
    choice_date: "[ISO8601]"
  ```
→ If "continue": proceed to Step 9 (Stage 2 implementation)
→ If "pause_2weeks": schedule reminder, hold at Step 8

## HITL-3 (Step 12 — Korean report approval + Telegram dispatch)
**Trigger**: After weekly report generated + pACS ≥ 50
**Presented to user**: 3-line summary (종목 / 신호 / 리스크) + Y/N prompt
**User action**: Review and run the approval helper, or type `/approve-hitl 3`

### 간소화 승인 흐름 (권장)
```
python3 -m investscan.approve_hitl
```
출력 예시:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋  HITL-3 최종 검토 — 2026-03-29  (2026-W13)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  종목    Samsung Electronics (005930)  (재무 실적 기반)
  신호    📈 Positive momentum maintained
  실적    Revenue +8.3% YoY, Op.Income +34.2%
  리스크   DRAM oversupply resurgence → est. -12% revenue…
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Telegram 발송하시겠습니까? [Y/N]:
```
Y 입력 시: state.yaml hitl_3 갱신 → Telegram 발송 명령어 안내
N 입력 시: 취소, 리포트 경로 표시

### Autopilot 모드 (자동 승인)
```
python3 -m investscan.approve_hitl --yes
```

**Action**: Write to `state.yaml`:
  ```yaml
  hitl_3:
    completed: true
    report_approved: true
    approved_at: "[ISO8601]"
  ```
→ Dispatch Telegram (Korean 5-line summary)
→ Save both English + Korean reports to `output/reports/`
