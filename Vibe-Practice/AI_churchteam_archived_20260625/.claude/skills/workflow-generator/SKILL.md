---
name: workflow-generator
description: Claude Code용 워크플로우(workflow.md) 자동 생성 스킬. 사용자가 "워크플로우 만들어줘", "workflow 생성", "자동화 파이프라인 설계", "작업 흐름 정의" 등을 요청할 때 사용. 대화를 통해 사용자의 의도를 파악하고, Research → Planning → Implementation 3단계 구조의 workflow.md를 생성. Claude Code의 sub-agents, agent teams(swarm), hooks, skills, slash commands, MCP servers를 활용한 구현 설계 포함.
---

# Workflow Generator

Skill that designs and generates workflow definition files (`workflow.md`) for Claude Code.

> **Language convention (Absolute Standard ③).** Internal logic and agent-facing
> instructions in this file are in **English** for token efficiency, accuracy, and
> interpretive consistency. Only the Korean blocks under "User-Facing Dialogue
> Templates" are addressed to the human user.

---

## Case Detection

Determine the user's situation first.

| Condition | Case | Procedure |
|-----------|------|-----------|
| PDF / spec document attached | Case 2 | Analyze the document first → confirmation dialogue |
| Idea only | Case 1 | Conversational question loop to gather requirements |

---

## Case 1 — Idea-Only

User has only a vague idea.

### Step 1: Identify Purpose
Use the Korean question set (see "User-Facing Dialogue Templates §A").

### Step 2: Define Phases
Use the Korean question set ("User-Facing Dialogue Templates §B").

### Step 3: Identify Human-in-the-Loop Points
Use the Korean question set ("User-Facing Dialogue Templates §C").

### Step 4: Implementation Design → Generation
After requirements are collected, generate `workflow.md`.

---

## Case 2 — Specification Document Provided

### Step 1: Deep Document Analysis
Read the document carefully and extract:

```
1. Core purpose: the ultimate goal the workflow must achieve
2. Major steps: processes/phases mentioned in the document
3. I/O definitions: input/output of each step
4. Technical requirements: tools, APIs, data sources required
5. Constraints: quality bars, time limits, dependencies
6. Human-in-the-loop: points where human intervention is required
```

### Step 2: Share Analysis Result
Present the extracted understanding to the user using the template in
"User-Facing Dialogue Templates §D".

### Step 3: Confirmation Dialogue
Use the Korean confirmation prompts in "User-Facing Dialogue Templates §E".

### Step 4: Generation
After confirmation, generate `workflow.md`.

---

## Absolute Standards

### Absolute Standard 1 — Quality of Final Output

> **Speed and token cost are completely ignored.**
> The single decision criterion is the **quality** and **highest qualitative level**
> of the final output. Prefer adding steps for quality over removing them for speed.
> If a quality-improving step increases SOT state complexity, accept the cost
> (Standard 1 > Standard 2).

### Absolute Standard 2 — Single-File SOT + Hierarchical Memory

> **Under a single-file SOT plus a hierarchical memory structure, dozens of agents
> can run concurrently without data inconsistency.**

Design implications:
- **State management**: all shared state lives in a **single file** (e.g. `state.json`).
  Do not scatter shared state across files.
- **Memory hierarchy**: separate per-agent local memory (working context) from
  global memory (shared state).
- **Write authority**: only the Orchestrator (or a single designated agent) may
  write to the SOT. Other agents read-only or hand results back to the Orchestrator.
- **Conflict prevention**: never design parallel agents (Agent Team / Swarm) that
  modify the same SOT field simultaneously.

```
Bad:  Agent A → writes state.json directly
      Agent B → writes state.json directly  → conflict / inconsistency
Good: Agent A → reports result to Orchestrator
      Agent B → reports result to Orchestrator
      Orchestrator → merges into state.json  → single write point, no conflict
```

### Absolute Standard 3 — Code Change Protocol (CCP)

