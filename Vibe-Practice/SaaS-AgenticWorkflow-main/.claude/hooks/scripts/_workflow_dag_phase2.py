#!/usr/bin/env python3
"""
Shared DAG definition for the Full-Stack SaaS Auto-Builder Development Workflow (Phase 2).

This module is the SINGLE source for the Phase 2 step dependency graph.
Mirrors _workflow_dag.py structure for Phase 1 compatibility.

Architecture:
  - Hardcoded DAG — same pattern as Phase 1 _workflow_dag.py.
  - Each step has: name, deps, type, team, human flag, pre_script,
    review agent, translate flag, output, gate_profile.
  - gate_profile: "code" (L1=tsc+eslint) or "document" (L1=D1-D5 structural).
  - Team membership defined in TEAMS dict.

P1 Compliance: Pure data — no I/O, no side effects, deterministic.
"""

# ---------------------------------------------------------------------------
# Step Dependency Graph — Phase 2: Full-Stack Development (16 steps)
# ---------------------------------------------------------------------------
DAG = {
    # ===== Phase A: Analysis & Design (Steps 1-3) =====
    1: {
        "name": "PRD Technical Extraction",
        "deps": [],
        "type": "sub-agent",
        "agent": "prd-tech-analyst",
        "team": None,
        "human": False,
        "pre_script": "extract_engine_specs.py",
        "review": "fact-checker",
        "translate": False,
        "output": "dev/analysis/prd-tech-analysis.md",
        "gate_profile": "document",
    },
    2: {
        "name": "Architecture Design",
        "deps": [1],
        "type": "agent-team",
        "agent": None,
        "team": "architecture-design-team",
        "human": False,
        "pre_script": None,
        "review": "reviewer",
        "translate": False,
        "output": "dev/architecture/step-2-manifest.md",
        "gate_profile": "document",
    },
    3: {
        "name": "Architecture Review",
        "deps": [2],
        "type": "human",
        "agent": None,
        "team": None,
        "human": True,
        "pre_script": None,
        "review": None,
        "translate": False,
        "output": "approved-by-user",
        "gate_profile": None,
    },

    # ===== Phase B: Core Implementation (Steps 4-10) =====
    4: {
        "name": "Project Scaffolding",
        "deps": [3],
        "type": "sub-agent",
        "agent": "project-scaffolder",
        "team": None,
        "human": False,
        "pre_script": "generate_project_config.py",
        "review": None,
        "translate": False,
        "output": "src/package.json",  # Representative file — L0 checks this
        "gate_profile": "code",
    },
    5: {
        "name": "Schema & Registry Implementation",
        "deps": [4],
        "type": "sub-agent",
        "agent": "schema-designer",
        "team": None,
        "human": False,
        "pre_script": None,
        "review": "code-reviewer",
        "translate": False,
        "output": "src/registries/index.ts",
        "gate_profile": "code",
    },
    6: {
        "name": "Engine Implementation — Front-End (E1-E3)",
        "deps": [5],
        "type": "agent-team",
        "agent": None,
        "team": "engine-frontend-team",
        "human": False,
        "pre_script": "extract_engine_context.py",
        "review": "code-reviewer",
        "translate": False,
        "output": "dev/implementation/step-6-manifest.md",
        "gate_profile": "code",
    },
    7: {
        "name": "Engine Implementation — Core (E4-E6)",
        "deps": [5],
        "type": "agent-team",
        "agent": None,
        "team": "engine-analysis-team",
        "human": False,
        "pre_script": "extract_engine_context.py",
        "review": "code-reviewer",
        "translate": False,
        "output": "dev/implementation/step-7-manifest.md",
        "gate_profile": "code",
    },
    8: {
        "name": "Engine Implementation — Back-End (E7-E9)",
        "deps": [5],
        "type": "agent-team",
        "agent": None,
        "team": "code-generation-team",
        "human": False,
        "pre_script": "extract_engine_context.py",
        "review": "code-reviewer",
        "translate": False,
        "output": "dev/implementation/step-8-manifest.md",
        "gate_profile": "code",
    },
    9: {
        "name": "Template System & CLI Implementation",
        "deps": [6, 7, 8],
        "type": "sub-agent",
        "agent": "template-architect",
        "team": None,
        "human": False,
        "pre_script": None,
        "review": "code-reviewer",
        "translate": False,
        "output": "src/cli/index.ts",
        "gate_profile": "code",
    },
    10: {
        "name": "Integration Wiring",
        "deps": [6, 7, 8, 9],
        "type": "sub-agent",
        "agent": "api-engineer",
        "team": None,
        "human": False,
        "pre_script": "collect_engine_interfaces.py",
        "review": "code-reviewer",
        "translate": False,
        "output": "src/pipeline/index.ts",
        "gate_profile": "code",
    },

    # ===== Phase C: Integration & Testing (Steps 11-14) =====
    11: {
        "name": "Unit Test Suite",
        "deps": [10],
        "type": "sub-agent",
        "agent": "test-engineer",
        "team": None,
        "human": False,
        "pre_script": "analyze_test_coverage.py",
        "review": None,
        "translate": False,
        "output": "tests/unit/index.test.ts",
        "gate_profile": "code",
    },
    12: {
        "name": "Integration Review",
        "deps": [11],
        "type": "human",
        "agent": None,
        "team": None,
        "human": True,
        "pre_script": None,
        "review": None,
        "translate": False,
        "output": "approved-by-user",
        "gate_profile": None,
    },
    13: {
        "name": "Integration & E2E Testing",
        "deps": [12],
        "type": "sub-agent",
        "agent": "test-engineer",
        "team": None,
        "human": False,
        "pre_script": "generate_test_fixtures.py",
        "review": "code-reviewer",
        "translate": False,
        "output": "tests/e2e/pipeline.test.ts",
        "gate_profile": "code",
    },
    14: {
        "name": "Adversarial Code Review",
        "deps": [13],
        "type": "sub-agent",
        "agent": "code-reviewer",
        "team": None,
        "human": False,
        "pre_script": "collect_review_targets.py",
        "review": None,  # This step IS the review
        "translate": False,
        "output": "dev/review/code-review-report.md",
        "gate_profile": "code",
    },

    # ===== Phase D: Delivery (Steps 15-16) =====
    15: {
        "name": "Documentation & Polish",
        "deps": [14],
        "type": "sub-agent",
        "agent": "docs-engineer",
        "team": None,
        "human": False,
        "pre_script": None,
        "review": "reviewer",
        "translate": True,
        "output": "README.md",
        "gate_profile": "document",
    },
    16: {
        "name": "Release Approval",
        "deps": [15],
        "type": "human",
        "agent": None,
        "team": None,
        "human": True,
        "pre_script": None,
        "review": None,
        "translate": False,
        "output": "approved-by-user",
        "gate_profile": None,
    },
}

