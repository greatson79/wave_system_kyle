# /harness-init

harness-template의 `{{placeholder}}` 토큰을 인터뷰 후 실제 값으로 채운다.

`harness-init` 스킬을 사용하여 실행한다.

## 실행 순서
1. 남은 placeholder 탐지 (이미 채워진 파일은 스킵)
2. 6단계 인터뷰 (공통 → CLAUDE → PRD → ARCHITECTURE → ADR → UI_GUIDE)
3. 수집한 값으로 일괄 치환
4. 남은 항목 목록 출력 및 다음 단계 안내
