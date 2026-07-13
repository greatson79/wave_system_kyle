# Wave Content Studio Sites Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `wave-content-studio` so a sourced article stops for explicit approval, then publishes exactly that approved article to the fixed WAVE AI Networks Sites blog and reports the public URL.

**Architecture:** Keep content production and external publishing separate. The Plugin creates and validates a content-addressed publication request, while a new `sites-blog-publisher` Skill performs the Sites source, test, build, version, and deployment workflow. The blog stores posts in a deterministic JSON collection so the publisher can append one article without rewriting application code or depending on a hard-coded local checkout.

**Tech Stack:** Codex Plugin skills, Bash contract tests, Python 3 standard library, Sites connector, vinext/React blog, Node test runner

---

## Scope and repositories

This feature changes two independently testable surfaces:

1. Plugin source: `Wave-AI-Networks-Agentic-System/wave-ai-networks-agentic-system-course/plugins/wave-content-studio/`
2. Sites blog source: the source repository bound to Project ID `appgprj_6a54f82761348191a9b1da66f9053c7a`

The Plugin never stores a local absolute path to the blog. During publishing it obtains a short-lived Sites source credential, clones or updates the fixed source into a temporary directory, modifies the deterministic article collection, verifies it, pushes the exact commit, saves a Sites version, and deploys it.

## File map

### Plugin

- Modify: `.codex-plugin/plugin.json` — version `0.2.0`, publishing capability and default prompts.
- Modify: `skills/content-studio-orchestrator/SKILL.md` — approval waiting and publish state transitions.
- Create: `skills/sites-blog-publisher/SKILL.md` — publishing-only responsibility and Sites procedure.
- Create: `skills/sites-blog-publisher/agents/openai.yaml` — UI metadata.
- Create: `scripts/validate-publication-request.py` — deterministic approval/hash/category/duplicate validation.
- Modify: `scripts/validate-workflow-contract.sh` — static requirements and publication state detection.
- Modify: `tests/run-contract-tests.sh` — publication fixtures and validator tests.
- Create: `tests/fixtures/publication-ready/workspace/*` — valid approved article fixture.
- Create: `tests/fixtures/publication-mutated/workspace/*` — changed-article rejection fixture.
- Create: `tests/fixtures/publication-duplicate/workspace/*` — duplicate publication fixture.
- Modify: `shared/policies/workflow-gates.md` — exact approval phrase and write boundary.
- Modify: `shared/policies/workspace-contract.md` — publication files.
- Modify: `shared/templates/pipeline-run-report.template.md` — publishing row and state.
- Create: `shared/templates/publication-report.template.md` — durable publish result.
- Modify: `docs/content-workflow.md`, `README.md`, `tests/contract-tests.md` — user and maintainer documentation.

### Blog

- Create: `content/articles.json` — deterministic article records.
- Modify: `lib/content.mjs` — categories and lookup functions over JSON records.
- Modify: `tests/content.test.mjs` — schema, duplicate hash, and slug uniqueness tests.
- Modify: `app/articles/[slug]/page.tsx` only if the normalized block schema requires rendering support.

### Task 1: Add failing Plugin publishing contract tests

**Files:**
- Modify: `tests/run-contract-tests.sh`
- Modify: `tests/contract-tests.md`
- Create: `tests/fixtures/publication-ready/workspace/final-article.md`
- Create: `tests/fixtures/publication-ready/workspace/editorial-report.md`
- Create: `tests/fixtures/publication-ready/workspace/pipeline-run-report.md`
- Create: `tests/fixtures/publication-ready/workspace/publication-request.json`

- [ ] **Step 1: Add the expected publishing Skill to static validation**

Extend the `expected_skills` array in `scripts/validate-workflow-contract.sh` with:

```bash
sites-blog-publisher
```

Require the new artifacts and approval text:

```bash
require_file 'shared/templates/publication-report.template.md'
require_file 'scripts/validate-publication-request.py'
require_text 'skills/content-studio-orchestrator/SKILL.md' 'AWAITING_PUBLISH_APPROVAL'
require_text 'skills/sites-blog-publisher/SKILL.md' '승인 포스팅해줘'
```

- [ ] **Step 2: Add a publication-ready stage expectation**

Add to `tests/run-contract-tests.sh`:

```bash
expect_stage "publication-ready" "AWAITING_PUBLISH_APPROVAL"
```

The fixture request must use this shape with a real SHA-256 value calculated from its fixture `final-article.md`:

```json
{
  "schema_version": 1,
  "status": "AWAITING_PUBLISH_APPROVAL",
  "site": {
    "name": "WAVE AI Networks",
    "project_id": "appgprj_6a54f82761348191a9b1da66f9053c7a"
  },
  "article": {
    "title": "Fixture article",
    "slug": "fixture-article",
    "category": "youth-identity",
    "audience": "중학생",
    "summary": "계약 검증용 글",
    "source_count": 1,
    "editorial_verdict": "PASS",
    "content_sha256": "860977cc6820f26abc94515c81d662c7660da287e8e01a1fab2398cc59f1213f"
  },
  "approval": {
    "required_phrase": "승인 포스팅해줘",
    "approved": false
  }
}
```

- [ ] **Step 3: Run the tests and verify RED**

Run from the Plugin root:

```bash
bash tests/run-contract-tests.sh
```

Expected: FAIL because `sites-blog-publisher`, the publication validator, and template do not exist.

- [ ] **Step 4: Commit the red contract**

```bash
git add Wave-AI-Networks-Agentic-System/wave-ai-networks-agentic-system-course/plugins/wave-content-studio/tests Wave-AI-Networks-Agentic-System/wave-ai-networks-agentic-system-course/plugins/wave-content-studio/scripts/validate-workflow-contract.sh
git commit -m "test: define Sites publishing contract"
```

### Task 2: Implement deterministic publication request validation

**Files:**
- Create: `scripts/validate-publication-request.py`
- Create: `tests/fixtures/publication-mutated/workspace/*`
- Create: `tests/fixtures/publication-duplicate/workspace/*`
- Modify: `tests/run-contract-tests.sh`

- [ ] **Step 1: Add failing command-level tests**

Add a helper to `tests/run-contract-tests.sh`:

```bash
expect_publication() {
  local fixture="$1"
  local phrase="$2"
  local expected="$3"
  local output
  output="$(python3 "$PLUGIN_ROOT/scripts/validate-publication-request.py" \
    --project "$TEST_DIR/fixtures/$fixture" \
    --approval-phrase "$phrase" 2>&1)" || true
  if printf '%s\n' "$output" | grep -Fq "PUBLICATION_CONTRACT=$expected"; then
    pass "$fixture publication contract is $expected"
  else
    fail "$fixture expected $expected but got: $output"
  fi
}
```

Add expectations:

```bash
expect_publication "publication-ready" "승인 포스팅해줘" "READY"
expect_publication "publication-ready" "게시해줘" "BLOCKED_APPROVAL_PHRASE"
expect_publication "publication-mutated" "승인 포스팅해줘" "BLOCKED_CONTENT_CHANGED"
expect_publication "publication-duplicate" "승인 포스팅해줘" "ALREADY_PUBLISHED"
```

- [ ] **Step 2: Run tests and verify validator missing failure**

Run: `bash tests/run-contract-tests.sh`

Expected: the four publication expectations fail because the Python validator is missing.

- [ ] **Step 3: Implement the validator with standard-library-only code**

The script must:

1. Load `workspace/publication-request.json`.
2. Require schema version 1 and the fixed Project ID.
3. Require category in the four-item allowlist.
4. Require editorial verdict `PASS` and pipeline report containing `COMPLETE`.
5. Compute SHA-256 from raw bytes of `workspace/final-article.md`.
6. Compare it with `article.content_sha256` using `hmac.compare_digest`.
7. Require the exact approval phrase.
8. Read optional `workspace/publication-report.md`; if it contains the same content hash and `PUBLISHED`, return `ALREADY_PUBLISHED`.
9. Print exactly one terminal marker and exit nonzero for blocked states.

The markers are:

```text
PUBLICATION_CONTRACT=READY
PUBLICATION_CONTRACT=BLOCKED_APPROVAL_PHRASE
PUBLICATION_CONTRACT=BLOCKED_CONTENT_CHANGED
PUBLICATION_CONTRACT=BLOCKED_EDITORIAL_VERDICT
PUBLICATION_CONTRACT=BLOCKED_SITE
PUBLICATION_CONTRACT=BLOCKED_CATEGORY
PUBLICATION_CONTRACT=ALREADY_PUBLISHED
```

- [ ] **Step 4: Run tests and verify GREEN**

Run: `bash tests/run-contract-tests.sh`

Expected: `CONTRACT_TESTS=PASS`, including all four publication cases.

- [ ] **Step 5: Commit validator and fixtures**

