# t3 Skills & Hooks Developer — Summary

- **차수/축**: 3차 / 코딩·구현
- **핵심 발견**: 레이어 분리가 답이다. **General(`val/*`) 은 부모 게놈 그대로 + Specific(`skill/*`) 에 도메인 검증** 을 둔다. 둘은 이름공간 prefix 로 충돌 방지.
- **태그**: 3.1 `[LOCAL-OK]`, 3.2 `[LOCAL-OK]`.
- **신학·SOT 검증 위치**: skill/sermon/rules/ + skill 전용 validator. SOT-pin checker(sermon-plan-2026.json JSONPath) 도 skill/sermon 안.
- **버려진 후보**: 단일 General, 단일 Specific.
- **파킹 로트**: skill 패키징·버전 관리(parking-lot 항목 #3).
- **재현 가능 근거**: 부모 게놈 11 validator + weekly-works 7 skill 구조.
