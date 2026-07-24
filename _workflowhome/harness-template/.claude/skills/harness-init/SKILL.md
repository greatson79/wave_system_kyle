---
name: harness-init
description: Harness 템플릿 초기화 스킬. 사용자가 /harness-init을 입력하거나 "템플릿 채우기", "프로젝트 초기화", "harness 설정"을 언급할 때 반드시 사용. CLAUDE.md·PRD.md·ARCHITECTURE.md·ADR.md·UI_GUIDE.md 내 {{placeholder}}를 인터뷰 후 일괄 치환.
---

# Harness Init Skill

harness-template의 `{{placeholder}}` 토큰을 사용자 인터뷰 후 실제 값으로 교체한다.
문서별 순서(CLAUDE → PRD → ARCHITECTURE → ADR → UI_GUIDE)로 진행하며, 이미 채워진 파일은 스킵한다.

---

## 전제 확인

시작 전 아래를 확인한다:

1. **남은 placeholder 탐지** — 작업 디렉토리에서 실행:
   ```bash
   grep -rhoE '\{\{[^}]+\}\}' . | sort -u
   ```
   결과가 없으면 "이미 모두 채워졌습니다" 메시지 출력 후 종료 (멱등성 보장).

2. **작업 범위 고지** — 치환할 파일 목록을 사용자에게 보여준다:
   ```bash
   grep -rlE '\{\{[^}]+\}\}' . --include="*.md" --include="*.json"
   ```

---

## 인터뷰 순서

각 단계마다: 질문 → 사용자 답변 → 확인 → 다음 단계. 한 단계 완료 후 다음으로 넘어간다.

### 단계 1 — 프로젝트 공통 (모든 파일에 사용)

```
다음 정보를 알려주세요:

1. 프로젝트 이름 ({{PROJECT_NAME}}):
   예) "Wave Academy 수강관리 시스템"

2. 프로젝트 목표 한 줄 ({{프로젝트 목표}}):
   예) "구글 스프레드시트 기반 수강생 이수 현황 관리"

3. 설계 철학 한 줄 ({{설계 철학}}):
   예) "구글 생태계 안에서 완결되는 최소 구현. 외부 의존성 제로."

4. 빌드 커맨드 ({{BUILD_COMMAND}}):
   없으면 "없음" 입력. 예) "npm run build" / "clasp push"

5. 테스트 커맨드 ({{TEST_COMMAND}}):
   없으면 "없음". 예) "npm test" / "python -m pytest"

6. 배포 커맨드 ({{DEPLOY_COMMAND}}):
   없으면 "없음". 예) "npm run deploy" / "clasp push"
```

### 단계 2 — CLAUDE.md (기술 규칙)

```
CLAUDE.md를 채울 기술 스택 정보를 알려주세요:

1. 핵심 기술 목록 ({{기술}}):
   예) "Google Apps Script, HTML Service, Google Spreadsheet"

2. 설정파일/진입점 ({{설정파일}}):
   예) ".clasp.json, appsscript.json" / "package.json"

3. 가장 중요한 불변 규칙 ({{가장 중요한 불변 규칙}}):
   예) "원본 .gsheet는 읽기 전용. 절대 수정 금지."

4. 두 번째 불변 규칙 ({{두 번째 불변 규칙}}):
   예) "AI가 데이터를 기억으로 생성하지 않는다. 반드시 원천 파일에서 읽는다."
```

### 단계 3 — PRD.md (기능 명세)

```
핵심 기능 2개를 설명해주세요 (나머지는 사용자가 직접 추가 가능):

기능 1:
- 기능명 ({{기능명}}): 예) "드라이브 자동 스캔"
- 상황 ({{상황}}): 예) "관리자가 [스캔] 버튼 클릭"
- 시스템 처리 ({{시스템 처리}}): 예) "DriveApp으로 폴더 탐색 → 파일명 파싱 → 마스터 시트 업데이트"

기능 2:
- 기능명: ...
- 상황: ...
- 시스템 처리: ...

보안 요구사항 한 줄 ({{보안 요구사항}}):
  예) "관리자 계정으로만 접근 가능. 열람자는 개인정보 마스킹 적용."
```