# ---------------------------------------------------------------------------
# Team Membership
# ---------------------------------------------------------------------------
TEAMS = {
    "architecture-design-team": {
        "members": [
            {
                "agent": "engine-architect",
                "task": "System Architecture — engine pipeline, module boundaries, interfaces",
                "output": "dev/architecture/system-architecture.md",
            },
            {
                "agent": "schema-designer",
                "task": "Data Model — 6 Zod registries, shared types, IntentObject",
                "output": "dev/architecture/data-model-design.md",
            },
            {
                "agent": "template-architect",
                "task": "Template System — Handlebars hierarchy, generated file structure, LLM boundary",
                "output": "dev/architecture/template-system-design.md",
            },
        ],
    },
    "engine-frontend-team": {
        "members": [
            {
                "agent": "engine-impl-e1",
                "task": "E1 NLU/Intent Engine — 7-state FSM, domain classification, slot extraction",
                "output": "src/engines/e1-intent/index.ts",
            },
            {
                "agent": "engine-impl-e2",
                "task": "E2 AI PM Engine — PRD expansion, Feature Registry population",
                "output": "src/engines/e2-aipm/index.ts",
            },
            {
                "agent": "engine-impl-e3",
                "task": "E3 Tool Selection Engine — tech stack selection, Dependency Registry",
                "output": "src/engines/e3-tools/index.ts",
            },
        ],
    },
    "engine-analysis-team": {
        "members": [
            {
                "agent": "engine-impl-e4",
                "task": "E4 Feature Extraction Engine — Frame Semantics, ToT discovery, priority scoring",
                "output": "src/engines/e4-features/index.ts",
            },
            {
                "agent": "engine-impl-e5",
                "task": "E5 User Research Engine — persona synthesis, user story generation",
                "output": "src/engines/e5-research/index.ts",
            },
            {
                "agent": "engine-impl-e6",
                "task": "E6 Document Pipeline Engine — 7-document DAG, registry-driven SOT",
                "output": "src/engines/e6-docs/index.ts",
            },
        ],
    },
    "code-generation-team": {
        "members": [
            {
                "agent": "engine-impl-e7",
                "task": "E7 Orchestration Engine — pipeline state machine, error recovery, progress reporting",
                "output": "src/engines/e7-orchestration/index.ts",
            },
            {
                "agent": "engine-impl-e8",
                "task": "E8 Code Generation Engine — 3-phase strategy, Handlebars + LLM",
                "output": "src/engines/e8-codegen/index.ts",
            },
            {
                "agent": "engine-impl-e9",
                "task": "E9 Meta-Programming Engine — AGENTS.md + CLAUDE.md DNA injection",
                "output": "src/engines/e9-meta/index.ts",
            },
        ],
    },
}

