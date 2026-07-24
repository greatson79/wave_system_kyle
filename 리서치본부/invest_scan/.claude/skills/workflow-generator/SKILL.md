---
name: workflow-generator
description: Generate workflow.md files for Claude Code. Use when the user requests "create a workflow", "generate a workflow", "design an automation pipeline", "define a task flow", etc. Conducts design conversations to understand user intent and generates Research → Planning → Implementation 3-phase workflow.md files. Includes implementation designs using Claude Code sub-agents, agent teams (swarm), hooks, skills, slash commands, and MCP servers.
---

# Workflow Generator

A skill for designing and generating workflow definition files (workflow.md) for Claude Code.

## Use Case Identification

**First, assess the user's situation:**

| Condition | Case | Approach |
|------|--------|----------|
| PDF/document attached | Case 2 | Document analysis first → confirmation dialogue |
| Idea only mentioned | Case 1 | Collect requirements via conversational questions |

---

## Case 1: Idea Only

When the user has only a vague idea.

### Step 1: Capture Intent

Elicit workflow purpose with these questions:

1. "What output do you want to produce?"
2. "What problem should this workflow solve?"
3. "What are the main input sources?"

### Step 2: Define Steps

Elicit specific steps for each phase:

1. "What information needs to be collected in the Research phase?"
2. "What reviews/approvals are needed in the Planning phase?"
3. "What is the form and quality standard of the final output?"

### Step 3: Identify Human-in-the-Loop

1. "At which steps does human review/approval need to happen?"
2. "Which steps can be automated versus which must be manually verified?"

### Step 4: Design Implementation → Generate

After requirements collection is complete, generate workflow.md.

---

## Case 2: Specification Document Provided

When the user has attached a concrete specification document such as a PDF.

### Step 1: Deep Document Analysis

**Read the document carefully first and extract:**

```
1. Core purpose: The ultimate goal this workflow aims to achieve
2. Key steps: Processes/stages mentioned in the document
3. Input/Output definition: Input/output for each step
4. Technical requirements: Required tools, APIs, data sources
5. Constraints: Quality standards, time limits, dependencies
6. Human-in-the-loop: Points requiring human intervention
```

### Step 2: Share Analysis Results

After document analysis, present a summary of your understanding to the user:

```markdown
## Document Analysis Results

**Workflow Purpose**: [extracted purpose]

**Identified Key Steps**:
1. [Step1]: [description]
2. [Step2]: [description]
...

**Identified Human-in-the-Loop Points**:
- [Point1]: [reason]

**Technical Implementation Direction**:
- Sub-agents: [agent list — delegation within a single session]
- Agent Team: [team composition — when independent parallel collaboration across sessions is needed]
- Hooks: [automation triggers — quality gates, formatting, validation]
- Required tools: [tools/MCP list]

**Items Requiring Confirmation**:
1. [Question1]
2. [Question2]
```

### Step 3: Confirmation Dialogue

Short confirmation questions based on the analysis:

- "Is my understanding correct?"
- "Is there anything to add or modify?"
- "Could you elaborate on [unclear part]?"

### Step 4: Generate

Generate workflow.md after confirmation is complete.

---

## Absolute Standards

### Absolute Standard 1: Quality of Final Output

> **Speed and token cost are completely ignored.**
> The absolute criterion for all design decisions is the **quality and highest-level result of the final output**.
> Choose to add steps to improve quality rather than reduce steps for speed.
> Even if adding steps for quality increases SOT state complexity, this is acceptable (Absolute Standard 1 > Absolute Standard 2).

### Absolute Standard 2: Single-File SOT + Hierarchical Memory Structure

> **Under a single-file SOT (Single Source of Truth) + hierarchical memory structure design, dozens of agents can operate simultaneously without data inconsistencies.**

Design implications of this rule:
- **State management**: All shared state in the workflow is concentrated in a **single file** (e.g., `state.json`). Do not distribute state across multiple files.
- **Memory hierarchy**: Clearly separate agent-local memory (task context) from global memory (shared state).
- **Write permissions**: Only the Orchestrator or a designated single agent has write access to the SOT file. Other agents access it read-only, or deliver results to the Orchestrator for merging.
- **Conflict prevention**: Do not design structures where parallel agents (Agent Team/Swarm) modify the same data simultaneously.

```
Bad:  Agent A → directly modifies state.json
      Agent B → directly modifies state.json  → data conflict/inconsistency
Good: Agent A → reports results to Orchestrator
      Agent B → reports results to Orchestrator
      Orchestrator → merges into state.json  → single write point, no inconsistency
```

### Absolute Standard 3: Code Change Protocol (CCP)

> **When writing or modifying code in workflow implementation (Phase 2), always perform these 3 steps: Intent Capture → Impact Scope Analysis → Change Design.**