> **When writing or modifying code in workflow Implementation (Phase 2), always
> perform Intent → Impact Scope → Change Design.**

Workflow components (sub-agents, hooks, SOT, slash commands, MCP) are
interdependent. A change in one can ripple. Therefore analyze impact before
changing code.

- **Step 1 — Intent**: precisely identify the change purpose and constraints.
- **Step 2 — Impact Scope**: review directly dependent modules, call relations,
  SOT files, configuration/environment, test code, and documentation.
- **Step 3 — Change Design**: design the change order and a modification plan
  for every affected file before executing.

> Proportionality: documentation edits in Phase 1 (workflow design) qualify as
> minor changes (Step 1 only). Code changes in Phase 2 are standard / large
> changes (full 3-step process).

### Priority Among Absolute Standards

> **Standard 1 (Quality) is supreme. Standards 2 (SOT) and 3 (CCP) are co-equal
> means of safeguarding quality.**
> A design that degrades final quality to preserve SOT structure is not allowed.
> A design that degrades final quality to satisfy CCP is not allowed.

All Absolute Standards outrank the design principles below. On principle
conflicts the Absolute Standards win; on conflicts among Absolute Standards the
order is **Standard 1 > (Standard 2, Standard 3)**.

---

## Genome Inheritance Protocol

> **When producing a child, inherit the parent's full genome structurally.
> Children produced without inheritance are not allowed.**

AgenticWorkflow is a parent organism that generates child workflows.
`workflow-generator` is the production line; every child born from this line
embeds the parent's full genome as an `Inherited DNA` section.

### Inheritance Mechanism

| Parent Genome (DNA) | Form embedded in the child |
|---------------------|---------------------------|
| Three Absolute Standards | `Inherited DNA` section — domain-contextualized |
| SOT pattern | `state.yaml` in Configuration + single write point |
| Three-phase structure | Research → Planning → Implementation |
| Four-layer verification | `Verification` + `pACS` fields |
| P1 containment | Hook-based deterministic verification |
| Safety Hook | PreToolUse blocking patterns |
| Adversarial Review | `Review:` field — `@reviewer` / `@fact-checker` |
| Decision Log | `autopilot-logs/` pattern |
| Context Preservation | Cross-session memory preservation pattern |

### Expression vs Inheritance

Like cells with the same genome that perform different functions, child systems
**express domain-appropriately** on top of the same DNA. A research-automation
system expresses Research-phase genes strongly; a software-development
automation expresses CCP genes strongly. The purpose differs, the genome does
not.

### Mandatory at Generation Time

1. Every `workflow.md` includes an `Inherited DNA (Parent Genome)` section
   (see template).
2. Every `state.yaml` includes a `parent_genome` metadata block (see SOT
   template).
3. The child's agent definitions reflect the parent's quality bar
   (Absolute Standard 1).

References: `soul.md §0`, `AGENTS.md §1 Reason for Existence`.

---

## Design Principles (Required)

Required when designing workflows. All principles are subordinate to the
**Absolute Standards** (1. Quality first, 2. Single-file SOT, 3. CCP).

### P1. Data Refinement for Accuracy

Passing large raw data to an AI introduces noise and **degrades accuracy**.
Refine data so the agent can focus on the essence.

- Each step specifies **pre-processing**: strip noise via Python script (etc.)
  before handing data to the AI → improved analytical accuracy.
- Each step specifies **post-processing**: refine the artifact before passing it
  to the next step → improved next-step quality.
- Pre-compute relationships at the **code level** when possible → the AI can
  focus on judgment and analysis.

```
Bad:  "Pass the entire collected HTML to the agent" → noise degrades quality
Good: "Use a Python script to extract main text → pass only core text" → higher accuracy
```

### P2. Expertise-Based Delegation

Delegate each task to the **specialist agent best suited** for it. The
Orchestrator coordinates overall quality; specialists go deep within their
domain.

```
Orchestrator (quality coordination + flow management)
  ├→ Sub-agent A: specialized research (domain-optimized)
  ├→ Sub-agent B: deep analysis (analysis-only focus)
  └→ Skill C: validated pattern application (quality-guaranteed reusable logic)
```

