# Wave Content Studio User Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert Wave Content Studio from an automatic chained pipeline into a user-directed, review-gated loop at every content stage.

**Architecture:** Add a deterministic interaction-state contract to `workspace/pipeline-run-report.md`, teach the stage detector to distinguish pre-stage direction, post-stage review, revision, approval, completion, and publication states, then update every skill to obey that contract. Keep domain-quality states separate from user-review states and preserve the exact Sites publishing phrase as the final external-write gate.

**Tech Stack:** Markdown skill contracts, Bash contract validator/tests, Python publication validator, Codex plugin validation tools.

---

## File map

- `shared/policies/user-participation-loop.md`: canonical interaction states, natural-language approval rules, and per-stage loop.
- `shared/policies/workflow-gates.md`: connects existing research, overwrite, and publication gates to the user loop.
- `shared/templates/pipeline-run-report.template.md`: stores direction, result, review state, response summary, and next allowed stage.
- `scripts/validate-workflow-contract.sh`: deterministic stage detection from artifacts and the last interaction state.
- `tests/run-contract-tests.sh`: regression tests for all new interaction transitions and prior completion bugs.
- `tests/fixtures/*`: minimal project states for review, approval, revision, completion, and publication.
- `skills/content-studio-orchestrator/SKILL.md`: owns the cross-skill user loop and prevents automatic chaining.
- Six specialist `SKILL.md` files: define their pre-run question and post-run review handoff.
- `.codex-plugin/plugin.json`: cachebuster only after all validations pass.

### Task 1: Establish failing interaction-state tests

**Files:**
- Modify: `/Users/kylechoi/plugins/wave-content-studio/tests/run-contract-tests.sh`
- Create: `/Users/kylechoi/plugins/wave-content-studio/tests/fixtures/topic-awaiting-review/workspace/content-brief.md`
- Create: `/Users/kylechoi/plugins/wave-content-studio/tests/fixtures/topic-awaiting-review/workspace/pipeline-run-report.md`
- Create: `/Users/kylechoi/plugins/wave-content-studio/tests/fixtures/topic-approved/workspace/content-brief.md`
- Create: `/Users/kylechoi/plugins/wave-content-studio/tests/fixtures/topic-approved/workspace/pipeline-run-report.md`
- Create: `/Users/kylechoi/plugins/wave-content-studio/tests/fixtures/topic-revision-requested/workspace/content-brief.md`
- Create: `/Users/kylechoi/plugins/wave-content-studio/tests/fixtures/topic-revision-requested/workspace/pipeline-run-report.md`
- Create: `/Users/kylechoi/plugins/wave-content-studio/tests/fixtures/editing-complete/workspace/*`
- Create: `/Users/kylechoi/plugins/wave-content-studio/tests/fixtures/publication-complete/workspace/*`

- [ ] **Step 1: Add stage assertions**

Add these exact assertions after the existing stage fixtures:

```bash
expect_stage "topic-awaiting-review" "TOPIC_REVIEW"
expect_stage "topic-approved" "RESEARCH_DIRECTION"
expect_stage "topic-revision-requested" "TOPIC_REVISION"
expect_stage "editing-complete" "AWAITING_PUBLISH_APPROVAL"
expect_stage "publication-complete" "PUBLISHED"
```

- [ ] **Step 2: Add minimal interaction records**

Use this exact machine-readable block in each `pipeline-run-report.md`, varying the values per fixture:

```markdown
## Current Interaction
- stage: TOPIC
- review_state: AWAITING_USER_REVIEW
- direction_summary: 교회 리더를 위한 AI 자동화 입문
- response_summary: 없음
- next_allowed_stage: TOPIC
```

For `topic-approved`, set `review_state: APPROVED` and `next_allowed_stage: RESEARCH`. For `topic-revision-requested`, set `review_state: REVISION_REQUESTED` and `next_allowed_stage: TOPIC`.

- [ ] **Step 3: Run tests and verify RED**

Run:

```bash
bash /Users/kylechoi/plugins/wave-content-studio/tests/run-contract-tests.sh
```

Expected: the five new assertions fail because the current detector returns `RESEARCH`, `OVERWRITE_APPROVAL`, or lacks `PUBLISHED`.

- [ ] **Step 4: Commit the RED tests**

```bash
git -C /Users/kylechoi/Desktop/Ai_works add Codex/docs/superpowers/plans/2026-07-30-wave-content-studio-user-loop.md
git -C /Users/kylechoi/Desktop/Ai_works commit -m "test: define content studio user loop states"
```

The plugin source is outside this Git repository, so preserve its test diff in the implementation report until the validated source is synchronized.

### Task 2: Implement deterministic stage transitions

**Files:**
- Modify: `/Users/kylechoi/plugins/wave-content-studio/scripts/validate-workflow-contract.sh`
- Test: `/Users/kylechoi/plugins/wave-content-studio/tests/run-contract-tests.sh`

- [ ] **Step 1: Add an interaction-field reader**

Add this helper before `detect_stage`:

```bash
interaction_value() {
  local report="$1"
  local key="$2"
  [[ -f "$report" ]] || return 1
  sed -n "s/^[[:space:]]*-[[:space:]]*$key:[[:space:]]*//p" "$report" | tail -n 1
}
```

- [ ] **Step 2: Gate each transition by review state**

At the beginning of `detect_stage`, read:

```bash
local report="$workspace/pipeline-run-report.md"
local interaction_stage
local review_state
local next_allowed_stage
interaction_stage="$(interaction_value "$report" stage || true)"
review_state="$(interaction_value "$report" review_state || true)"
next_allowed_stage="$(interaction_value "$report" next_allowed_stage || true)"
```

Apply these transitions before artifact fallbacks:

```bash
if [[ "$review_state" == "AWAITING_USER_REVIEW" ]]; then
  printf '%s_REVIEW\n' "$interaction_stage"
  return
fi
if [[ "$review_state" == "REVISION_REQUESTED" ]]; then
  printf '%s_REVISION\n' "$interaction_stage"
  return
fi
if [[ "$review_state" == "APPROVED" && -n "$next_allowed_stage" ]]; then
  printf '%s_DIRECTION\n' "$next_allowed_stage"
  return
fi
```

Handle `PUBLISHED` before the publication-request and overwrite checks by requiring a publication report with a standalone `PUBLISHED` result and matching content hash. Handle valid final content as `AWAITING_PUBLISH_APPROVAL` instead of the unreachable `COMPLETE` branch.

- [ ] **Step 3: Run the focused tests**

```bash
bash /Users/kylechoi/plugins/wave-content-studio/tests/run-contract-tests.sh
```

Expected: all stage and publication assertions pass with `CONTRACT_TESTS=PASS`.

- [ ] **Step 4: Add malformed-state tests**

Add fixtures or temporary mutations for an unknown `review_state`, missing `stage`, and `APPROVED` without `next_allowed_stage`. Assert they return `INTERACTION_BLOCKED`, not an inferred later stage.

- [ ] **Step 5: Run tests and verify GREEN**

```bash
bash /Users/kylechoi/plugins/wave-content-studio/tests/run-contract-tests.sh
```

Expected: `CONTRACT_TESTS=PASS` and zero `FAIL:` lines.

### Task 3: Add the shared user-participation contract

**Files:**
- Create: `/Users/kylechoi/plugins/wave-content-studio/shared/policies/user-participation-loop.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/shared/policies/workflow-gates.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/shared/templates/pipeline-run-report.template.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/scripts/validate-workflow-contract.sh`

- [ ] **Step 1: Add static contract tests**

Require these exact strings:

```bash
require_file 'shared/policies/user-participation-loop.md'
require_text 'shared/policies/user-participation-loop.md' 'AWAITING_USER_REVIEW'
require_text 'shared/policies/user-participation-loop.md' 'REVISION_REQUESTED'
require_text 'shared/policies/user-participation-loop.md' 'APPROVED'
require_text 'shared/policies/user-participation-loop.md' '수정 요청이 함께 있으면 승인으로 처리하지 않는다'
require_text 'shared/templates/pipeline-run-report.template.md' '## Current Interaction'
```

