# ai_churchteam 푸시본 실발동 재검수 및 누락 근인

## 1. 긴급 결론

> **ACCEPT — 어제 푸시한 `ai_churchteam`은 실제 스킬베이스 진입점으로 발동 가능하다.**

- 대상 푸시 커밋: `c501c713fc68aa97c7e4543c02254ea5adf0932a`
- 원격 계보: `origin/feat-0-mvp`가 `c501c71`을 포함
- 레지스트리 등재: PASS
- 공용 심볼릭 링크: PASS
- frontmatter `name` 정합: PASS
- fresh 격리 Skill 호출: PASS
- 선택 라우트: `/팀-분기`
- 프로젝트·상태파일 변경: 0건
- 복구 필요: **없음**

정확한 구조는 **스킬로 진입·분류하고 workflow가 정식 실행을 완결하는 하이브리드 구조**다. 워크플로우로만 작동하는 것도 아니고, 모든 사역 실행이 Skill 하나로 끝나는 것도 아니다.

## 2. 푸시 커밋 실측

`c501c71`은 다음 4개 변경을 포함한다.

| 파일 | 형태·기능 | 판정 |
|---|---|---|
| `.claude/build_skill_registry.sh` | `ai-churchteam` 매핑 1행 추가 | PASS |
| `.claude/skills/ai-churchteam` | mode `120000` 심볼릭 링크 | PASS |
| `목회사역본부/AI_churchteam/.claude/skills/ai-churchteam/SKILL.md` | Skill 정의 | PASS |
| `목회사역본부/AI_churchteam/.claude/skills/ai-churchteam/agents/openai.yaml` | 표시·기본 프롬프트 metadata | PASS |

현재 공용 링크의 realpath:

`/Users/kylechoi/Desktop/Ai_works/목회사역본부/AI_churchteam/.claude/skills/ai-churchteam`

레지스트리 빌더의 매핑:

`ai-churchteam|목회사역본부/AI_churchteam/.claude/skills/ai-churchteam`

## 3. frontmatter·호출명 정합

`SKILL.md`:

- `name: ai-churchteam`
- `description:` 존재

`openai.yaml`:

- `display_name: "AI Church Team"`
- 기본 프롬프트가 `$ai-churchteam` 호출을 명시

레지스트리명, 디렉터리명, frontmatter `name`, 기본 호출명이 모두 `ai-churchteam`으로 일치한다.

## 4. 실제 발동 실측

### fresh 격리 호출

- 런타임: Claude Code 2.1.220 · Claude Sonnet 5
- 설정 범위: AI_churchteam 프로젝트
- 쓰기·상태변경·세션저장 차단
- 호출: `/ai-churchteam`으로 분기 사역 평가·준비 요청
- 결과:
  - Route: `/팀-분기`
  - 담임목사 승인 필요 안내
  - 목회철학 SOT 적용
  - 신학 필터 적용
  - downstream bridge 경계 유지

판정: **fresh 발동 성공**

### native Skill 도구 기존 실측 대조

기존 실제발동 증거에는 native `Skill(ai-churchteam)` 호출 2회의 다음 결과가 보존돼 있다.

- `success: true`
- `commandName: ai-churchteam`
- 선택 route: `/팀-분기`

fresh 격리 호출과 기존 native Skill 도구 실측 결과가 동일하게 수렴했다.

### 비변경 검증

- 대상 프로젝트 tracked 변경: 0건
- state write: 0건
- 산출물 생성·수정: 0건

## 5. 작업 경계

### Skill 단독 가능

- 요청 분류
- `/팀`, `/팀-전략분석`, `/팀-연간계획`, `/팀-월간`, `/팀-분기`, `/팀-건강` 진입점 선택
- 승인 필요 여부 안내
- 목회철학 SOT·신학 필터·state 권한·bridge 보호장치 안내
- `$theological-reasoning`, `$health-dashboard` 후속 Skill 선택

### workflow 필수