### P3. Image / Resource Accuracy

Steps that need image resources must specify **exact download paths**.
Placeholders must all be extracted; nothing may be omitted.

### P4. Question Design Rule

When asking the user:
- At most 4 questions.
- Each question offers around 3 choices (sub-agent / skill / recommended option).
- If nothing is ambiguous, proceed without questions.

---

## Standard Workflow Structure

Every workflow has three phases:

1. **Research** — gather and analyze information.
2. **Planning** — formulate and structure the plan.
3. **Implementation** — execute and produce artifacts.

**Each step must include:**
- Task
- Owner agent (`@agent`)
- Pre-processing — noise reduction for accuracy (P1)
- Output
- Adversarial Review — `@reviewer`, `@fact-checker`, or `none` (AGENTS.md §5.5)
- Translation — `@translator` or `none` (text artifacts only)
- Post-processing — refinement to safeguard the next step's quality (P1)

## Claude Code Component Mapping

| Workflow Element | Claude Code Implementation | Selection Criterion |
|------------------|---------------------------|---------------------|
| Single delegated task | Sub-agent (`.claude/agents/*.md`) | Deep focus in a specialty, quality maximization |
| Large-scale parallel collaboration | Agent Team / Swarm (`TeamCreate`) | Independent work executed concurrently across sessions |
| Human-in-the-loop step | Slash command (`.claude/commands/`) | Review / approval / selection — user interaction |
| Automated verification / trigger | Hooks (`settings.json`) | Formatting, quality gates, security checks |
| Reusable logic | Skill (`.claude/skills/`) | Domain knowledge, repeated patterns |
| External integration | MCP Server | API, DB, external service integration |

### Sub-agent vs Agent Team — Selection Criterion

> **The single criterion is: "Which structure raises final-output quality the most?"**
> Do not pick Agent Team because parallelism is faster.
> Do not pick Sub-agent because it uses fewer tokens.

| Situation | Choice | Quality Rationale |
|-----------|--------|-------------------|
| One specialist must hold deep context end-to-end for top quality | **Sub-agent** | Consistent depth within a single context |
| Different specialties must each be handled at top quality | **Agent Team** | Each specialist focuses 100% in an independent context |
| Multi-perspective analysis / cross-verification raises quality | **Agent Team** | Independent perspectives combine into a richer result |
| Accuracy of cross-step context handoff is the quality lever | **Sequential sub-agent invocation** | Step-by-step artifacts hand off precisely |

> **Standard-2 mandatory companion**: when choosing Agent Team, define the SOT
> design alongside it — SOT file location, single-write authority for the Team
> Lead, teammate artifact-file rules. Agent Team without SOT design is
> disallowed in principle. See `references/claude-code-patterns.md` § State
> Management.
>
> **Standard-1 priority exception**: for fully independent parallel work (no
> shared state between agents, no cross-references between artifacts) where
> SOT design is explicitly shown not to contribute to quality, the SOT may be
> lightened. Document this judgment in the workflow design.

## Reference Documents

- `workflow.md` template: `references/workflow-template.md`
- Claude Code implementation patterns (Sub-agents, Teams, Hooks):
  `references/claude-code-patterns.md`
  - Anti-Skip Guard Protocol: §Anti-Skip Execution Protocol (artifact verification — 100-byte minimum)
  - Autopilot Execution Checklist: §Autopilot + Agent Team integrated checklist
  - SOT state management: §SOT State Management Protocol
- Document-analysis guide (Case 2): `references/document-analysis-guide.md`
- Context-injection patterns (sub-agent / team input handoff):
  `references/context-injection-patterns.md`
- SOT template (`state.yaml` bootstrap): `references/state.yaml.example`
- Autopilot Decision Log template: `references/autopilot-decision-template.md`

## Final Generation Procedure

