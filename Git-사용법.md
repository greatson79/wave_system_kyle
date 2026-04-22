# Git 사용법 완벽 가이드

> church-automation 프로젝트를 위한 Git 워크플로우

---

## 📚 목차

1. [기본 워크플로우](#-기본-워크플로우)
2. [브랜치 전략](#-브랜치-전략)
3. [자주 사용하는 명령어](#-자주-사용하는-명령어)
4. [실전 시나리오](#-실전-시나리오)
5. [문제 해결](#-문제-해결)
6. [팁과 주의사항](#-팁과-주의사항)

---

## 🚀 기본 워크플로우

### 작업 시작부터 GitHub 업로드까지

#### 1단계: 작업 환경 준비

```bash
# 프로젝트 폴더로 이동
cd "/Users/kylej.choi/Desktop/Ai works/Claude skills"

# 현재 상태 확인
git status

# 최신 상태로 업데이트 (다른 곳에서 작업했을 경우)
git pull origin main
```

#### 2단계: 작업하기

파일을 수정/추가/삭제합니다.
- 매일묵상 콘텐츠 생성
- 수요기도회 자료 작성
- 코드 수정 등

#### 3단계: 변경사항 확인

```bash
# 어떤 파일이 변경되었는지 확인
git status

# 변경 내용 자세히 보기 (선택사항)
git diff

# 특정 파일의 변경사항만 보기
git diff 파일명
```

#### 4단계: Staging (변경사항 등록)

```bash
# 모든 변경사항 추가
git add .

# 특정 파일만 추가
git add 매일묵상/output/week-8_2026-02-23/
git add 수요기도회/output/

# 특정 확장자 파일만 추가
git add *.html

# Staging 상태 확인
git status
```

#### 5단계: Commit (저장)

```bash
# 커밋 메시지와 함께 저장
git commit -m "커밋 메시지 내용"
```

**커밋 메시지 규칙:**
- `feat:` - 새로운 기능 추가
- `fix:` - 버그 수정
- `docs:` - 문서 수정
- `style:` - 코드 포맷팅
- `refactor:` - 코드 리팩토링
- `chore:` - 기타 작업

**예시:**
```bash
git commit -m "feat: week-8 매일묵상 콘텐츠 추가"
git commit -m "fix: 수요기도회 템플릿 오류 수정"
git commit -m "docs: README 업데이트"
```

#### 6단계: GitHub 업로드

```bash
# GitHub로 전송
git push origin main
```

#### 7단계: 확인

```bash
# 브라우저로 열기
open https://github.com/greatson79/church-automation

# 또는 CLI로
gh repo view greatson79/church-automation --web
```

### ⚡ 전체 과정 요약 (한 번에)

```bash
cd "/Users/kylej.choi/Desktop/Ai works/Claude skills"
git status
git add .
git commit -m "작업 내용 설명"
git push origin main
```

---

## 🌿 브랜치 전략

### 언제 브랜치를 사용할까?

#### ✅ 브랜치 사용 권장

- 새로운 자동화 스크립트 추가
- 템플릿 대폭 수정
- 실험적인 기능 테스트
- 다른 사람과 협업

#### ❌ 브랜치 불필요

- 주간 콘텐츠 생성
- 오타 수정
- 작은 개선사항
- 문서 업데이트

### 브랜치 기본 명령어

```bash
# 새 브랜치 생성 및 이동
git checkout -b feature/새기능

# 브랜치 목록 보기
git branch

# 다른 브랜치로 전환
git checkout 브랜치명

# 브랜치에서 작업 및 커밋
git add .
git commit -m "feat: 새 기능 추가"
git push origin feature/새기능

# main으로 돌아가기
git checkout main

# 브랜치를 main에 합치기
git merge feature/새기능

# main을 GitHub에 업로드
git push origin main

# 브랜치 삭제
git branch -d feature/새기능

# 원격 브랜치도 삭제
git push origin --delete feature/새기능
```

### 추천 브랜치 전략

#### 심플 전략 (현재 사용 중)

```
main (production)
  ↓
매주 직접 커밋
```

**사용 시기:** 일상적인 콘텐츠 생성

#### 하이브리드 전략

```
main (안정 버전)
  ↓
feature/* (새 기능)
```

**사용 시기:** 큰 변경 작업

---

## 📖 자주 사용하는 명령어

### 기본 명령어

```bash
# 현재 상태 확인
git status

# 변경사항 보기
git diff

# 커밋 히스토리 보기
git log
git log --oneline
git log --oneline -5  # 최근 5개만

# 특정 파일의 히스토리
git log -- 파일명

# 원격 저장소 확인
git remote -v

# 원격 저장소와 동기화
git pull origin main
```

### 취소/되돌리기

```bash
# Staging 취소 (add 취소)
git restore --staged 파일명
git restore --staged .  # 전체

# 파일 변경사항 취소 (주의: 복구 불가)
git restore 파일명
git checkout .  # 전체

# 마지막 커밋 취소 (파일은 유지)
git reset --soft HEAD~1

# 마지막 커밋 취소 (변경사항도 삭제, 주의!)
git reset --hard HEAD~1

# 커밋 메시지 수정
git commit --amend -m "새로운 메시지"

# 이미 push한 커밋 수정 (주의: force push)
git commit --amend -m "수정된 메시지"
git push -f origin main
```

### 브랜치 관리

```bash
# 브랜치 생성
git branch 브랜치명

# 브랜치 생성 + 이동
git checkout -b 브랜치명

# 브랜치 목록
git branch          # 로컬
git branch -a       # 로컬 + 원격
git branch -r       # 원격만

# 브랜치 이동
git checkout 브랜치명

# 브랜치 삭제
git branch -d 브랜치명       # 안전한 삭제
git branch -D 브랜치명       # 강제 삭제

# 원격 브랜치 삭제
git push origin --delete 브랜치명
```

### 기타 유용한 명령어

```bash
# 특정 커밋으로 이동
git checkout 커밋해시

# 태그 생성
git tag v1.0.0
git push origin v1.0.0

# stash (임시 저장)
git stash           # 현재 변경사항 임시 저장
git stash list      # stash 목록
git stash pop       # stash 복원 및 삭제
git stash apply     # stash 복원만

# 파일 무시 (이미 추적 중인 파일)
git rm --cached 파일명
git rm -r --cached 폴더명/
```

---

## 🎯 실전 시나리오

### 시나리오 1: 주간 콘텐츠 생성

```bash
cd "/Users/kylej.choi/Desktop/Ai works/Claude skills"
# /weekly-devotion 8 실행
# /insert-images 8 ~/images/week-8/ 실행
git add 매일묵상/output/week-8_2026-02-23/
git commit -m "feat: week-8 매일묵상 콘텐츠 추가"
git push origin main
```

### 시나리오 2: 새 템플릿 개발

```bash
# 브랜치 생성
git checkout -b feature/new-template

# 작업
# (템플릿 파일 수정)

# 커밋
git add 매일묵상/.claude/skills/weekly-devotion/templates/
git commit -m "feat: 새로운 A4 템플릿 추가"
git push origin feature/new-template

# 테스트 완료 후 main에 합치기
git checkout main
git merge feature/new-template
git push origin main

# 브랜치 삭제
git branch -d feature/new-template
```

### 시나리오 3: 긴급 수정

```bash
# 잘못된 커밋 수정
git commit --amend -m "fix: 올바른 커밋 메시지"
git push -f origin main

# 또는 이전 버전으로 되돌리기
git log --oneline
git reset --hard 커밋해시
git push -f origin main
```

### 시나리오 4: 실수로 잘못 커밋한 경우

```bash
# 마지막 커밋만 취소 (변경사항은 유지)
git reset --soft HEAD~1

# 원하는 파일만 다시 add
git add 원하는파일.html

# 다시 커밋
git commit -m "올바른 커밋"
git push origin main
```

---

## 🔧 문제 해결

### 문제 1: push가 거부됨

```bash
# 오류: ! [rejected] main -> main (fetch first)

# 해결: 먼저 pull 받기
git pull origin main

# 충돌 발생 시
# 1. 충돌 파일 수동 수정
# 2. 수정 완료 후
git add .
git commit -m "merge: 충돌 해결"
git push origin main
```

### 문제 2: 큰 파일 push 실패

```bash
# 오류: File xxx is 101 MB; this exceeds GitHub's file size limit

# 해결 1: .gitignore에 추가
echo "큰파일.pdf" >> .gitignore
git rm --cached 큰파일.pdf
git commit -m "chore: 큰 파일 제거"

# 해결 2: Git history에서 완전 제거
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch 큰파일.pdf' \
  --prune-empty --tag-name-filter cat -- --all
git push -f origin main
```

### 문제 3: 잘못된 브랜치에서 작업

```bash
# main에서 작업했는데 브랜치에서 했어야 하는 경우

# 변경사항 임시 저장
git stash

# 새 브랜치 생성 및 이동
git checkout -b feature/작업내용

# 변경사항 복원
git stash pop

# 커밋 및 push
git add .
git commit -m "feat: 작업 내용"
git push origin feature/작업내용
```

### 문제 4: 커밋 메시지 오타

```bash
# 아직 push 안 한 경우
git commit --amend -m "올바른 메시지"

# 이미 push한 경우 (주의: force push)
git commit --amend -m "올바른 메시지"
git push -f origin main
```

---

## 💡 팁과 주의사항

### ✅ 좋은 습관

1. **자주 커밋하기**
   - 작은 단위로 자주 커밋
   - 한 커밋에 한 가지 목적만

2. **명확한 커밋 메시지**
   - 무엇을 왜 변경했는지 명확히
   - 규칙 준수 (feat:, fix:, docs: 등)

3. **작업 전 pull 받기**
   ```bash
   git pull origin main
   ```

4. **push 전 상태 확인**
   ```bash
   git status
   git log --oneline -3
   ```

5. **.gitignore 활용**
   ```
   *.pdf
   *.zip
   node_modules/
   .DS_Store
   ```

### ❌ 피해야 할 것

1. **절대 하지 말 것**
   - 비밀번호, API 키 커밋
   - 100MB 이상 파일 커밋
   - 의미 없는 커밋 메시지 ("수정", "ㅁㄴㅇㄹ")

2. **신중하게 사용**
   - `git push -f` (force push)
   - `git reset --hard`
   - `git clean -f`

3. **확인 필수**
   - `git add .` 전에 `git status` 확인
   - 큰 변경 전에 브랜치 생성 고려

### 🎁 단축 명령어 설정

```bash
# Git alias 설정
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
git config --global alias.lg "log --oneline --graph"

# 사용 예
git st      # = git status
git co main # = git checkout main
git lg      # = git log --oneline --graph
```

### 📋 체크리스트

**커밋 전:**
- [ ] `git status`로 변경사항 확인
- [ ] 불필요한 파일 제외했는지 확인
- [ ] 민감한 정보 포함되지 않았는지 확인
- [ ] 커밋 메시지 작성 준비

**Push 전:**
- [ ] 로컬에서 테스트 완료
- [ ] 커밋 메시지 확인
- [ ] 의도한 파일만 포함되었는지 확인

---

## 📚 참고 자료

### 공식 문서
- [Git 공식 문서](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)

### 유용한 명령어 모음

```bash
# 현재 프로젝트 상태 한눈에 보기
git log --oneline --graph --all --decorate

# 특정 파일의 변경 히스토리
git log -p 파일명

# 누가 언제 수정했는지 확인
git blame 파일명

# 검색
git log --all --grep="검색어"
git log -S "코드내용"
```

---

## 🔗 Quick Links

- **Repository**: https://github.com/greatson79/church-automation
- **계정**: greatson79
- **메인 브랜치**: main

---

**마지막 업데이트**: 2026-02-13
**작성자**: Claude Code Assistant
