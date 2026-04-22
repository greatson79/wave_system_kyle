# Harness Template 사용법

---

## 0. 처음 한 번만 — 템플릿 복사

```bash
cp -r harness-template my-skill-project
cd my-skill-project
```

git을 사용할 경우 (선택):
```bash
git init
git add -A
git commit -m "init: harness template"
```

---

## 1. 기획 — `/skill-plan`

Claude에게 입력:
```
/skill-plan
```

Claude가 먼저 **기획 계획을 보고**한다. 승인하면 5개 질문 인터뷰 시작.  
완료 시 `docs/skill-brief.md` 자동 생성.

---

## 2. 설계 — `/skill-design`

```
/skill-design
```

Claude가 **설계 계획을 보고**한다. 승인하면 문서 5종 + Step 파일 작성.  
완료 시:
- `CLAUDE.md`
- `docs/PRD.md`, `ARCHITECTURE.md`, `ADR.md`
- `phases/0-mvp/step*.md`

---

## 3. 점검 — `/skill-review 1` → `2` → `3`

순서대로 3회 실행. 각 회차가 **통과**되어야 다음으로 넘어간다.

```
/skill-review 1   ← 문서 완성도 + 기능 완성도
/skill-review 2   ← 구조 안전성 + 문서 간 충돌
/skill-review 3   ← 엣지케이스 + 잠재 오류 최종 확인
```

미통과 항목이 나오면 해당 문서를 수정하고 **같은 회차를 재실행**.  
3차까지 통과하면 구현으로 진행.

---

## 4. 구현 — `/skill-build`

```
/skill-build
```

Claude가 **구현 계획을 보고**한다. 승인하면 자동 실행:

```bash
python3 scripts/execute.py 0-mvp
```

Step별 완료 보고를 받으며 진행. 완료 후 빌드/테스트 자동 검증.

---

## 전체 흐름 요약

```
/skill-plan
    ↓ (docs/skill-brief.md 생성)
/skill-design
    ↓ (문서 5종 + step 파일 생성)
/skill-review 1  →  보완 → 재실행
    ↓ 통과
/skill-review 2  →  보완 → 재실행
    ↓ 통과
/skill-review 3  →  보완 → 재실행
    ↓ 통과
/skill-build
    ↓
완성
```

---

## 중간에 멈췄다면

```bash
# step이 error로 끝난 경우
# phases/0-mvp/index.json 열어서
# "status": "error" → "pending", error_message 삭제 후

python3 scripts/execute.py 0-mvp
```

설계가 잘못됐다고 판단되면 `/skill-design` 으로 돌아가 문서 수정 후 점검 재실행.

---

## 기존 프로젝트에 템플릿만 채우고 싶다면

```
/harness-init
```

`{{placeholder}}` 토큰만 인터뷰로 채워준다. 이미 채워진 파일은 스킵.

---

## 커맨드 전체 목록

| 커맨드 | 단계 | 역할 |
|--------|------|------|
| `/skill-plan` | 기획 | 인터뷰 → skill-brief.md 생성 |
| `/skill-design` | 설계 | 문서 5종 + Step 파일 작성 |
| `/skill-review 1` | 점검 1차 | 문서 완성도 + 기능 완성도 |
| `/skill-review 2` | 점검 2차 | 구조 안전성 + 문서 간 충돌 |
| `/skill-review 3` | 점검 3차 | 엣지케이스 + 잠재 오류 |
| `/skill-build` | 구현 | execute.py 실행 + step별 보고 |
| `/harness-init` | 초기화 | placeholder 인터뷰로 채우기 |
| `/harness` | step 설계 | Claude가 step 초안 생성 |
| `/review` | 최종 검토 | 전체 완성도 체크 |
