# 주인님 상황판 비공개 접근·응답 전달 기술 조사

- 조사일: 2026-07-29 (KST)
- 역할/범위: 개발본부 기술조사 워커. 후보 비교와 근거 기록만 수행했다.
- 발동 스킬: `agent-reach` (공식 웹 문서 탐색 경로). `agent-reach doctor`와 Exa 호출은 현재 로컬 설치/등록 오류로 실행 불가였고, 그 실패는 아래에 남겼다. 그 뒤에도 **Vercel·Cloudflare·Tailscale의 공식 문서만** 브라우저로 직접 확인했다.
- 금지행위 확인: 코드 변경 0건, DNS 변경 0건, 배포 0건, 계정 생성·변경 0건, 터널 생성 0건, 외부 업로드 0건. 이 문서만 새로 작성했다.

## 1. 현행 정본과 문제 정의

### 1.1 로컬 실측

| 항목 | 확인 결과 | 근거 | 신뢰도 |
|---|---|---|---|
| 현행 UI의 응답 경로 | `상황판.html`은 상대경로 `POST /decision` 및 `GET /inbox`를 호출한다. | [`상황판.html`](/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/상황판.html:342), [`상황판.html`](/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/상황판.html:363), [`상황판.html`](/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/상황판.html:411) | High |
| 현행 수신·저장 | `serve_board.py`는 `POST /decision`의 값을 `_수신함.jsonl`에 append하고 `fsync`한 뒤 `GET /inbox`로 다시 읽는다. | [`serve_board.py`](/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/serve_board.py:51), [`serve_board.py`](/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/serve_board.py:72) | High |
| 외부 직접 접근 불가 | 서버는 `127.0.0.1`에만 바인딩한다. 따라서 휴대폰에서 `127.0.0.1`은 CEO Mac이 아니라 휴대폰 자신을 뜻하며, 정적 파일만 외부 배포해도 상대경로 `/decision`은 로컬 CEO 수신기로 가지 않는다. | [`serve_board.py`](/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/serve_board.py:95); IP loopback의 표준 동작에 따른 네트워크 추론 | High |
| 현재 중복 방지 수준 | UI는 `/inbox`의 마지막 응답을 표시해 재클릭을 줄이지만, 수신 서버에는 이벤트 ID, 원자적 중복 제거, 재전송 ACK 상태가 없다. | [`상황판.html`](/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/상황판.html:411), [`serve_board.py`](/Users/kylechoi/Desktop/Ai_works/output/WaveAI/경영본부/대시보드/0729_주인님_상황판/serve_board.py:72) | High |

**판정:** 외부 정적 배포만으로는 화면 열람은 가능해도 클릭 응답의 CEO Mac 도달 계약이 끊긴다. 외부 배포안에는 별도 응답 브리지(원격 저장소 + 로컬 puller, 또는 인증된 수신 webhook)가 필수다.

## 2. 공식 자료 확인표

모든 URL은 2026-07-29 KST에 재확인했다. 아래 외의 비공식 글·가격비교 사이트는 채택하지 않았다.

