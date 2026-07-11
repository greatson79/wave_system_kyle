# 📋 실행팀장 (Execution Team Leader) 작업 추적 TODO

이 문서는 **목회사역본부 실행팀장(Sub-Master)**의 작업 수행 상태를 관리하는 SOT(Source of Truth) TODO 리스트입니다. 세션 clear 및 메모리 유실 시 이 문서를 기반으로 작업을 즉시 복원합니다.

---

## 1. 초기 각성 및 기본 셋업
- [x] **WORKER_DIRECTIVE.md 전문 독출 및 내면화**
  - *1조 (서버 최소화)*: 불필요한 서버 실행 금지, 필요한 경우 단일 인스턴스 생명주기(trap) 엄격히 관리
  - *2조 (전기능 오케스트레이션)*: 클로드 내부 툴(sub-agent, slash command, verification)을 능동 활용
  - *3조/4조 (품질/환각0 & 실측)*: 추측 금지, node check/dump-dom 등을 활용한 실측 검증 필수
  - *6조 (Gemini-Codex 협력)*: 디자인/리뷰/코드 검수 적극 협력 및 surface 통신 루프 수행
  - *10조 (막힘 즉시 보고)*: hang 방지를 위해 한 작업 5분 초과 시 즉시 보고
- [x] **보고선 및 통신 프로토콜 확인**
  - `cmux tree --all`을 통해 총괄팀장(master) 노드 동적 해소 가능 여부 검증 완료
  - 모든 `cmux send/send-key` 전송 시 `--workspace`와 `--surface` 동시 명시 규칙 준수
- [x] **TODO 관리 체계 수립**
  - 본 `TODO_execution_leader.md` 파일 생성 및 영구화
- [x] **각성 완료 보고**
  - 총괄팀장(master) 노드로 push 보고 전송 완료

## 2. 금주 정규 2건 선행 준비 (대기 중)
- [x] **SOT(설교 계획, 설교 스킬, 아티클 스킬) 읽기 및 분석**
  - *설교 본문*: 행 6:1-7 ("섬김으로 세워지는 교회" - 맥추감사주일)
  - *설교 스킬*: `sermon_SKILL.md` (5단계 설교 프로세스) 및 `mode_b.md` (서사 텍스트 N기법/2ST 구조) 분석 완료
  - *아티클 스킬*: `brunch-writing-workflow-SKILL.md` (브런치 5단계 프로세스 및 문체 규율) 분석 완료
- [x] **소환 주체 및 과업 보고선 전송 완료**
  - 총괄팀장(ws1/s28) 및 COO(ws1/s54)에 주인님 직접명령 착수 push 보고 전송 완료
- [x] **선행 '준비' 자료 취합 및 패키징 완료**
  - [sermon-prep-package.md](file:///Users/kylechoi/Desktop/Ai_works/Claude_skills/weekly-works/output/7%EC%9B%94/1%EC%A3%BC%EC%B0%A8/%EC%84%A4%EA%B5%90/sermon-prep-package.md) 파일 생성 완료 (원어 분석, 역사문화 배경, Tim Keller/Bryan Chapell 신학 통찰, 아티클 소스 취합)
  - COO(ws1/s54)에게 선행 준비자료 완료 push 보고 완료
- [ ] **내일(금 7/3) 정규 2건 본격 산출 착수 대기 (디딤팀장과 연계 대기)**