### 단계 4 — ARCHITECTURE.md (구조)

```
시스템 구조 정보를 알려주세요:

1. 핵심 엔티티 2개 ({{엔티티 1}}, {{엔티티 2}}):
   예) "Student (수강생)", "Assignment (과제)"

2. 핵심 역할/레이어 ({{역할}}):
   예) "DriveScanner → DataParser → MasterWriter → WebRenderer"

3. 주요 데이터 흐름 한 줄 ({{흐름 1: 예) 사용자 등록}}):
   프로젝트 맞게 레이블 수정. 예) "수강생 등록: 폼응답 → 파싱 → 마스터시트 기록"
```

### 단계 5 — ADR.md (결정 기록)

```
가장 중요한 기술 결정 1개를 설명해주세요:

- 결정 제목 ({{결정 제목}}): 예) "Google Apps Script 웹앱 선택"
- 무엇을 결정했는가 ({{무엇을 결정했는가}}): 예) "GAS + HTML Service로 웹앱 구현. 별도 서버, DB, 호스팅 없음."
- 이유 ({{이유}}): 예) "원본 데이터가 구글 스프레드시트 → GAS 네이티브 접근 가능"
- 포기한 것 ({{포기한 것 / 감수하는 비용}}): 예) "React 불가, 실행 6분 제한, iframe 샌드박스"
```

### 단계 6 — UI_GUIDE.md (선택)

```
UI가 있는 프로젝트라면 답해주세요 (없으면 "스킵"):

- 앱 이름 ({{앱 이름}}): 예) "Wave Academy 수강관리"
- 주 브랜드 색상 헥스 ({{#hex}}): 예) "#1a73e8"
- 메인 화면 구성 한 줄 ({{메인 화면}}): 예) "헤더(탭) + 클래스 카드 그리드 + 수강생 테이블"
```

---

## 치환 실행

인터뷰 완료 후 수집한 값을 파일별로 일괄 치환한다.

### 치환 전략
- `sed -i` 또는 Python으로 `{{token}}` → `값` 교체
- 파일당 치환 후 남은 `{{...}}` 목록 출력 (사용자가 직접 채울 항목 안내)
- 원래 파일을 직접 수정 (백업 불필요 — git으로 복구 가능)

### 치환 실행 예시
```python
import re, pathlib

replacements = {
    "PROJECT_NAME": "Wave Academy 수강관리 시스템",
    "BUILD_COMMAND": "clasp push",
    # ... 수집한 모든 값
}

for path in pathlib.Path(".").rglob("*.md"):
    text = path.read_text()
    for token, value in replacements.items():
        text = text.replace(f"{{{{{token}}}}}", value)
    path.write_text(text)
```

치환 후 검증:
```bash
grep -rE '\{\{[^}]+\}\}' . --include="*.md" | grep -v "SKILL.md"
```
남은 항목이 있으면 목록을 사용자에게 보여주고 "직접 편집하거나 다시 실행하세요" 안내.

---

## 완료 후 안내

```
✅ 초기화 완료!

채워진 파일:
- CLAUDE.md
- docs/PRD.md
- docs/ARCHITECTURE.md
- docs/ADR.md
- docs/UI_GUIDE.md (선택)

다음 단계:
1. 각 파일을 열어 세부 내용 보완 (특히 PRD의 기능 목록, ADR의 추가 결정들)
2. /harness 실행 → Claude가 step 초안 생성
3. python3 scripts/execute.py 0-mvp 로 자동 실행

남은 {{placeholder}} 있음? 위 grep 결과 확인 후 직접 편집하세요.
```