- [ ] **Step 2: Run the static validator and verify RED**

```bash
bash /Users/kylechoi/plugins/wave-content-studio/scripts/validate-workflow-contract.sh
```

Expected: `WORKFLOW_CONTRACT=FAIL` because the new policy and template block do not exist.

- [ ] **Step 3: Write the shared policy**

Define the exact loop:

```text
DIRECTION_REQUIRED
→ RUNNING
→ AWAITING_USER_REVIEW
→ APPROVED or REVISION_REQUESTED
```

State that natural-language approval is accepted only when intent is unambiguous and contains no requested change. State that silence, file existence, successful validation, or a quality verdict never implies user approval. Keep `승인 포스팅해줘` as the only publication approval.

- [ ] **Step 4: Extend the report template**

Add:

```markdown
## Current Interaction
- stage:
- review_state:
- direction_summary:
- response_summary:
- next_allowed_stage:
```

- [ ] **Step 5: Run static and full tests**

```bash
bash /Users/kylechoi/plugins/wave-content-studio/scripts/validate-workflow-contract.sh
bash /Users/kylechoi/plugins/wave-content-studio/tests/run-contract-tests.sh
```

Expected: `WORKFLOW_CONTRACT=PASS` and `CONTRACT_TESTS=PASS`.

### Task 4: Convert the orchestrator to a review-gated loop

**Files:**
- Modify: `/Users/kylechoi/plugins/wave-content-studio/skills/content-studio-orchestrator/SKILL.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/skills/content-studio-orchestrator/agents/openai.yaml`
- Test: `/Users/kylechoi/plugins/wave-content-studio/scripts/validate-workflow-contract.sh`

- [ ] **Step 1: Add failing static requirements**

Require the orchestrator to contain:

```text
shared/policies/user-participation-loop.md
DIRECTION_REQUIRED
AWAITING_USER_REVIEW
REVISION_REQUESTED
사용자 확인 전에는 다음 전문 Skill을 실행하지 않는다
```

- [ ] **Step 2: Verify RED**

Run the static validator and confirm it fails on the first missing phrase.

- [ ] **Step 3: Rewrite the stage loop**

For every stage, require:

1. summarize known inputs and constraints;
2. ask one focused direction question only when a material decision is missing;
3. record the answer and set `RUNNING`;
4. execute exactly one specialist skill;
5. save its contracted files;
6. report paths, result summary, and review points;
7. set `AWAITING_USER_REVIEW` and stop the turn;
8. interpret the next user response as approval, revision, or ambiguous;
9. advance only on `APPROVED`.

Remove wording that permits Stage 1 through Stage 5 to chain in one turn. Keep publication as a separate exact-phrase turn.

- [ ] **Step 4: Update UI metadata**

Set `default_prompt` to describe the interactive loop, for example:

```yaml
default_prompt: "Use $content-studio-orchestrator to guide me through one content stage at a time, ask for my direction before each stage, save the result, and wait for my review before continuing."
```

- [ ] **Step 5: Validate the orchestrator**

```bash
python3 /Users/kylechoi/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/kylechoi/plugins/wave-content-studio/skills/content-studio-orchestrator
bash /Users/kylechoi/plugins/wave-content-studio/scripts/validate-workflow-contract.sh
```

Expected: both commands exit 0.

### Task 5: Convert all specialist skills

**Files:**
- Modify: `/Users/kylechoi/plugins/wave-content-studio/skills/content-topic-strategist/SKILL.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/skills/content-researcher/SKILL.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/skills/source-validator/SKILL.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/skills/blog-article-writer/SKILL.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/skills/article-editor/SKILL.md`
- Modify: `/Users/kylechoi/plugins/wave-content-studio/skills/sites-blog-publisher/SKILL.md`

