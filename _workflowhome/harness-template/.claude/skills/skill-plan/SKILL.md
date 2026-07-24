---
name: skill-plan
description: 스킬 제작의 기획 단계. 사용자가 "스킬 기획 시작", "새 스킬 만들자", "기획 시작해", "스킬 만들고 싶어", "시작하자", "/skill-plan" 을 입력하면 반드시 이 스킬을 사용한다. 사용자가 커스텀 트리거를 추가하면 description에 등록한다.
---

# Skill Plan — 기획 단계

`.claude/commands/skill-plan.md` 의 내용을 그대로 따른다.

## 트리거 안내

처음 실행 시 아래 안내를 출력한다:

```
기본 트리거: "스킬 기획 시작", "새 스킬 만들자", "기획 시작해", "스킬 만들고 싶어", "/skill-plan"

추가로 원하는 트리거 문구가 있으면 알려주세요.
이 파일(.claude/skills/skill-plan/SKILL.md)의 description에 등록해드립니다.
```

사용자가 추가 트리거를 알려주면 즉시 이 파일의 description 줄 끝에 추가한다.
