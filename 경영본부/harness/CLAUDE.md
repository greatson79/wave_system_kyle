# CLAUDE.md — harness/

**Harness Engineering System** — 장기 자율 앱 개발용 3-에이전트 하네스.
Planner → (Generator ↔ Evaluator) GAN 루프. 에이전트는 **파일로만** 통신한다.

> **자기완결형 독립 프로젝트다.** 모노레포·AgenticWorkflow 틀과 분리되어 이 폴더 내부만으로
> 작동한다. 의존성은 `requirements.txt`에 전부 선언돼 있고(부모 리포에서 아무것도 import하지
> 않음), 산출물·생성앱·git은 모두 폴더 안에 머문다. 폴더를 통째로 다른 위치/별도 레포로 옮겨도
> 그대로 돌아간다.

> 사람용 상세 가이드는 `HARNESS_README.md`. 이 파일은 **에이전트 작업 컨텍스트**다.

---

## 절대 기준

1. **격리가 핵심** — 생성 앱은 `workspace/<run-id>/`에 **자체 git**으로 빌드한다.
   상위 모노레포(`Ai_works/`)는 **절대** 건드리거나 `git add` 하지 않는다.
2. **파일 통신만** — 에이전트는 서로 직접 호출하지 않는다. `artifacts/`의 파일 +
   시그널 토큰(`READY_FOR_QA`, `CONTRACT_APPROVED` 등)으로만 주고받는다.
3. **스키마가 진실** — 흐름 제어는 `*.json` 사이드카(스키마 검증)에서 읽는다.
   마크다운 산문을 정규식으로 파싱하지 않는다.
4. **Evaluator는 회의적** — 작동하는 걸 칭찬하지 말고 깨진 것을 찾는다. 스텁·미완성은 FAIL.
5. **실행 전 검증** — 실 비용 발생하는 real run 전에 반드시 `--dry-run` + `--check`.

---

## 변경 시 주의

| 파일 | 역할 | 바꿀 때 |
|------|------|---------|
| `run_harness.py` | 오케스트레이터 (루프·검증·핸드오프) | 루프 분기/검증 게이트 깨지지 않는지 dry-run 재실행 |
| `agents/_runtime.py` | `claude` CLI 드라이버 | **프롬프트는 stdin 전달** (variadic 플래그 충돌 방지). 플래그 순서 바꾸면 `--check` 재실행 |
| `agents/_context.py` | 경로·시그널·스키마검증·workspace git | 시그널 토큰/경로 규칙 바꾸면 3개 에이전트·테스트 동시 수정 |
| `agents/{planner,generator,evaluator}.py` | 에이전트 (real + dry-run) | dry-run 스텁은 **스키마 유효**해야 함. 둘 다 수정 |
| `prompts/*_system.md` | 시스템 프롬프트 | 파일 경로·시그널 토큰·JSON 사이드카 지시 일관성 유지 |
| `schemas/*.json` | JSON Schema | 변경 시 dry-run 스텁·에이전트 프롬프트 동기화 |
| `config/harness_config.yaml` | 튜너블 | `evaluation.weights` 합은 1.0 (로더가 강제) |

---

## 실행

```bash
cd harness
python tests/test_harness_wiring.py    # 배관 테스트 (무료, dry-run 루프)
python run_harness.py --check          # 실 CLI 백엔드 확인 (haiku 2콜, ~8¢)
python run_harness.py "<앱 아이디어>" --dry-run
python run_harness.py "<앱 아이디어>"   # 실 빌드 (수시간·수달러 — 주의)
```

---

## 안전 모델 (정확히)

`--add-dir`는 **파일 도구**만 워크스페이스로 제한한다. Generator의 `Bash`는 제한받지
않으므로 진짜 샌드박스가 아니다. 보호막은 (1) 협조적 에이전트 + 프롬프트, (2) 스프린트별
커밋 롤백, (3) Evaluator 읽기전용 + git-revert 백스톱, (4) 모노레포 미커밋. 하드 샌드박스가
필요하면 `harness/workspace/`로 스코프된 컨테이너/VM 안에서 돌린다.

---

## 모델 / 비용

실 모델 ID 사용 (스펙의 `claude-opus-4-6-20251101`은 가상). 기본값: planner·evaluator =
`claude-opus-4-8`, generator = `claude-sonnet-4-6`. `config/harness_config.yaml`에서 조정.
OAuth/구독 인증이면 `ANTHROPIC_API_KEY` 불필요(없으면 `--bare` 자동 비활성).