- 실제 팀·agent 소환
- 순차·병렬 실행
- 실제 사역 산출물 작성
- `workflow-state.yaml` 진행상태 기록
- `state.yaml` 최종 갱신
- downstream weekly-works·church-admin 실행

## 6. 전체 조직 설정에서 발견된 운영 리스크

루트 전체 설정은 약 493개 Skill, 약 26만 토큰을 적재해 호출 예산을 소진할 수 있다. 이는 `ai-churchteam` 기능 결함이 아니라 전체 설정범위의 성능·비용 문제다.

- 프로젝트 설정만 격리하면 정상 발동
- 전체 설정 적재에서는 budget-exhausted 가능
- `--bare`는 custom Skill 자체를 끄므로 검증 방식으로 사용할 수 없음

운영 시 AI_churchteam 프로젝트 컨텍스트 또는 project setting 범위에서 발동하는 것이 안전하다.

## 7. “계속 누락” 근인

반복 누락은 두 단계로 나뉜다.

### A. 최초 누락 — 확인 자체가 미완료

7월 28일에는 `c501c71` wrapper commit/push와 정적 검증만 보고됐다. “푸시한 것이 실제 Skill 도구로 발동 가능한가”라는 주인님 질문에 필요한 런타임 실측은 그 시점에 완료되지 않았다.

CEO 핸드오프도 이를 “푸시는 완료됐으나 스킬베이스 판정은 절반 미이행”으로 기록했다.

즉 최초 누락은 **push 완료를 과업 완료로 오인한 범위 관리 실패**다.

### B. 후속 누락 — 검수는 했지만 CEO 직접 완료회신이 없음

7월 29일 14:16의 실발동 보고와 17:16의 푸시본 검수보고에는 결과가 존재하고 COO 취합에도 반영됐다. 그러나 CEO 직접 outbox에는 다음 완료회신 기록이 없었다.

- 검수 대상 커밋
- native Skill 발동 결과
- 최종 경계 판정
- 과업 CLOSED 선언

즉 후속 누락은 **산출물 작성과 COO 취합을 CEO 직접 전달 완료로 잘못 간주한 전달경로 실패**다.

### 혼동을 키운 표현

7월 28일 일일보고의 “전환완료·잔여 0”은 wrapper 등록 범위만 의미했다. 그러나 적용범위를 명시하지 않아 “실제 Skill 발동 검수까지 완료”로 읽힐 수 있었다.

## 8. 재발 방지

1. “커밋·push”와 “런타임 발동 검수”를 별도 체크박스로 관리한다.
2. Skill 과업은 아래 4개 evidence가 모두 있어야 CLOSED 처리한다.
   - 원격 계보 포함
   - registry·frontmatter 정합
   - native Skill 도구 `success`
   - 실제 route 결과
3. “잔여 0”에는 반드시 적용범위를 붙인다.
   - 예: `wrapper 등록 잔여 0`
   - 예: `실발동 검수 잔여 0`
4. 주인님 직접지시는 COO 취합 여부와 별개로 CEO 직접 완료회신까지 전달상태를 추적한다.
5. 보고서 파일 생성만으로 완료 처리하지 않고, 수신자 outbox 전송기록과 CLOSED 회신을 함께 확인한다.

## 9. 근거

- native Skill 실제발동:
  `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/개발본부/점검보고/0729_AI_churchteam_스킬발동실측/EVIDENCE_실제발동.md`
- 작업경계 보고:
  `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/개발본부/점검보고/0729_AI_churchteam_스킬발동실측/AI_churchteam_스킬발동_경계점검보고.md`
- 푸시본 검수:
  `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/개발본부/점검보고/0729_AI_churchteam_푸시본_스킬베이스_검수/AI_churchteam_푸시본_스킬베이스_검수보고.md`
- 최초 누락 확인:
  `/Users/kylechoi/Desktop/Ai_works/_round/CEO_핸드오프_2026-07-28.md`
- 경영본부 판정보고:
  `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/판정/0728_ai_churchteam_스킬워크플로우판정/판정보고.md`
