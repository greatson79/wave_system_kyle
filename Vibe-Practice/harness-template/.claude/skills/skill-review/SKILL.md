---
name: skill-review
description: 스킬 제작의 점검 단계. 사용자가 "점검 시작", "리뷰 해줘", "점검해줘", "검토 시작", "/skill-review", "/skill-review 1", "/skill-review 2", "/skill-review 3" 을 입력하면 반드시 이 스킬을 사용한다. 사용자가 커스텀 트리거를 추가하면 description에 등록한다.
---

# Skill Review — 점검 단계

`.claude/commands/skill-review.md` 의 내용을 그대로 따른다.

## 회차 판단

사용자가 회차를 명시하지 않은 경우 아래 순서로 판단한다:
1. `output/{스킬명}/` 안에 `skill-brief.md`만 있으면 → 1차
2. 설계 문서(PRD, ARCHITECTURE 등)가 있으면 → 2차
3. 1·2차 점검 결과 파일이 있으면 → 3차

## 트리거 안내

처음 실행 시 아래 안내를 출력한다:

```
기본 트리거: "점검 시작", "리뷰 해줘", "점검해줘", "검토 시작", "/skill-review 1|2|3"

추가로 원하는 트리거 문구가 있으면 알려주세요.
이 파일(.claude/skills/skill-review/SKILL.md)의 description에 등록해드립니다.
```

사용자가 추가 트리거를 알려주면 즉시 이 파일의 description 줄 끝에 추가한다.
