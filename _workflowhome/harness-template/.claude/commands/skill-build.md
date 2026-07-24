# /skill-build — 구현 단계

3차 점검이 통과된 이후에만 실행한다. `execute.py`를 사용해 step을 순차 실행한다.
실행 전 반드시 **구현 계획을 먼저 보고**한 뒤 승인을 받아 진행한다.

---

## 전제 확인

```bash
# 3차 점검 통과 여부 확인 (placeholder 없음)
grep -rE '\{\{[^}]+\}\}' . --include="*.md" --include="*.json" \
  | grep -v "SKILL.md" | grep -v "commands/"

# phase 파일 존재 확인
ls phases/0-mvp/index.json phases/0-mvp/step0.md
```

placeholder가 남아 있거나 phase 파일이 없으면 중단하고 이유를 알린다.

---

## Step 1: 구현 계획 보고 (실행 전 필수)

아래 형식으로 보고한 뒤 사용자 승인을 기다린다.

```
## 구현 계획 보고

**실행할 Phase:** 0-mvp
**총 Step 수:** N개

**Step 실행 순서:**
| Step | 제목 | 예상 산출물 | 의존성 |
|------|------|------------|--------|
| 0 | ... | ... | 없음 |
| 1 | ... | ... | Step 0 완료 |
| N | ... | ... | Step N-1 완료 |

**CLAUDE.md 핵심 제약 (매 step에 적용):**
- CRITICAL: [규칙 1]
- CRITICAL: [규칙 2]

**실패 시 대응 계획:**
- 1~2회 자동 재시도 (execute.py 기본 동작)
- 3회 실패 시: status → error, 사용자에게 error_message 보고

**추정 소요 시간:** 약 N분

승인하시면 execute.py를 실행합니다.
```

---

## Step 2: 실행

승인 후 실행한다.

```bash
python3 scripts/execute.py 0-mvp
```

자동 push가 필요하면:
```bash
python3 scripts/execute.py 0-mvp --push
```

---

## Step 3: 진행 중 모니터링

각 step 완료 시 아래를 확인하고 사용자에게 보고한다:

```
Step N 완료
- 생성된 파일: [목록]
- Acceptance Criteria 통과: Y / N개
- 다음 Step: [제목]
```

Step이 error 상태가 되면:

```
Step N 실패
- 오류 메시지: [error_message]
- 원인 분석: [파악한 원인]
- 권장 대응:
  1. phases/0-mvp/index.json에서 해당 step status → "pending"
  2. error_message 삭제
  3. python3 scripts/execute.py 0-mvp 재실행
  또는
  - 오류 원인이 설계 문제라면 /skill-design으로 돌아가 수정 후 재점검
```

---

## Step 4: 구현 완료 검증

모든 step 완료 후 최종 검증을 실행한다.

```bash
# 1. 빌드 / 테스트 실행
[BUILD_COMMAND]
[TEST_COMMAND]

# 2. 생성된 파일 목록 확인
find . -newer phases/0-mvp/index.json -type f | grep -v ".git"

# 3. Acceptance Criteria 전체 확인
grep -h "Acceptance Criteria" -A 20 phases/0-mvp/step*.md
```

---

## 완료 후 안내

```
구현 완료.

실행된 Step: N개
생성된 파일: [목록]
빌드/테스트: 통과 / 실패

다음 단계 옵션:
1. /skill-review 3차 점검 (구현 결과물 재검증)
2. clasp push / git push (배포)
3. /review (전체 완성도 최종 검토)
```

---

## 에러 복구 가이드

```
# step이 error로 끝난 경우:
1. phases/{phase}/index.json 열기
2. 해당 step의 "status": "error" → "pending" 변경
3. "error_message" 키 삭제
4. 저장 후 재실행: python3 scripts/execute.py {phase}

# step이 blocked인 경우:
1. "blocked_reason" 확인
2. 사유 해결 (파일 생성, 권한 부여 등)
3. "status": "blocked" → "pending", "blocked_reason" 삭제
4. 재실행
```