- [ ] **Step 1: Add failing static requirements for every specialist**

For each content-stage skill, require the phrases:

```text
실행 전 방향 확인
결과 저장 후 사용자 확인
AWAITING_USER_REVIEW
사용자 확인 전에는 다음 단계로 이동하지 않는다
```

For the publisher, require that natural-language local approval cannot replace `승인 포스팅해줘`.

- [ ] **Step 2: Verify RED**

Run the static validator and confirm it fails before editing production skill instructions.

- [ ] **Step 3: Add pre-run direction sections**

Add one focused decision contract per skill:

- topic: topic, audience, purpose, then highest-impact optional choice;
- research: research questions, scope, preferred/excluded source types;
- validation: freshness, conservatism, mandatory rechecks;
- writing: structure, voice, length, CTA, preserve/avoid list;
- editing: editing strength and must-preserve elements;
- publishing: exact preview and exact approval phrase only.

Do not re-ask values already fixed in approved upstream artifacts.

- [ ] **Step 4: Add post-run review sections**

Each content-stage skill must save its existing output files first, summarize the result and review points, write `AWAITING_USER_REVIEW` to the interaction report, and stop. On a later turn, route a clear revision request back to the same skill and a clear approval to the orchestrator.

- [ ] **Step 5: Validate all seven skills**

```bash
for skill_dir in /Users/kylechoi/plugins/wave-content-studio/skills/*; do
  python3 /Users/kylechoi/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill_dir"
done
```

Expected: seven `Skill is valid!` messages and exit 0.

### Task 6: Full verification, source synchronization, and reinstall

**Files:**
- Modify: `/Users/kylechoi/plugins/wave-content-studio/.codex-plugin/plugin.json`
- Verify: all plugin files

- [ ] **Step 1: Run the complete verification suite**

```bash
python3 /Users/kylechoi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/kylechoi/plugins/wave-content-studio
bash -n /Users/kylechoi/plugins/wave-content-studio/scripts/validate-workflow-contract.sh
bash -n /Users/kylechoi/plugins/wave-content-studio/tests/run-contract-tests.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile /Users/kylechoi/plugins/wave-content-studio/scripts/validate-publication-request.py
bash /Users/kylechoi/plugins/wave-content-studio/tests/run-contract-tests.sh
```

Expected: plugin validation passes, syntax checks exit 0, and `CONTRACT_TESTS=PASS`.

- [ ] **Step 2: Update the cachebuster**

```bash
python3 /Users/kylechoi/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py /Users/kylechoi/plugins/wave-content-studio
```

Expected: the version keeps base `0.2.0` and receives one new suffix in the form `+codex.20260730183045`.

- [ ] **Step 3: Revalidate after cachebuster**

Run the complete verification suite again and require all commands to exit 0.

- [ ] **Step 4: Read the marketplace name**

```bash
python3 /Users/kylechoi/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py
```

Expected: `personal`.

- [ ] **Step 5: Reinstall the plugin**

```bash
codex plugin add wave-content-studio@personal
```

Expected: installation succeeds and the new cache directory version matches `plugin.json`.

- [ ] **Step 6: Verify source and installed cache**

```bash
PLUGIN_VERSION="$(python3 -c 'import json; print(json.load(open("/Users/kylechoi/plugins/wave-content-studio/.codex-plugin/plugin.json"))["version"])')"
diff -qr \
  /Users/kylechoi/plugins/wave-content-studio \
  "/Users/kylechoi/.codex/plugins/cache/personal/wave-content-studio/$PLUGIN_VERSION"
```

Expected: no differences.

- [ ] **Step 7: Start a new Codex task for forward testing**

Use a new task and request:

```text
Use $content-studio-orchestrator to create an article for church leaders who want to understand practical AI automation.
```

Expected: the plugin asks for direction before TOPIC, executes only TOPIC after direction, saves the brief, reports review points, and stops at `AWAITING_USER_REVIEW`.
