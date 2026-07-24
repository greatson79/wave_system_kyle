---
name: skill-build
description: 스킬 제작의 구현 단계. 사용자가 "구현 시작", "빌드 시작해", "만들어줘", "실행해줘", "/skill-build" 을 입력하면 반드시 이 스킬을 사용한다. 사용자가 커스텀 트리거를 추가하면 description에 등록한다.
---

# Skill Build — 구현 단계

`.claude/commands/skill-build.md` 의 내용을 그대로 따른다.

## 트리거 안내

처음 실행 시 아래 안내를 출력한다:

```
기본 트리거: "구현 시작", "빌드 시작해", "만들어줘", "실행해줘", "/skill-build"

추가로 원하는 트리거 문구가 있으면 알려주세요.
이 파일(.claude/skills/skill-build/SKILL.md)의 description에 등록해드립니다.
```

사용자가 추가 트리거를 알려주면 즉시 이 파일의 description 줄 끝에 등록한다.