```bash
git add Wave-AI-Networks-Agentic-System/wave-ai-networks-agentic-system-course/plugins/wave-content-studio/scripts Wave-AI-Networks-Agentic-System/wave-ai-networks-agentic-system-course/plugins/wave-content-studio/tests
git commit -m "feat: validate publication approvals"
```

### Task 3: Add the publisher Skill and approval states

**Files:**
- Create: `skills/sites-blog-publisher/SKILL.md`
- Create: `skills/sites-blog-publisher/agents/openai.yaml`
- Modify: `skills/content-studio-orchestrator/SKILL.md`
- Modify: `shared/policies/workflow-gates.md`
- Modify: `shared/policies/workspace-contract.md`
- Create: `shared/templates/publication-report.template.md`
- Modify: `shared/templates/pipeline-run-report.template.md`

- [ ] **Step 1: Create the publisher Skill with a narrow trigger**

Frontmatter:

```yaml
---
name: sites-blog-publisher
description: Use only after Wave Content Studio has a PASS editorial report and an AWAITING_PUBLISH_APPROVAL request for the fixed WAVE AI Networks Sites blog, and the user says the exact phrase 승인 포스팅해줘. Validates the approved content hash, prevents duplicates and slug collisions, then verifies and publishes through Sites. Do not use for writing, editing, research, other sites, or unapproved drafts.
---
```

The body must require this order:

```text
validate request
→ obtain short-lived Sites source credential
→ clone fixed source into temporary directory
→ compare content hash and slug index
→ append normalized article JSON
→ run content tests, route tests, build, lint
→ commit and push exact source
→ package exact commit
→ save Sites version
→ public deploy
→ poll succeeded/failed
→ write publication report
```

It must prohibit storing credentials, pushing unverified source, changing another article, or deploying another Project ID.

- [ ] **Step 2: Add the Orchestrator approval transition**

After `EDITING` PASS, the Orchestrator creates `publication-request.json`, computes the current article hash, records `AWAITING_PUBLISH_APPROVAL`, reports the preview fields, and stops. It invokes `sites-blog-publisher` only when the user input equals `승인 포스팅해줘` and the deterministic validator returns `READY`.

- [ ] **Step 3: Update shared contracts and report templates**

Add `publication-request.json` and `publication-report.md` to the workspace contract. Add `Gate 3 — Sites 게시 승인` with the exact phrase, content hash scope, and public write consequence. Add a `게시` row to the pipeline report and create the publication report sections specified in the design.

- [ ] **Step 4: Run Plugin contract tests**

Run:

```bash
bash tests/run-contract-tests.sh
bash scripts/validate-workflow-contract.sh
```

Expected: both PASS markers.

- [ ] **Step 5: Commit Skill and policy changes**

```bash
git add Wave-AI-Networks-Agentic-System/wave-ai-networks-agentic-system-course/plugins/wave-content-studio/skills Wave-AI-Networks-Agentic-System/wave-ai-networks-agentic-system-course/plugins/wave-content-studio/shared
git commit -m "feat: add approval-gated Sites publisher"
```

### Task 4: Move blog posts to a deterministic JSON collection

**Files:**
- Create: `content/articles.json`
- Modify: `lib/content.mjs`
- Modify: `tests/content.test.mjs`

- [ ] **Step 1: Write failing collection tests**

Add tests that load `content/articles.json` and assert:

```js
test("stores articles in the publishing collection", async () => {
  const data = JSON.parse(await readFile(new URL("../content/articles.json", import.meta.url), "utf8"));
  assert.ok(data.articles.length >= 4);
  assert.equal(new Set(data.articles.map((article) => article.slug)).size, data.articles.length);
  assert.equal(new Set(data.articles.map((article) => article.contentSha256)).size, data.articles.length);
});
```

Every record must include:

```json
{
  "slug": "identity-and-respect",
  "category": "youth-identity",
  "status": "published",
  "title": "나는 누구인가, 그리고 우리는 어떻게 서로를 존중할까",
  "summary": "...",
  "audience": "청소년",
  "readingMinutes": 8,
  "publishedAt": "2026-07-13",
  "contentSha256": "64-character-lowercase-hex",
  "introduction": [],
  "sections": [],
  "sources": []
}
```

- [ ] **Step 2: Run content tests and verify missing collection failure**

Run: `npm run test:content`

Expected: FAIL because `content/articles.json` does not exist.

- [ ] **Step 3: Move existing records without changing rendered content**

Create the JSON collection from the current article objects. Change `lib/content.mjs` to read the JSON records and export the same `articles`, `getArticle`, and `getCategoryArticles` API. Preserve the four category objects in code.