Workflow components (Sub-agent, Hook, SOT, Slash Command, MCP) are interdependent. A change in one component can cause ripple effects in others, so always analyze the impact scope before making code changes.

- **Step 1 — Intent Capture**: Accurately identify the purpose and constraints of the change.
- **Step 2 — Impact Scope Analysis**: Check directly dependent modules, call relationships, SOT files, configuration/environment, test code, and documentation.
- **Step 3 — Change Design**: Design the change sequence, create a modification plan for all affected files, then execute.

> Proportionality rule: Document modifications in the workflow design phase (Phase 1) are trivial changes (Step 1 only); code changes in the implementation phase (Phase 2) are standard/large-scale changes (all 3 steps).

### Priority Among Absolute Standards

> **Absolute Standard 1 (quality) is supreme. Absolute Standard 2 (SOT) and Absolute Standard 3 (CCP) are co-equal means to guarantee quality.**
> Designs that degrade final output quality to maintain SOT structure are not permitted.
> Designs that degrade final output quality to comply with CCP are not permitted.

All Absolute Standards supersede the design principles below. When principles conflict, Absolute Standards always take precedence; when Absolute Standards conflict, follow **Absolute Standard 1 > (Absolute Standard 2, Absolute Standard 3)**.

---

## Genome Inheritance Protocol

> **When generating a child, structurally inherit the parent's complete genome. Generating a child without inheritance is not permitted.**

AgenticWorkflow is the parent organism that generates child workflows. `workflow-generator` is the production line, and every child born on this line carries the parent's complete genome as an `Inherited DNA` section.

### Inheritance Mechanism

| Parent Genome (DNA) | Form embedded in child |
|---------------|-------------------|
| 3 Absolute Standards | `Inherited DNA` section — contextualized for the domain |
| SOT pattern | `state.yaml` in Configuration + single write point |
| 3-phase structure | Research → Planning → Implementation workflow structure |
| 4-layer validation | `Verification` + `pACS` fields |
| P1 containment | Hook-based deterministic validation |
| Safety Hook | PreToolUse blocking pattern |
| Adversarial Review | `Review:` field — `@reviewer` / `@fact-checker` |
| Decision Log | `autopilot-logs/` pattern |
| Context Preservation | Cross-session memory preservation pattern |

### Expression vs Inheritance

Just as cells with identical genomes perform different functions, child systems **express** on the same DNA according to their domain. For example, in a research automation system the Research phase genes express strongly; in software development automation the CCP (Code Change Protocol) genes express strongly. The purpose differs but the genome is the same.

### Mandatory Actions on Generation

1. Include an `Inherited DNA (Parent Genome)` section in every workflow.md (see template)
2. Include `parent_genome` metadata in every state.yaml (see SOT template)
3. Child agent definitions reflect the parent's quality standards (Absolute Standard 1)

Details: `soul.md §0`, `AGENTS.md §1 Reason for Existence`.

---

## Design Principles (Required)

Principles that must be applied when designing workflows. However, all principles are **subordinate to all Absolute Standards (1. Quality First, 2. Single-File SOT, 3. Code Change Protocol)**.

### P1. Data Refinement for Accuracy

Passing large amounts of data directly to AI introduces noise that **reduces accuracy**. Refine data so agents can focus on the core.

- Specify **data pre-processing** at each step: remove noise via Python scripts etc. before passing to AI → **improves analysis accuracy**
- Specify **post-processing** at each step: refine output before passing to the next step → **improves next step quality**
- **Pre-calculate** data relationships at code level where possible → **allows AI to focus on judgment and analysis**

```
Bad:  "Pass entire collected webpage HTML to the agent" → noise degrades analysis quality
Good: "Extract body text only with Python script → pass only key text to agent" → improved analysis accuracy
```

### P2. Expertise-Based Delegation Structure

Delegate each task to **the specialized agent best suited** to maximize quality. The Orchestrator coordinates overall quality; specialized agents focus deeply on their domain.

```
Orchestrator (quality coordination and overall flow management)
  ├→ Sub-agent A: specialized research (optimized for the domain)
  ├→ Sub-agent B: deep analysis (focused on analysis only)
  └→ Skill C: apply validated patterns (quality-assured reusable logic)
```

### P3. Image/Resource Accuracy

For steps requiring image resources, specify **exact download paths**. All placeholders must be extracted; omission is not permitted.

### P4. Question Design Rules

When asking questions to users:
- Maximum 4 questions
- Provide **~3 options** (sub-agent/skill/recommended options, etc.) for each question
- Proceed without questions when there is no ambiguity

---

## Workflow Basic Structure

All workflows consist of 3 phases:

