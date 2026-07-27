# WordPress 미디어 업로드 500 진단 기록 — 2026-07-27

## 범위와 보안

- 이 기록은 주간작업의 WordPress 이미지 업로드를 제거하기 전 수행한 읽기·승인된 테스트 결과다.
- 인증값, 응답 원문, 절대 서버 경로는 기록하지 않는다.
- 서버 설정 변경, 플러그인 비활성화, 재시작, 테스트 미디어 삭제는 수행하지 않았다.

## 재현 결과

- 10KB 이하의 작은 PNG 1건과 약 2.5MB의 문제 PNG 1건을 각각 REST 미디어 엔드포인트에 업로드했다.
- 두 요청 모두 HTTP 500과 `rest_upload_sideload_error`로 실패했다.
- 정제된 오류 의미는 업로드 파일을 `wp-content/uploads`로 이동할 수 없다는 것이었다.
- 공개 site-health directory-sizes 응답에서 uploads 사용량은 761.21MB(798,187,256 bytes)였다. 가용 용량·쿼터 필드는 제공되지 않았다.

## 결론과 후속 읽기점검

파일 크기, 인증, 미디어 REST route 자체는 주원인에서 배제됐다. 서버 관리 읽기접근으로 다음 세 축을 확인해야 세부 원인을 확정할 수 있다.

1. `wp-content/uploads`와 상위 경로의 권한·소유자
2. 디스크 여유공간·호스팅 쿼터
3. PHP `upload_tmp_dir` 및 PHP/WordPress 오류 로그

서버 측 변경은 별도 승인 후에만 수행한다. 복원 근거는 Git 이력 `6c17bdb`와 이 문서이며, 활성 주간작업에는 WordPress 업로드 코드를 보관하지 않는다.

## 업로드 제거 TDD 기록

- RED(구현 전): 동일한 subprocess fixture를 `<tmp>/src/scripts/insert-images.py`와 `<tmp>/output/...` 구조로 실행했다. `.wp-config.json`이 없는 fixture에서 `FileNotFoundError`로 종료됐으며, 오류 대상은 `.wp-config.json`이었다.
- GREEN(구현 후): `tests/test_insert_images_local_only.py`의 A는 `.wp-config.json` 없이, B는 유효한 구 형식 fixture config가 있어도 성공해야 한다. B는 가짜 `requests.post`가 호출되지 않는지까지 확인한다. 두 테스트 모두 5일 × 3 HTML 변형의 두 placeholder가 `../images/{day}.png`로 바뀌고 WordPress 업로드 stdout이 없는지를 확인한다. `INSERT_IMAGES_SCRIPT` 환경변수로 검증 대상 스크립트를 교체할 수 있어, 구 구현을 지정한 B는 `NETWORK_POST_CALLED`로 RED가 된다.
