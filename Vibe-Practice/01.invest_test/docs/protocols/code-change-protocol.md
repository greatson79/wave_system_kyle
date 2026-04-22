# Code Change Protocol (CCP) — Detailed Specification

> This document is the detailed procedure for Absolute Standard 3 (Code Change Protocol).
> Separated from CLAUDE.md — reference when making code changes.

## 3-Step Protocol

Before writing, modifying, adding, or deleting code, perform the following 3 steps internally.
Skipping this protocol is a violation of Absolute Standards.
Always perform the protocol; depth of analysis is proportional to the impact scope of the change.

### Step 1 — Intent Capture
- Define the purpose of the change (bug fix / feature addition / refactoring / performance) and constraints (compatibility, tech stack) in 1-2 sentences
- For trivial changes (typos, comments, formatting): confirm "no ripple effect" then proceed immediately

### Step 2 — Impact Scope Analysis (Ripple Effect Analysis)
- Direct dependencies + call relationships (caller/callee)
- Structural relationships (inheritance, composition, references)
- Data model / schema / type chain changes
- Tests, configuration, documentation, API specs
- If high coupling or shotgun-surgery risk is detected, **always** notify in advance and consult with the user

### Step 3 — Change Design (Change Plan)
- Step-by-step change sequence (which file/function first → dependency propagation → test/documentation consistency)
- If opportunities to reduce coupling / increase cohesion are visible, propose them together (execute only after user approval)

## Proportionality Rule

| Change Scale | Applied Depth |
|-------------|--------------|
| Trivial (typo, comment) | Step 1 only — confirm no ripple effect |
| Standard (function/logic change) | All 3 steps |
| Large-scale (architecture, API) | All 3 steps + mandatory prior user approval |

## Communication Rules
- Avoid unnecessarily verbose theoretical explanations; focus on practical code and concrete steps.
- Add brief justifications for important design choices.
- Do not avoid work due to ambiguity — state a "reasonable assumption" explicitly, then propose the best design.

## Coding Attitude Points (CAP)

All CCP steps are performed with these 4 internalized attitudes:

- **CAP-1**: Think before coding — do not modify code without reading it first. Surface trade-offs. Ask if unclear.
- **CAP-2**: Simplicity first — minimum code. No speculative features, premature abstractions, or unnecessary helpers.
- **CAP-3**: Goal-based execution — define success criteria first, verify after implementation.
- **CAP-4**: Surgical changes — only the requested change. No unrelated "improvements."

> CAP is subordinate to CCP; when in conflict with Absolute Standard 1 (quality), quality wins. Details: AGENTS.md §2 Absolute Standard 3.
