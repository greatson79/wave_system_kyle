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
