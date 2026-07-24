---
name: skill-design
description: 스킬 제작의 설계 단계. 사용자가 "스킬 설계 시작", "설계 시작해", "설계 해줘", "문서 작성 시작", "/skill-design" 을 입력하면 반드시 이 스킬을 사용한다. 사용자가 커스텀 트리거를 추가하면 description에 등록한다.
---

# Skill Design — 설계 단계

`.claude/commands/skill-design.md` 의 내용을 그대로 따른다.

## 트리거 안내

처음 실행 시 아래 안내를 출력한다:

```
기본 트리거: "스킬 설계 시작", "설계 시작해", "설계 해줘", "문서 작성 시작", "/skill-design"

추가로 원하는 트리거 문구가 있으면 알려주세요.
이 파일(.claude/skills/skill-design/SKILL.md)의 description에 등록해드립니다.
```

사용자가 추가 트리거를 알려주면 즉시 이 파일의 description 줄 끝에 추가한다.
