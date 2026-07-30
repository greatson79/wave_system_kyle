# Wave Content Studio Claude Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the public Wave Content Studio repository installable in Claude Code while preserving the existing Codex distribution and excluding Sites publishing from Claude.

**Architecture:** Add a Claude marketplace at the repository root and a separate Claude plugin directory containing only the six content workflow skills. Use a Claude-specific orchestrator and policies that terminate at `COMPLETE_NO_PUBLISH`, then document both installations in the root README.

**Tech Stack:** Claude Code plugin manifests, Markdown skills, JSON marketplaces, Bash contract tests, GitHub.

---

### Task 1: Add failing Claude distribution checks

**Files:**
- Create: `/Users/kylechoi/Desktop/Ai_works/Codex/wave-content-studio-repo/scripts/validate-claude-distribution.sh`

- [ ] **Step 1: Write the validation script**

The script must fail unless all of these conditions are true:

```bash
test -f .claude-plugin/marketplace.json
test -f plugins/wave-content-studio-claude/.claude-plugin/plugin.json
test -f plugins/wave-content-studio-claude/skills/content-studio-orchestrator/SKILL.md
test ! -e plugins/wave-content-studio-claude/skills/sites-blog-publisher
```

It must also fail if this search finds output:

```bash
rg -n 'appgprj_|승인 포스팅해줘|AWAITING_PUBLISH_APPROVAL|OpenAI Sites|sites-blog-publisher' \
  plugins/wave-content-studio-claude
```

- [ ] **Step 2: Run the validator and verify RED**

```bash
bash scripts/validate-claude-distribution.sh
```

Expected: nonzero exit because `.claude-plugin/marketplace.json` is missing.

### Task 2: Create the Claude marketplace and plugin package

**Files:**
- Create: `/Users/kylechoi/Desktop/Ai_works/Codex/wave-content-studio-repo/.claude-plugin/marketplace.json`
- Create: `/Users/kylechoi/Desktop/Ai_works/Codex/wave-content-studio-repo/plugins/wave-content-studio-claude/.claude-plugin/plugin.json`
- Create: Claude copies of the six skill directories, shared policies, templates, docs, and applicable scripts
- Modify: Claude copies of `content-studio-orchestrator/SKILL.md`, `workflow-gates.md`, `workspace-contract.md`, and `pipeline-run-report.template.md`

- [ ] **Step 1: Create the marketplace**

Use this exact structure:

```json
{
  "name": "wave-content-studio-claude",
  "owner": {
    "name": "Wave AI Networks"
  },
  "plugins": [
    {
      "name": "wave-content-studio-claude",
      "source": "./plugins/wave-content-studio-claude",
      "description": "User-reviewed sourced article workflow for Claude Code without external publishing"
    }
  ]
}
```

- [ ] **Step 2: Create the Claude manifest**

```json
{
  "name": "wave-content-studio-claude",
  "version": "0.2.0",
  "description": "Plan, research, validate, write, and edit sourced articles one user-reviewed stage at a time.",
  "author": {
    "name": "Wave AI Networks",
    "email": "waveainetworks@gmail.com"
  }
}
```

- [ ] **Step 3: Copy only the six supported skills**

Include:

```text
content-studio-orchestrator
content-topic-strategist
content-researcher
source-validator
blog-article-writer
article-editor
```

Do not create `skills/sites-blog-publisher`.

- [ ] **Step 4: Adapt the Claude orchestrator**

Remove the publishing skill reference, Stage 6, fixed project ID, publication request generation, and exact publishing phrase. After an approved `PASS` edit, require:

```text
save final article and editorial report
→ provide title, summary, slug, category, tags, and verified sources
→ set final state COMPLETE_NO_PUBLISH
→ stop without external publishing
```

- [ ] **Step 5: Adapt Claude policies**

Remove `publication-request.json` and `publication-report.md` from the workspace contract. Remove Sites gates and publishing statuses from workflow gates. Add `COMPLETE_NO_PUBLISH` to the report template.

- [ ] **Step 6: Run the validator and verify GREEN**

```bash
bash scripts/validate-claude-distribution.sh
```

Expected: `CLAUDE_DISTRIBUTION=PASS`.

### Task 3: Rewrite the public README

**Files:**
- Modify: `/Users/kylechoi/Desktop/Ai_works/Codex/wave-content-studio-repo/README.md`

- [ ] **Step 1: Document platform differences**

State that Codex includes Sites publishing and Claude ends with `COMPLETE_NO_PUBLISH`.

- [ ] **Step 2: Document Codex installation**

```bash
git clone https://github.com/greatson79/wave-content-studio.git
cd wave-content-studio
codex plugin marketplace add .
codex plugin add wave-content-studio@wave-content-studio
```

- [ ] **Step 3: Document Claude Code installation**

```text
/plugin marketplace add greatson79/wave-content-studio
/plugin install wave-content-studio-claude@wave-content-studio-claude
/reload-plugins
```

- [ ] **Step 4: Document invocation**

```text
/wave-content-studio-claude:content-studio-orchestrator
```

- [ ] **Step 5: Add update, uninstall, outputs, security, and validation sections**

Use the real repository and official documentation links. Do not claim Claude supports Sites publishing.

### Task 4: Validate and republish

**Files:**
- Verify all distribution files

- [ ] **Step 1: Run Codex checks**

```bash
python3 /Users/kylechoi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/wave-content-studio
bash plugins/wave-content-studio/tests/run-contract-tests.sh
```

Expected: plugin validation passes and `CONTRACT_TESTS=PASS`.

- [ ] **Step 2: Run Claude checks**

```bash
bash scripts/validate-claude-distribution.sh
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool plugins/wave-content-studio-claude/.claude-plugin/plugin.json
claude plugin validate .
```

Expected: all commands exit zero. If Claude CLI validation uses a different accepted path, run it against the repository root and the Claude plugin directory and record both results.

- [ ] **Step 3: Run secret and diff checks**

```bash
rg -n -i 'ghp_[A-Za-z0-9]+|github_pat_|api[_-]?key|access[_-]?token|password' .
git diff --check
git status --short
```

Expected: no secrets, no whitespace errors, and only intended files changed.

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin plugins/wave-content-studio-claude scripts/validate-claude-distribution.sh README.md
git commit -m "add Claude Code distribution"
```

- [ ] **Step 5: Push**

```bash
git push origin main
```

- [ ] **Step 6: Verify GitHub**

```bash
git ls-remote origin refs/heads/main
gh repo view greatson79/wave-content-studio --json url,visibility,defaultBranchRef
```

Expected: the remote main SHA equals local `HEAD` and visibility is `PUBLIC`.
