# _DEPLOY — 병합 초안 배포 매핑 (Phase 4에서 이 표대로 반영)

> 이 폴더의 초안은 **아래 최종 경로로 복사되어야** @import·상호 참조가 해소된다
> (초안 폴더 상태에서는 self-contained가 아님 — 의도된 전제).

| 초안 (_merge-draft/) | 최종 경로 (Ai_works 루트 기준) |
|---|---|
| `CLAUDE.md` | `CLAUDE.md` |
| `soul.md` | `soul.md` |
| `memory.md` | `memory.md` |
| `RECOVERY.md` | `RECOVERY.md` |
| `MASTER_DIRECTIVE.md` | `.claude/MASTER_DIRECTIVE.md` |
| `WORKER_DIRECTIVE.md` | `.claude/WORKER_DIRECTIVE.md` |
| `CSO_DIRECTIVE.md` | `.claude/CSO_DIRECTIVE.md` |
| `COO_DIRECTIVE.md` | `.claude/COO_DIRECTIVE.md` |

- 반영 절차: 주인님 diff 승인(Phase 3) → 위 경로로 복사 → **헌장 파일만** 외과적 `git add`·커밋.
- 롤백: `.claude/_legacy-cmux/` 원본 복사로 즉시 복원.
- 배포 후 검증: 새 세션에서 CLAUDE.md 로드 → @import 4종 해소 확인 → "너는 마스터다" 부트 스모크.

> ★**주의(2026-07-22 CSO 발견)**: 이 폴더의 `CLAUDE.md` 초안은 "cmux/wmux 폐기, CYS 단독"
> 전제로 작성된 **구세대 초안**이라, 2026-07-10 주인님 확정(★메인 런타임=cmux.app·cys.app=보조,
> 루트 CLAUDE.md 정본)과 **정반대 내용**이다. 이 표대로 그대로 복사·배포하면 런타임 정본을
> 되돌리는 사고가 된다. **이 표는 §매핑 구조 참고용으로만 쓰고, 실제 배포 시 위 draft
> `CLAUDE.md`는 현재 루트 `CLAUDE.md`의 최신 내용으로 먼저 교체한 뒤에만 유효하다** — 이
> 표 자체를 "지금 그대로 실행 가능한 절차"로 오독 금지.

---

## ★엔진↔조직 조화 계약 (2026-07-22 CEO 지시 4항 — CSO 설계)

> 근거 티켓: `output/WaveAI/경영본부/_round/CSO_엔진조직_조화메커니즘_지시_2026-07-22.md`.
> 아래 계약 중 **DIRECTIVE·CLAUDE.md 본문 개정이 필요한 항목은 별도 표기**하고 denylist·주인님
> 게이트를 거친다 — 이 섹션 자체의 신설만으로 헌장이 바뀌지 않는다.

### 엔진→조직 (pack-update가 조직층에 영향 주는 경로)
- **게이트 = directives diff 감사**(위 §1·§2). `pack-update`로 엔진 directives(MASTER·WORKER·
  CSO·REVIEWER·RSI_LEARNING·CEO_TEMPLATE 6종)가 바뀌면, `.claude/_engine-snapshot/`과의 diff가
  **자동 감지되어야** 조직층이 무음으로 뒤처지지 않는다 — 저빈도 감시잡(설계안 §2, 승인대기)이
  이 게이트의 집행 기구다.
- **충돌 해소 원칙 = 도메인 carve-out**(현행 우선순위 유지, 뒤집지 않음): 엔진 directives는
  **메커니즘 정본**(부트시퀀스·결정론 검증·소켓·라운드루프)이고, 조직 확장층(`.claude/*_DIRECTIVE.md`·
  `org/`·루트 `CLAUDE.md`)은 **도메인·운영 정본**(Wave AI Networks 매트릭스 조직·발행 거버넌스·
  denylist)이다. 엔진이 자기 영역(메커니즘)을 바꿔도 조직층 도메인 결정을 침범하지 않고,
  그 역도 마찬가지 — 겹치는 것처럼 보이면 "이게 메커니즘이냐 도메인이냐"로 1차 분류한다.

### 조직→엔진 (조직층 학습·결정을 엔진에 반영하고 싶을 때)
- **raw 팩 직접편집 절대 금지** — `~/.cys/pack/directives/*.md`를 조직층이 직접 고치면
  다음 `pack-update`가 그 수정을 **무음으로 덮어쓴다**(엔진 자체 경고: "로컬 수정은 덮어써지며
  denylist"). 조직층 결정이 아무리 옳아도 이 경로로는 영속되지 않는다.
- **유일한 반영 경로 = 팩 `.user` heal 경로 + deploy 계약**: 엔진 pack이 지원하는 사용자
  오버레이/heal 메커니즘(존재 확인은 §2 저빈도 잡 설계 시 `cys pack --help`류로 함께 실사할
  백로그 항목)을 통해서만 조직층 결정을 엔진 쪽에 "제안"한다. 직접 대상은 공유 학습기억
  (`pack/memory`) 같은 엔진 소유 스토어이며, **거버넌스 텍스트(directives 6종) 자체를
  조직층이 엔진에 강제로 밀어넣지 않는다** — 방향이 바뀌면(조직→엔진 거버넌스 반영) 그건
  엔진 자체 개발 로드맵 문제이지 조직층 배포 문제가 아니다.
- **갭1 원칙 확인(4항 지시 3번과 동기화)**: 우리 운영기억·상태의 캐논 = `ai_works` git
  (`output/WaveAI/경영본부/_round/` 등)이다. 팩 내부 스토어(`pack/memory`·`pack/round/*TODO`)는
  엔진 소유로 격리되며, 조직층은 이를 캐논으로 의존하지 않는다 — 이미 이관 완료된 cys시대
  잔여물(`pack/round/MASTER_TODO`·`COO_TODO` 등)은 엔진 내부라 무해 방치.