- [ ] **Step 4: Run full blog verification**

Run:

```bash
npm run test:content
npm test
npm run lint
```

Expected: content and route tests pass, production build succeeds, lint exits 0.

- [ ] **Step 5: Commit the data boundary**

```bash
git add content/articles.json lib/content.mjs tests/content.test.mjs
git commit -m "refactor: store blog posts as publication data"
```

### Task 5: Document and version Plugin 0.2.0

**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `README.md`
- Modify: `docs/content-workflow.md`
- Modify: `tests/contract-tests.md`

- [ ] **Step 1: Update manifest metadata**

Set version to `0.2.0`, change the description and long description to include approval-gated Sites publishing, add `Network` to capabilities if accepted by the existing validator schema, and add these default prompts:

```json
"$content-studio-orchestrator를 사용해 주제와 대상 독자를 바탕으로 글을 완성하고 게시 승인 단계까지 진행해줘.",
"승인 포스팅해줘"
```

Do not add unsupported manifest fields.

- [ ] **Step 2: Update user documentation**

Document the two-turn flow:

```text
1. AI 시대 청소년의 정체성을 주제로 중학생이 자신과 타인을 존중하도록 돕는 글을 작성해줘.
2. 승인 포스팅해줘
```

State that exact approval is scoped to the reported content hash and the fixed WAVE AI Networks site.

- [ ] **Step 3: Validate Plugin and Skills**

Run from the Plugin root:

```bash
bash tests/run-contract-tests.sh
bash scripts/validate-workflow-contract.sh
python3 /Users/kylechoi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

For every Skill directory, run the available `skill-creator` quick validator. Expected: all validators exit 0.

- [ ] **Step 4: Commit documentation and manifest**

```bash
git add .codex-plugin/plugin.json README.md docs tests/contract-tests.md
git commit -m "docs: release Wave Content Studio 0.2.0"
```

### Task 6: Run an end-to-end dry run without public deployment

**Files:**
- Create in a temporary fixture project only: `workspace/publication-request.json`, `workspace/publication-report.md`

- [ ] **Step 1: Run the existing pipeline fixture to approval waiting**

Use a copied fixture outside the Plugin source. Confirm stage detection returns:

```text
NEXT_STAGE=AWAITING_PUBLISH_APPROVAL
```

- [ ] **Step 2: Verify wrong approval is blocked**

Run the validator with `게시해줘`.

Expected: `PUBLICATION_CONTRACT=BLOCKED_APPROVAL_PHRASE` and nonzero exit.

- [ ] **Step 3: Verify changed content is blocked**

Append one byte to the copied final article and run with the exact approval phrase.

Expected: `PUBLICATION_CONTRACT=BLOCKED_CONTENT_CHANGED` and nonzero exit.

- [ ] **Step 4: Restore the article and verify readiness**

Restore exact fixture bytes and run with `승인 포스팅해줘`.

Expected: `PUBLICATION_CONTRACT=READY` and exit 0.

- [ ] **Step 5: Do not deploy the fixture**

The dry run ends before any Sites connector call. Record the results in the implementation handoff.

### Task 7: Install/update the Plugin development build

**Files:**
- Update through helper: local Plugin cachebuster and installed development copy

- [ ] **Step 1: Validate the source one final time**

Run all Plugin contract and validator commands from Task 5.

- [ ] **Step 2: Use the official cachebuster update flow**

Run:

```bash
python3 /Users/kylechoi/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py /Users/kylechoi/Desktop/Ai_works/Codex/Wave-AI-Networks-Agentic-System/wave-ai-networks-agentic-system-course/plugins/wave-content-studio
```

Follow `plugin-creator/references/installing-and-updating.md` for reinstall. Do not hand-edit marketplace configuration.

- [ ] **Step 3: Verify discovery in a new Codex task**

Confirm `content-studio-orchestrator` and `sites-blog-publisher` are both discoverable after reinstall. Existing tasks are not sufficient because Plugin discovery occurs at task start.

## Final verification checklist

- Plugin contract tests pass.
- Publication validator passes ready, wrong-phrase, changed-content, duplicate, invalid-site and invalid-category cases.
- Every Plugin and Skill validator passes.
- Blog content, route, build and lint checks pass after JSON migration.
- Plugin contains no absolute user path, credentials, or runtime workspace.
- Fixed Sites Project ID is the only allowed destination.
- Public deployment requires the exact phrase and a matching content hash.
- Dry run performs no external write.