1. **Research**: Information collection and analysis
2. **Planning**: Plan formulation and structuring
3. **Implementation**: Actual execution and artifact generation

**Items that must be included in each step:**
- Task to perform (Task)
- Responsible agent (@agent)
- Data pre-processing (Pre-processing) — noise removal for accuracy improvement (P1)
- Output (Output)
- Adversarial review (Review) — `@reviewer`, `@fact-checker`, or `none` (AGENTS.md §5.5)
- Translation (Translation) — `@translator` or `none` (text artifacts only)
- Post-processing (Post-processing) — refinement to guarantee next step quality (P1)

## Claude Code Component Mapping

| Workflow Element | Claude Code Implementation | Selection Criteria |
|---------------|-----------------|----------|
| Single task delegation | Sub-agent (`.claude/agents/*.md`) | Deep focus on specialized domain, maximize quality |
| Large-scale parallel collaboration | Agent Team/Swarm (`TeamCreate`) | Perform independent tasks simultaneously across multiple sessions |
| Human intervention step | Slash command (`.claude/commands/`) | User interaction for review/approval/selection |
| Automated validation/triggers | Hooks (`settings.json`) | Formatting, quality gates, security validation |
| Reusable logic | Skill (`.claude/skills/`) | Domain knowledge, recurring patterns |
| External integration | MCP Server | API, DB, external service integration |

### Sub-agent vs Agent Team Selection Criteria

> **The only selection criterion is "which structure maximizes final output quality."**
> Do not choose Agent Team just because parallel processing is faster.
> Do not choose Sub-agent just because it uses fewer tokens.

| Situation | Choice | Quality Rationale |
|------|------|----------|
| One expert must maintain deep context for highest quality | **Sub-agent** | Maintains consistent depth within a single context |
| Different specialized domains each need maximum quality | **Agent Team** | Each expert focuses 100% on their domain in an independent context |
| Multi-perspective analysis/cross-validation improves quality | **Agent Team** | Independent perspectives combine for richer results than a single agent |
| Accuracy of context transfer between steps is critical to quality | **Sub-agent sequential calls** | Accurately passes step artifacts to the next step |

