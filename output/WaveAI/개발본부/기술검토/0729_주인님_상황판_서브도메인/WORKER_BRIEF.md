# 워커 과업 — 주인님 상황판 비공개 서브도메인

역할: 개발본부 기술조사 워커. 구축은 금지하고 비교안 근거만 조사한다.

## 정본

- `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/상황판.html`
- `/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/serve_board.py`
- 현재 로컬 `127.0.0.1:8788`, 응답은 `_수신함.jsonl`에 기록.

## 후보

1. Vercel 서브도메인 + 인증 + 서버리스 수신(KV/Blob/Postgres 등)
2. Cloudflare Access + Workers/KV 또는 D1
3. 로컬 유지 + Tailscale Funnel/Serve 또는 동등한 사설 터널

필요하면 응답 브리지 변형안을 보조안으로 추가할 수 있다.

## 비교축

- 주인님 휴대폰 접근 편의
- 주인님 1인 인증 강도
- 클릭 응답이 로컬 CEO에 도달하는 end-to-end 경로와 유실/중복/재전송
- 구축시간, D-4 유사 긴급도, 비용
- 내부 조직 정보의 외부 저장·캐시·로그·백업 노출
- 기존 wave-homepage/Vercel 계보와 분리 가능성
- 공급자 종속, 운영·키회전·장애 복구

## 조사 규율

- 최신 기능·가격·제약은 Vercel, Cloudflare, Tailscale 공식 문서만 사용하고 URL과 확인일을 기록한다.
- Vercel Password Protection의 요금제 제약, Cloudflare Access 무료 좌석/OTP, Tailscale Serve/Funnel의 public/private 차이를 반드시 확인한다.
- “정적 배포만 하면 응답 전달이 끊김”을 전제로 push/pull/webhook/로컬 poller를 비교한다.
- 코드·DNS·배포·계정·터널 생성·외부 업로드는 0건이어야 한다.

## 산출물

아래 파일에 근거 메모·후보별 PASS/PARTIAL/FAIL·권고 초안을 저장한다.

`/Users/kylechoi/Desktop/Ai_works/output/WaveAI/개발본부/기술검토/0729_주인님_상황판_서브도메인/WORKER_RESEARCH.md`