1. Detect case (document present?).
2. Case 1: collect requirements via dialogue. Case 2: analyze document → confirm.
3. **Genome Inheritance**: include `Inherited DNA (Parent Genome)` in
   `workflow.md` (see template). `parent_genome.version` uses the workflow
   creation date (YYYY-MM-DD). Include CAP-1..4 (coding anchors) when
   contextualizing CCP.
4. Define work in the three-phase structure while applying P1–P4.
   - Evaluate the need for a Domain Knowledge Structure (DKS): workflows that
     require domain-specific reasoning (medicine, law, competitive analysis,
     etc.) include a DKS-construction step in the Research phase. Workflows
     using DKS include
     `python3 .claude/hooks/scripts/validate_domain_knowledge.py --project-dir . --check-output --step N`
     in the relevant step's Post-processing. See `AGENTS.md §5.3 DKS`.
5. Specify pre-/post-processing per step (P1).
6. Mark human-in-the-loop points.
7. **Define a `Verification` field for every step** (AGENTS.md §5.3 — required):
   - Place `Verification` **before** `Task` (so the agent sees it first).
   - **Required for every agent-execution step** — no Research/Planning/
     Implementation distinction. Research steps too need completeness checks
     (e.g. "all 5 competitors analyzed").
   - `(human)` steps are exempt — the human is the verifier.
   - Each criterion is a **concrete sentence a third party can judge true/false**.
   - Combine the five criterion types:
     - **Structural completeness**: artifact internal structure → "all 5
       sections present", "each item has ≥3 sub-items".
     - **Functional goal**: task goal achieved → "pricing data for ≥3
       competitors", "every API endpoint implemented".
     - **Data integrity**: data correctness → "all URLs valid, no placeholders",
       "numeric data sources cited".
     - **Pipeline linkage**: next-step input compatibility → "contains the
       fields required by Step N+1", "output format matches Step N+1's input".
     - **Cross-step traceability**: derivable from prior steps → "≥80% of
       analytical claims have a `[trace:step-N]` source marker".
   - **Tip**: use a `(source: Step N)` annotation when authoring criteria.
     Verification criteria then explicitly reference upstream steps, enabling
     automatic upstream-impact analysis during diagnosis. Example: "competitor
     analysis data reflects Step 2 research (source: Step 2)".
8. Set the **Review field** per step (AGENTS.md §5.5 — optional):
   - Research/analysis artifacts (need fact verification) → `@fact-checker`
   - Code/technical artifacts (need logic/completeness verification) → `@reviewer`
   - High-risk steps (both) → `@reviewer + @fact-checker`
   - Low-risk or intermediate → `none` (L1.5 only)
   - **Order**: Review PASS → Translation. Translation forbidden while Review FAIL.
9. Set the **Translation field** — text artifacts (`.md`, `.txt`) → `@translator`;
   code/data/config → `none`.
10. Add the Claude Code implementation design (Sub-agents, Teams, Hooks,
    Commands, Skills, MCP).
    - **Choose a Context Injection pattern** per agent step:
      - Input < 50KB → Pattern A (Full Delegation — pass file paths)
      - Input 50–200KB + partially relevant → Pattern B (Filtered — refine via
        a pre-processing script first)
      - Input > 200KB or splitting needed → Pattern C (Recursive Decomposition
        — chunked parallel processing)
      - Standard-1 priority: regardless of size, choose Pattern B if filtering
        raises quality.
      - See `references/context-injection-patterns.md`.
    - **Agent Team requires SOT design** (Standard 2):
      - SOT file location (`.claude/state.yaml`), single-write authority for
        the Team Lead, teammate artifact rules.
      - `active_team` schema: `name`, `status`, `tasks_completed/pending`,
        `completed_summaries`.
      - SOT update at 4 points: right after `TeamCreate` → on each teammate
        completion → on full completion → right after `TeamDelete`.
      - See `references/workflow-template.md §Agent Team SOT schema`.
    - **Checkpoint Pattern**: estimate each Task's expected turn count and
      pick `standard` (≤10 turns) or `dense` (>10 turns). See
      `references/claude-code-patterns.md §DCP`.