# ---------------------------------------------------------------------------
# Output Directories (per-step phase mapping)
# ---------------------------------------------------------------------------
STEP_OUTPUT_DIRS = {
    step_num: "/".join(info["output"].split("/")[:-1]) or "."
    for step_num, info in DAG.items()
    if info["output"] != "approved-by-user"
}

# ---------------------------------------------------------------------------
# Translation Points
# ---------------------------------------------------------------------------
# Phase 2: Only documentation step (Step 15) produces EN+KO pairs.
# All code steps are NOT translated (technical output).
TRANSLATION_STEPS = [15]

# Human checkpoint steps
HUMAN_STEPS = [3, 12, 16]

# Total steps
TOTAL_STEPS = 16

# Phase identifier — used by quality_gate_runner.py for subprocess routing
PHASE_NAME = "phase2"

# ---------------------------------------------------------------------------
# Phase 2-specific constants
# ---------------------------------------------------------------------------
# pACS dimensions: 4D for code (adds T = Testability)
PACS_DIMENSIONS = ["F", "C", "L", "T"]

# Gate profiles: determines which L1 gate to use per step
# "code" → L1 = tsc --noEmit (deterministic)
# "document" → L1 = D1-D5 structural verification
# None → human steps (no L1 gate)
GATE_PROFILES = {
    step_num: info["gate_profile"]
    for step_num, info in DAG.items()
}

# Steps that use L3 Integration Gate (full build + test + E2E)
L3_STEPS = [13]

# Phase 2 Explicit Input Map (C-1 pattern: eliminates incomplete DAG-tracing)
STEP_INPUTS = {
    # Step 1: prd-tech-analyst — reads approved PRD from Phase 1
    1: [
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    # Step 2: architecture-design-team (per-member inputs)
    "2:engine-architect": [
        "dev/analysis/prd-tech-analysis.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    "2:schema-designer": [
        "dev/analysis/prd-tech-analysis.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    "2:template-architect": [
        "dev/analysis/prd-tech-analysis.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    # Step 4: project-scaffolder
    4: [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/architecture/template-system-design.md",
    ],
    # Step 5: schema-designer (implementation)
    5: [
        "dev/architecture/data-model-design.md",
        "dev/architecture/system-architecture.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    # Step 6: engine-frontend-team (per-member inputs)
    "6:engine-impl-e1": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/engine-context/e1-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    "6:engine-impl-e2": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/engine-context/e2-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    "6:engine-impl-e3": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/engine-context/e3-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    # Step 7: engine-analysis-team (per-member inputs)
    "7:engine-impl-e4": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/engine-context/e4-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    "7:engine-impl-e5": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/engine-context/e5-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    "7:engine-impl-e6": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/engine-context/e6-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    # Step 8: code-generation-team (per-member inputs)
    "8:engine-impl-e7": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/engine-context/e7-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    "8:engine-impl-e8": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/architecture/template-system-design.md",
        "dev/engine-context/e8-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    "8:engine-impl-e9": [
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
        "dev/engine-context/e9-context.md",
        "prompt/PRD-SaaS-AutoBuilder.md",
    ],
    # Step 9: template-architect (implementation)
    9: [
        "dev/architecture/template-system-design.md",
        "dev/architecture/system-architecture.md",
        "dev/architecture/data-model-design.md",
    ],
    # Step 10: api-engineer (integration wiring)
    10: [
        "dev/architecture/system-architecture.md",
        "dev/integration/engine-interfaces.json",
    ],
    # Step 11: test-engineer (unit tests)
    11: [
        "dev/testing/coverage-gaps.json",
    ],
    # Step 13: test-engineer (integration + E2E)
    13: [
        "tests/fixtures/",
    ],
    # Step 14: code-reviewer (adversarial review)
    14: [
        "dev/review/review-manifest.json",
    ],
    # Step 15: docs-engineer
    15: [
        "dev/review/code-review-report.md",
    ],
}