> **Absolute Standard 2 mandatory accompaniment**: When choosing Agent Team, always define SOT design together — SOT file location, Team Lead's single write authority, teammate artifact file creation rules. Agent Teams without SOT design are not permitted in principle. Details: `references/claude-code-patterns.md` state management section.
>
> **Absolute Standard 1 priority exception**: For completely independent parallel tasks (agents share no state and do not reference each other's artifacts), SOT can be lightweight only when it is explicitly demonstrated that SOT design does not contribute to quality. This judgment must be documented at workflow design time.

## Reference Documents

- workflow.md template: `references/workflow-template.md`
- Claude Code implementation patterns (Sub-agents, Teams, Hooks): `references/claude-code-patterns.md`
  - Anti-Skip Guard Protocol: §Anti-Skip Execution Protocol (artifact validation — 100 bytes minimum size)
  - Autopilot Execution Checklist: §Autopilot + Agent Team integrated checklist
  - SOT state management: §SOT State Management Protocol
- Document analysis guide (Case 2): `references/document-analysis-guide.md`
- Context injection patterns (Sub-agent/Team input delivery): `references/context-injection-patterns.md`
- SOT template (state.yaml bootstrap): `references/state.yaml.example`
- Autopilot Decision Log template: `references/autopilot-decision-template.md`

## Final Generation Procedure

1. Identify the case (document present or not)
2. Case 1: Collect requirements via conversation / Case 2: Analyze document → confirmation dialogue
3. **Genome Inheritance**: Include `Inherited DNA (Parent Genome)` section in workflow.md (Inheritance Protocol — see `references/workflow-template.md`). Use the workflow generation date (YYYY-MM-DD) as `parent_genome.version`. Include Coding Attitude Points (CAP-1~4) when contextualizing CCP.
4. Apply design principles P1~P4 and define tasks in the 3-phase structure
   - Evaluate the need for Domain Knowledge Structure (DKS): Include a DKS construction step in the Research phase for workflows requiring domain-specialized reasoning (medical, legal, competitive analysis, etc.). Workflows using DKS include `python3 .claude/hooks/scripts/validate_domain_knowledge.py --project-dir . --check-output --step N` in Post-processing of relevant steps. Details: `AGENTS.md §5.3 DKS`
5. Specify data pre-processing/post-processing at each step (P1)
6. Mark human-in-the-loop points
7. **Define `Verification` field at each step** (AGENTS.md §5.3 — required):
   - Place `Verification` field **before** the `Task` field (agent perceives it first)
   - **`Verification` is required for all agent execution steps** — regardless of Research/Planning/Implementation phase (Research steps also require "completeness" verification, e.g., "all 5 competitors analyzed")
   - `(human)` steps are the only exception — no `Verification` field needed since the human is the verifier
   - Each criterion must be written as a **specific statement that a third party can judge true/false**
   - Combine 5 criterion types:
     - **Structural completeness**: Internal structure of the artifact → "all 5 sections included", "each item has 3+ sub-items"
     - **Functional goal**: Task goal achieved → "price data for 3+ competitors", "all API endpoints implemented"
     - **Data consistency**: Data accuracy → "all URLs valid, no placeholders", "numeric data sources cited"
     - **Pipeline connectivity**: Next step input compatibility → "includes fields required by Step N", "output format matches Step N+1 input"
     - **Cross-step traceability**: Logical derivation from prior steps → "80%+ of analysis claims traceable via [trace:step-N] markers"
   - **Tip**: Using `(source: Step N)` annotations in criteria makes Verification criteria explicitly reference prior steps, automating upstream impact analysis during diagnosis. Example: "Competitor analysis data reflects Step 2 research results (source: Step 2)"
8. Set **Review field** at each step (AGENTS.md §5.5 — optional):
   - Research/analysis artifacts (fact verification needed) → `@fact-checker`
   - Code/technical artifacts (logic/completeness verification needed) → `@reviewer`
   - High-risk steps (both) → `@reviewer + @fact-checker`
   - Low-risk or intermediate steps → `none` (L1.5 only)
   - **Execution order**: Review PASS → Translation (translation prohibited when Review is FAIL)
9. Set **Translation field** at each step — `@translator` for text artifacts (`.md`, `.txt`); `none` for code/data/configuration
10. Add Claude Code implementation design (Sub-agents, Teams, Hooks, Commands, Skills, MCP)
   - **Select Context Injection pattern** (per agent step):
     - Input < 50KB → Pattern A (Full Delegation — pass file path)
     - Input 50-200KB + partially relevant → Pattern B (Filtered — refine via Pre-processing script then pass)
     - Input > 200KB or needs splitting → Pattern C (Recursive Decomposition — chunk parallel processing)
     - Absolute Standard 1 priority: Choose Pattern B when filtering improves quality regardless of size
     - Details: `references/context-injection-patterns.md`
   - **SOT design is mandatory when using Agent Team** (Absolute Standard 2):
     - SOT file location (`.claude/state.yaml`), Team Lead single write authority, teammate artifact rules
     - `active_team` schema: name, status, tasks_completed/pending, completed_summaries
     - 4 SOT update points: immediately after TeamCreate → on Teammate completion → on all complete → immediately after TeamDelete
     - Details: `references/workflow-template.md §Agent Team SOT Schema`
   - **Checkpoint Pattern**: Evaluate expected turn count for each Task to select `standard` (≤ 10 turns) or `dense` (> 10 turns) pattern. Details: `references/claude-code-patterns.md §DCP`
11. **Apply English-First execution principle** (AGENTS.md §5.2):
   - Write all agent Task descriptions and prompts in **English** (maximize AI performance — Absolute Standard 1)
   - User dialogue (workflow design) in Korean; agent execution in English
   - `@translator` sub-agent handles English→Korean translation (specify via Translation field)
12. Generate workflow.md file
13. **(Optional) Distill validation**: Quality check to maximize the generated workflow
    - "Does this step contribute to final quality?" — remove only steps irrelevant to quality
    - "Does automating this step make quality more stable?" — identify automation opportunities
    - "Are there steps to add for quality improvement?" — add validation/reinforcement steps
    - "Does each `Verification` criterion include **pipeline connectivity**?" — verify inter-step data flow
    - **DNA Inheritance P1 validation**: Run `python3 .claude/hooks/scripts/validate_workflow.py --workflow-path ./workflow.md` → confirm W1-W8 pass
    - Reference: `prompt/distill-partner.md`

## Autopilot Mode Support

Include Autopilot Mode fields in the workflow.md you generate.

- Add `- **Autopilot**: [disabled|enabled]` to the Overview section (default: disabled)
- Set to `enabled` when the user requests "run automatically", "uninterrupted execution", etc.
- Do not change the `(human)` step design itself — Autopilot is an execution mode, not a design change
- Optional: Specify default auto-approval behavior for each `(human)` step via an `Autopilot Default` field

## pACS Support

Include pACS (self-confidence rating) fields in the workflow.md you generate.

- Add `- **pACS**: [enabled|disabled]` to the Overview section (default: enabled, AGENTS.md §5.4)
- pACS operates independently from Autopilot mode — applies even in manual execution
- `(human)` steps do not need pACS since the human is the evaluator (same principle as Verification)
- Set to `disabled` if the user explicitly requests "without pACS" etc.