11. **Apply the English-First execution principle** (AGENTS.md §5.2):
    - All agent Task descriptions and prompts are written in **English** to
      maximize AI performance (Standard 1).
    - User dialogue (workflow design) is Korean; agent execution is English.
    - The `@translator` sub-agent handles English→Korean translation
      (declared via the Translation field).
12. Generate the `workflow.md` file.
13. **(Optional) Distill verification** — quality-maximization checks for the
    generated workflow:
    - "Does this step contribute to final quality?" — drop quality-irrelevant
      steps only.
    - "If automated, would this step be more reliable?" — surface automation
      opportunities.
    - "Is there a step we should add to raise quality?" — add verification /
      reinforcement steps.
    - "Does each `Verification` criterion include **pipeline linkage**?" —
      validate inter-step data flow.
    - **DNA Inheritance P1 check**:
      `python3 .claude/hooks/scripts/validate_workflow.py --workflow-path ./workflow.md`
      → confirm W1–W8 pass.
    - Reference: `prompt/distill-partner.md`.

## Autopilot Mode Support

Include an Autopilot Mode field in every generated `workflow.md`.

- Add `- **Autopilot**: [disabled|enabled]` to the Overview section
  (default: `disabled`).
- If the user requests "auto-run", "uninterrupted execution", etc., set
  `enabled`.
- The design of `(human)` steps does not change — Autopilot is an execution
  mode, not a design change.
- Optional: per `(human)` step, add an `Autopilot Default` field stating the
  default behavior under auto-approval.

## pACS Support

Include a pACS (self-confidence assessment) field in every generated
`workflow.md`.

- Add `- **pACS**: [enabled|disabled]` to the Overview section (default:
  `enabled`, AGENTS.md §5.4).
- pACS operates independently of Autopilot — applies in manual runs too.
- `(human)` steps do not need pACS (the human is the evaluator — same rule as
  Verification).
- If the user explicitly requests "without pACS", set `disabled`.

---

## User-Facing Dialogue Templates (Korean — for end-user only)

> The blocks below are spoken to the human user. Korean by Absolute Standard ③.

### §A. Case 1 — Step 1 질문
1. "어떤 결과물(output)을 만들고 싶으신가요?"
2. "이 워크플로우가 해결해야 할 문제는 무엇인가요?"
3. "주요 입력(input) 소스는 무엇인가요?"

### §B. Case 1 — Step 2 질문
1. "Research 단계에서 어떤 정보를 수집해야 하나요?"
2. "Planning 단계에서 어떤 검토/승인이 필요한가요?"
3. "최종 산출물의 형태와 품질 기준은 무엇인가요?"

### §C. Case 1 — Step 3 질문
1. "어느 단계에서 사람의 검토/승인이 필요한가요?"
2. "자동화해도 되는 단계와 반드시 확인이 필요한 단계를 구분해주세요."

### §D. Case 2 — 분석 결과 공유 템플릿
```markdown
## 문서 분석 결과

**워크플로우 목적**: [추출한 목적]

**파악된 주요 단계**:
1. [단계1]: [설명]
2. [단계2]: [설명]
...

**식별된 휴먼-인-더-루프 지점**:
- [지점1]: [이유]

**기술적 구현 방향**:
- Sub-agents: [에이전트 목록 — 단일 세션 내 위임]
- Agent Team: [팀 구성 — 독립 세션 간 병렬 협업이 필요한 경우]
- Hooks: [자동화 트리거 — 품질 게이트, 포맷팅, 검증]
- 필요 도구: [도구/MCP 목록]

**확인이 필요한 사항**:
1. [질문1]
2. [질문2]
```

### §E. Case 2 — 확인 질문
- "제가 파악한 내용이 맞나요?"
- "추가하거나 수정할 부분이 있으신가요?"
- "[불명확한 부분]에 대해 좀 더 설명해주시겠어요?"