| ID | 공식 자료·확인 사실 | URL | 신뢰도 |
|---|---|---|---|
| V1 | Vercel Password Protection은 Enterprise 또는 Pro의 Advanced Deployment Protection add-on에서만 가능하다. Pro add-on은 월 $150이며, 최소 30일 사용 후 해지 가능하다. | [Vercel Deployment Protection](https://vercel.com/docs/deployment-protection) | High |
| V2 | Hobby의 Vercel Authentication 표준 보호는 프로덕션 도메인을 보호하지 않는다. 프로덕션을 포함한 All Deployments 보호는 Enterprise 또는 Pro 고급 add-on이다. | [Vercel Deployment Protection](https://vercel.com/docs/deployment-protection) | High |
| V3 | Vercel Functions는 요청·응답 본문 최대 4.5 MB이며, 함수 호출 런타임 로그가 남는다. 로그 보존은 Hobby 1시간, Pro 1일, Enterprise 3일이다. | [Functions limitations](https://vercel.com/docs/functions/limitations), [Runtime Logs](https://vercel.com/docs/logs/runtime) | High |
| V4 | Vercel Blob은 전 플랜에서 가능하지만 Blob은 객체 저장소이고, KV·Postgres는 현재 Marketplace의 외부 공급자 통합으로 선택한다. | [Vercel Storage overview](https://vercel.com/docs/storage), [Vercel Blob pricing](https://vercel.com/docs/vercel-blob/usage-and-pricing) | High |
| C1 | Cloudflare Zero Trust Free는 가입 절차상 결제정보 입력이 필요하지만 청구되지 않는다. 기본 IdP는 Cloudflare 계정이며 OTP IdP를 추가할 수 있다. | [Cloudflare One setup](https://developers.cloudflare.com/cloudflare-one/setup/), [One-time PIN login](https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/) | High |
| C2 | Access 정책은 deny-by-default이며, `Emails` selector로 정확히 한 이메일 주소만 Allow할 수 있다. OTP만을 로그인 방법으로 포함하는 정책은 모든 유효 OTP 이메일을 허용하므로 1인 용도에는 부적합하다. | [Access policies](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/) | High |
| C3 | Access 애플리케이션/정책 세션은 즉시 만료~1개월로 설정 가능하며, 애플리케이션 기본값은 24시간이다. | [Access session management](https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/session-management/) | High |
| C4 | Workers Free는 100,000 요청/일, 10ms CPU/호출이다. Paid는 계정당 최소 월 $5이며 Workers·Pages Functions·KV 등을 포함한다. | [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/) | High |
| C5 | KV Free는 읽기 100,000/일, 쓰기·삭제·list 각 1,000/일, 1GB이고 같은 키 쓰기는 플랜과 무관하게 초당 1회 제한이다. D1 Free는 읽기 500만 행/일, 쓰기 10만 행/일, 총 저장 5GB이다. | [Workers KV pricing](https://developers.cloudflare.com/kv/platform/pricing/), [D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/) | High |
| C6 | Free Zero Trust Access 로그 보존은 24시간, 관리자 감사 로그는 18개월이다. | [Cloudflare Zero Trust logs](https://developers.cloudflare.com/cloudflare-one/insights/logs/), [Cloudflare Audit Logs v2](https://developers.cloudflare.com/fundamentals/account/account-security/audit-logs/) | High |
| T1 | Tailscale Serve는 tailnet 내부 기기만 로컬 서비스로 연결한다. tailnet ACL이 적용되고, Serve는 backend에 사용자 식별 헤더를 추가한다. | [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve) | High |
| T2 | Tailscale Funnel은 인터넷 전체에 로컬 서비스를 공개한다. Serve와 같은 포트를 함께 쓸 수 없고, Funnel 트래픽에는 Serve의 identity header가 없다. | [Tailscale Funnel](https://tailscale.com/kb/1223/funnel), [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve) | High |
| T3 | Funnel은 MagicDNS·HTTPS·policy의 funnel node attribute가 필요하고, `*.ts.net` tailnet 도메인과 443/8443/10000 포트만 쓴다. macOS에서는 오픈소스 Tailscale 앱 변형이 필요하다. | [Tailscale Funnel](https://tailscale.com/kb/1223/funnel) | High |
| T4 | Tailscale Personal은 개인·비상업 용도로 최대 6명/기기 무제한이며, Standard는 사용자당 월 $8이다. tailnet 기기간 연결은 종단간 암호화된다. | [Tailscale pricing](https://tailscale.com/pricing), [Secure the network](https://tailscale.com/kb/1429/secure) | High |

### 조사 도구 상태

- `agent-reach doctor --json`: `ModuleNotFoundError: agent_reach.cli`로 실행 실패.
- `mcporter ... exa.web_search_exa(...)`: Exa MCP 서버가 현 환경에 등록되지 않아 실패.
- 이 실패 때문에 비공식 검색 결과를 사용하지 않았다. 위 공식 문서는 브라우저로 직접 조회했다.

## 3. 후보별 판정

| 후보 | 판정 | 주인님 휴대폰 편의 / 1인 인증 | 응답의 E2E 경로 | 외부 데이터·로그 노출 | D-4·비용·계보 | 핵심 이유 |
|---|---|---|---|---|---|---|
| 1. Vercel 서브도메인 + 인증 + 함수 + 원격 저장 | **PARTIAL** | 휴대폰 브라우저는 편하지만, 비밀번호 보호는 Pro에 월 $150 고급 add-on(또는 Enterprise)이다. Vercel Authentication은 주인님 Vercel 계정 의존이다. | Phone → Vercel 보호·Function → Blob 또는 Marketplace DB/KV → **로컬 puller** → `_수신함.jsonl` | 화면·응답은 Vercel/저장 공급자에 놓인다. 함수 호출 로그도 외부에 남으며 보존기간은 플랜별 상이하다. | Vercel 계보와 논리적으로는 별도 project/domain으로 분리 가능하나, 동일 팀·계정의 배포·권한·로그 경계에 남는다. 인증 비용과 신규 응답 브리지 때문에 긴급 단기안에는 무겁다. | 화면 배포만으로는 현행 POST 계약을 보존하지 못하고, 원하는 비밀번호 인증의 가격 제약이 크다. |
| 2. Cloudflare Access + Workers + KV/D1 | **PASS (조건부)** | 휴대폰 브라우저 접근이 자연스럽다. 정확한 1개 이메일 Allow + OTP로 구성 가능하다. 단 OTP는 이메일 계정 소유에 의존하므로 그 메일 계정의 MFA·복구수단 보안이 실제 강도를 결정한다. | Phone → Access(정확한 이메일·OTP) → Worker → D1(권장) 또는 KV → **로컬 puller** → `_수신함.jsonl` | 정적 UI·응답 레코드는 Cloudflare에 저장된다. Access 로그는 Free 24시간, 관리자 감사 로그는 18개월이다. | Free 한도는 이 작은 응답량에 충분하나, custom hostname은 Cloudflare active zone/DNS가 필요하다. D1은 event-id 유니크 제약을 둘 수 있어 KV보다 중복 제어에 적합하다. | 외부 비공개 서브도메인이 꼭 필요할 때 가장 비용·보안·운영의 균형이 좋다. |
| 3-A. 로컬 유지 + **Tailscale Serve** | **PASS (사전조건 충족 시 최우선)** | 휴대폰과 CEO Mac이 같은 tailnet에 로그인되어야 하므로 최초 앱·로그인 마찰은 있다. 이후 URL은 브라우저로 열리고 tailnet ACL/기기 신원으로 1인 접근을 강하게 제한할 수 있다. | Phone(Tailscale) → tailnet encrypted path → Tailscale Serve → `127.0.0.1:8788` → 현행 `/decision` → 현행 `_수신함.jsonl` | 상황판 HTML과 응답 내용은 기존 CEO Mac에만 남고 별도 응답 DB·외부 정적 호스트가 없다. 단 Tailscale 관리·정책 메타데이터는 별도 서비스 영역이므로 실제 도입 전 개인정보정책/관리 로그 범위를 별도 확인해야 한다. | DNS·배포·원격 저장소가 없어 가장 짧다. 다만 URL은 custom subdomain이 아니라 `device.tailnet.ts.net`으로 제한된다. 현행 로컬 서버 계약을 그대로 보존한다. | "비공개 접근"이 목표이고 tailnet 준비가 이미 되어 있다면, 외부 노출·유실 지점·운영 부하가 가장 적다. |
| 3-B. 로컬 유지 + **Tailscale Funnel** | **FAIL (단독 사용)** | 앱 설치 없이 휴대폰 브라우저로 열 수 있지만, 인터넷 공개 URL이다. HTTPS는 전송 암호화이지 주인님 1인 인증이 아니다. | Public Internet → Funnel relay → local service → `_수신함.jsonl` | 콘텐츠와 입력 엔드포인트가 공개 도달 가능해진다. 현행 `/decision`에는 인증·권한·CSRF·서명 검증이 없다. | Funnel은 기능·정책·HTTPS 요구사항과 macOS 앱 제약도 있다. 추가 앱 수준 인증을 새로 설계하지 않는 한 D-4에 부적합하다. | Funnel은 Serve의 private 대체가 아니라 public 노출 기능이다. 현행 수신 서버와 결합하면 인증되지 않은 제3자의 입력 위험이 생긴다. |

### PASS/PARTIAL/FAIL의 의미

- **PASS:** 브리프의 휴대폰 접근·1인 인증·응답 도달·비공개성 요구를 충족할 수 있다. 조건은 명시했다.
- **PARTIAL:** 기술적으로 가능하나 가격, 외부 저장, 신규 bridge, 또는 인증 모델 때문에 현재 우선순위에는 손실이 있다.
- **FAIL:** 현행 코드와 단독 결합 시 1인 비공개 접근의 핵심 요구를 충족하지 못한다.

## 4. 정적 배포에서 반드시 추가되는 응답 브리지

### 4.1 권장 전달 계약: 원격 append + 로컬 puller (at-least-once)

정적 화면을 Vercel 또는 Cloudflare에 둘 때의 안전한 비교 기준이다. 이 절은 설계 메모이며 구현·배포 지시가 아니다.

```text
주인님 휴대폰
  └─ 인증된 HTTPS POST {event_id, no, label, answer, memo, client_at}
       └─ 원격 Function/Worker
            └─ 원격 durable store (event_id UNIQUE, received_at, delivered_at)
                 └─ CEO Mac의 outbound HTTPS poller
                      └─ 현행 _수신함.jsonl append + fsync
                           └─ 원격 delivered_at ACK
```

| 위험 | 필수 제어 | 근거/판정 |
|---|---|---|
| 휴대폰 재시도·더블 탭으로 중복 | 클라이언트가 UUID `event_id`를 매 요청에 보내고 원격 DB가 유니크 제약으로 dedupe한다. 동일 `event_id` 재요청에는 기존 결과를 반환한다. | 현행은 번호별 UI 표시만 하며 서버 dedupe가 없다. D1의 SQL 모델은 이 제어에 적합하다. KV는 동일 key 초당 1회 쓰기 제한이 있어 상태 갱신 설계가 더 까다롭다. |
| 저장 후 CEO Mac pull 전 장애 | `received`와 `delivered`를 분리한다. Mac이 append+`fsync` 성공한 뒤에만 ACK한다. poller는 미전달 이벤트를 반복 조회한다. | 현행 로컬 서버의 `fsync` 의도를 보존한다. 정확히 한 번(exactly-once)이 아니라 **중복 제거를 갖춘 at-least-once**를 목표로 한다. |
| ACK 손실 | Mac이 append 후 ACK 전 죽으면 다음 poll에서 같은 이벤트를 다시 받을 수 있다. 로컬에도 `event_id` dedupe(별도 receipt ledger 또는 append 전 검사)가 있어야 한다. | 원격 dedupe만으로 local append 중복은 막지 못한다. |
| webhook 직접 수신 | CEO Mac은 인바운드 공개 포트·터널·서명 검증·재전송 endpoint를 가져야 한다. | 브리프의 구축/터널 금지와 맞지 않으며, NAT·sleep·네트워크 변경에 취약하다. 본 비교에서는 **비권고**다. |
| 정적 캐시 | 인증된 HTML/API 응답과 응답 레코드 endpoint에 공유 캐시를 허용하지 않는 별도 정책이 필요하다. | 외부 CDN의 캐시·로그·보존 경계는 설계 시 명시해야 한다. 현재 어떤 공급자 설정도 생성·검증하지 않았다. |

### 4.2 원격 저장소 선택

- **D1 우선:** 이벤트 표·`event_id` 유니크 제약·전달 상태·정렬 조회를 한 트랜잭션 모델로 표현하기 쉬워서, 버튼 응답의 dedupe/ACK 상태에 적합하다. Free 한도도 브리프의 소량 응답에는 넉넉하다. 근거: [D1 overview](https://developers.cloudflare.com/d1/) 및 [D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/). 신뢰도 High.
- **KV 보조:** 아주 단순한 최신 상태값이나 cache에는 가능하지만, 동일 키 초당 1회 write 제약과 key-value 모델 때문에 append queue·ACK 상태의 정합성 설계가 D1보다 불리하다. 근거: [KV limits](https://developers.cloudflare.com/kv/platform/limits/). 신뢰도 High.
- **Vercel Blob 비권고:** Blob은 큰 content-addressable object 대상이다. 버튼 응답 queue의 순서·중복 제거·ACK 상태를 모델링하는 주 저장소로는 부적합하다. Vercel의 KV/Postgres는 Marketplace 외부 공급자 선택이므로 추가 데이터 경계가 생긴다. 근거: [Vercel storage overview](https://vercel.com/docs/storage). 신뢰도 High.

## 5. 비교축 상세 평가

| 비교축 | Vercel | Cloudflare Access + Workers/D1 | Tailscale Serve | Tailscale Funnel |
|---|---|---|---|---|
| 휴대폰 접근 | 매우 쉬움(브라우저) | 매우 쉬움(브라우저·OTP) | 앱/로그인 1회 필요 후 쉬움 | 매우 쉬움(브라우저) |
| 1인 인증 강도 | Vercel 계정 또는 공유 비밀번호. 비밀번호는 고급 add-on 제약. | 정확한 이메일 + OTP. 메일 계정 MFA가 사실상 핵심. | tailnet identity + ACL + 기기 접근. 가장 강함. | 단독 인증 없음 — FAIL |
| E2E 신뢰성 | 원격 store/puller 설계가 없으면 FAIL. 설계 시 at-least-once 가능. | 원격 store/puller 설계가 없으면 FAIL. D1 + poller로 at-least-once 가능. | 직접 현행 서버로 도달하므로 중간 store/poller 없음. | 직접 도달하나 공개 입력 위험. |
| 유실/중복 제어 | 새 event-id/dedupe/ACK 필요 | 새 event-id/dedupe/ACK 필요 | 현행은 서버 dedupe 부재; 네트워크 재시도 시 개선 여지 있음 | 현행 dedupe 부재 + 공격/오입력 위험 |
| 구축 시간 | 프로젝트·도메인·보호 add-on·함수·저장소·poller 필요 | zone/DNS·Access·Worker·D1·poller 필요 | 이미 가입·두 기기 준비라면 가장 짧음 | 공개 노출은 짧아도 보안 완결에는 새 인증 필요 |
| 비용 | Pro seat 비용 + 월 $150 add-on + 저장/함수 사용량 가능성 | Free 범위 가능, Paid 전환 시 최소 월 $5 | Personal은 비상업 개인 용도 6명 무료; 업무/조직은 Standard 등 적합 플랜 재확인 필요 | Funnel 자체 플랜 가능 여부와 무관하게 앱 인증 설계 비용 발생 |
| 외부 저장/로그 | 배포/함수 로그/원격 저장소 | 정적 asset/D1/Access·감사 로그 | 본문과 결정은 로컬 유지, 관리 plane 메타데이터는 별도 | 로컬 본문이나 public reachability가 노출면 확대 |
| wave-homepage/Vercel 분리 | 새 Vercel project로 논리 분리는 가능하나 계정/팀 경계는 별도 검증 필요 | Vercel 계보와 완전 분리 가능 | Vercel과 완전 분리 | Vercel과 완전 분리 |
| 키회전·장애 복구 | Vercel 보호·저장 공급자 자격증명 + poller 비밀값의 회전 계획 필요 | Access IdP/OTP, API token, Worker secret, DB/poller credential 회전 필요 | tailnet 사용자/기기 revoke·ACL·노드 교체 절차 필요 | 위 항목 + public endpoint 방어·차단·인증키 회전 필요 |

## 6. 권고 초안

### 권고 1 — 사전조건 충족 시: Tailscale Serve를 우선 검토

**판정: PASS.** CEO Mac과 주인님 휴대폰이 이미 동일 tailnet에서 승인된 계정/기기로 사용 가능하고, custom subdomain이 절대 요구사항이 아니라면 Tailscale Serve가 우선안이다.

- 현재 `/decision` → `_수신함.jsonl` → `/inbox` 계약을 그대로 이용하므로 새 원격 queue/poller와 그에 따른 유실·중복·키회전 문제가 생기지 않는다.
- Tailscale 공식 문서상 Serve는 tailnet 내부에 한정되고 ACL이 적용되며 identity header도 제공한다. Funnel과 혼동하면 안 된다.
- 단, URL은 custom domain이 아닌 `device-name.tailnet-name.ts.net`이다. 이 제약 또는 휴대폰의 Tailscale 로그인 마찰이 수용 불가하면 다음 권고로 넘어간다.

### 권고 2 — custom 비공개 서브도메인이 필수일 때: Cloudflare Access + Workers/D1

**판정: PASS (구축 승인 후).** 외부 서브도메인 브라우저 접근이 반드시 필요하면 Cloudflare Access에서 **정확히 주인님 한 이메일만 Allow**하고, OTP를 그 이메일의 MFA와 함께 쓰는 구성이 Vercel보다 현실적이다.

- D1을 source-of-truth로 하고 `event_id` 유니크/수신시각/전달 ACK 상태를 둔 outbound local poller 방식을 선택한다.
- Access 정책은 `Include: Emails = <주인님 이메일>`처럼 정확한 주소로 좁힌다. `Include: Login Methods = One-time PIN`만 둬서는 안 된다.
- 세션은 기본 24시간을 그대로 두지 말고 민감도에 맞춰 짧게 정한다. 값은 구현 승인 시 주인님이 결정해야 한다.
- Cloudflare active zone·DNS와 신규 계정/설정은 이 조사 범위에서 전혀 생성하지 않았다. 실제 도입은 별도 승인 과업이다.

### 비권고 — Vercel Password Protection 중심안과 Funnel 단독안

- **Vercel:** 기존 계보의 익숙함은 장점이지만, 원하는 프로덕션 비밀번호 보호에 월 $150 add-on이 추가되고, 응답 bridge는 별도로 여전히 필요하다. Cloudflare안보다 비용·외부 저장 경계가 불리하다.
- **Funnel:** HTTPS가 있어도 공개 URL이며 Serve identity header가 없다. 현행 무인증 `/decision`에 연결하는 것은 주인님 1인 인증 조건에 맞지 않는다.

## 7. 승인 전 확인 게이트 (실행 금지 상태)

아래 항목은 결정을 위한 확인 목록일 뿐, 이 조사에서 실행하지 않았다.

1. 주인님이 **custom subdomain 필수 여부**와 **휴대폰 Tailscale 로그인 수용 여부**를 결정한다.
2. Tailscale 우선안이면: CEO Mac/휴대폰이 동일 tailnet·승인 기기인지, 조직 용도에 맞는 플랜인지, ACL이 오직 주인님 identity를 허용하는지 독립 검증한다.
3. Cloudflare안이면: 정확한 허용 이메일, 메일 계정 MFA/복구 경로, Access session duration, 원격 데이터 보존/삭제 기간, Cloudflare active zone 및 DNS 권한의 소유자를 결정한다.
4. 원격 bridge는 먼저 **event-id dedupe + received/delivered ACK + CEO Mac 재시작 후 미전달 재처리**를 시험 기준으로 승인한다. 단순 정적 배포는 이 게이트를 통과한 것으로 간주하지 않는다.
5. 어떤 안이든 `Funnel` 또는 임의 public webhook을 현행 서버에 바로 연결하지 않는다.

## 8. 저장·검증 결과

- 이 파일은 요청된 경로에 새로 저장했다.
- 정본 코드의 응답 경로와 저장 동작은 위 1.1의 파일·줄 근거로 재확인했다.
- 외부 공식 문서는 위 2절의 공급자 공식 URL만 채택했다.
- 인프라 변경/배포/계정 생성/터널 생성/외부 업로드는 수행하지 않았다.
- 증류 대상 없음: 이번 과업은 지정 조사 산출물의 작성이며, 재사용 스킬·영구기억 신규 등록 권한은 요청 범위 밖이다.
