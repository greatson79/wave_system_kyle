#!/usr/bin/env python3
"""
Shared DAG definition for the SaaS Auto-Builder PRD Workflow.

This module is the SINGLE source for the step dependency graph.
Imported by: workflow_router.py, task_dag_init.py

Architecture:
  - Hardcoded DAG — NOT parsed from workflow.md at runtime (GAP-H2).
  - Each step has: name, deps, type, team, human flag, pre_script,
    review agent, translate flag.
  - Team membership defined in TEAMS dict.

P1 Compliance: Pure data — no I/O, no side effects, deterministic.
"""

# ---------------------------------------------------------------------------
# Step Dependency Graph
# ---------------------------------------------------------------------------
DAG = {
    1: {
        "name": "PRD Foundation Extraction",
        "deps": [],
        "type": "sub-agent",
        "agent": "prd-analyst",
        "team": None,
        "human": False,
        "pre_script": "extract_prd_sections.py",
        "review": None,
        "translate": True,
        "output": "prompt/research/prd-foundation-analysis.md",
    },
    2: {
        "name": "Multi-Perspective Deep Analysis",
        "deps": [1],
        "type": "agent-team",
        "agent": None,
        "team": "prd-analysis-team",
        "human": False,
        "pre_script": None,
        "review": None,
        "translate": True,
        # Team steps use manifest as SOT output (individual outputs in TEAMS)
        "output": "prompt/research/step-2-manifest.md",
    },
    3: {
        "name": "Research Synthesis & Gap Analysis",
        "deps": [1, 2],
        "type": "sub-agent",
        "agent": "research-synthesizer",
        "team": None,
        "human": False,
        "pre_script": None,
        "review": "fact-checker",
        "translate": True,
        "output": "prompt/research/synthesis-and-gaps.md",
    },
    4: {
        "name": "Research Findings Review",
        "deps": [3],
        "type": "human",
        "agent": None,
        "team": None,
        "human": True,
        "pre_script": None,
        "review": None,
        "translate": False,
        "output": "approved-by-user",
    },
    5: {
        "name": "PRD Document Architecture Design",
        "deps": [4],
        "type": "sub-agent",
        "agent": "prd-architect",
        "team": None,
        "human": False,
        "pre_script": None,
        "review": None,
        "translate": True,
        "output": "prompt/planning/prd-architecture.md",
    },
    6: {
        "name": "Intent Capture & Question Flow Spec",
        "deps": [4],
        "type": "sub-agent",
        "agent": "intent-designer",
        "team": None,
        "human": False,
        "pre_script": None,
        "review": "reviewer",
        "translate": True,
        "output": "prompt/planning/intent-capture-spec.md",
    },
    7: {
        "name": "Engine Pipeline & Quality Framework",
        "deps": [5, 6],
        "type": "sub-agent",
        "agent": "engine-planner",
        "team": None,
        "human": False,
        "pre_script": None,
        "review": "reviewer",
        "translate": True,
        "output": "prompt/planning/engine-quality-specs.md",
    },
    8: {
        "name": "Planning Review & Approval",
        "deps": [7],
        "type": "human",
        "agent": None,
        "team": None,
        "human": True,
        "pre_script": None,
        "review": None,
        "translate": False,
        "output": "approved-by-user",
    },
    9: {
        "name": "PRD Document Generation",
        "deps": [8],
        "type": "agent-team",
        "agent": None,
        "team": "prd-generation-team",
        "human": False,
        "pre_script": None,
        "review": None,
        "translate": True,
        # Team steps use manifest as SOT output (individual outputs in TEAMS)
        "output": "prompt/implementation/step-9-manifest.md",
    },
    10: {
        "name": "Cross-Validation & Integration",
        "deps": [9],
        "type": "sub-agent",
        "agent": "cross-validator",
        "team": None,
        "human": False,
        "pre_script": "merge_prd_sections.py",
        "review": None,
        "translate": False,
        "output": "prompt/implementation/prd-validated.md",
    },
    11: {
        "name": "Adversarial Review",
        "deps": [10],
        "type": "sub-agent",
        "agent": "reviewer",
        "team": None,
        "human": False,
        "pre_script": None,
        "review": None,
        "translate": True,
        "output": "prompt/review/prd-adversarial-review.md",
    },
    12: {
        "name": "Final PRD Review & Approval",
        "deps": [11],
        "type": "human",
        "agent": None,
        "team": None,
        "human": True,
        "pre_script": None,
        "review": None,
        "translate": True,
        # Hybrid: human checkpoint that produces final deliverable
        "output": "prompt/PRD-SaaS-AutoBuilder.md",
    },
}

# ---------------------------------------------------------------------------
# Team Membership
# ---------------------------------------------------------------------------
TEAMS = {
    "prd-analysis-team": {
        "members": [
            {
                "agent": "arch-engine-specialist",
                "task": "Architecture & Engine Pipeline Analysis",
                "output": "prompt/research/arch-engine-analysis.md",
            },
            {
                "agent": "feature-ux-specialist",
                "task": "Feature & Intent Capture Analysis",
                "output": "prompt/research/feature-ux-analysis.md",
            },
            {
                "agent": "biz-quality-specialist",
                "task": "Business Model & Quality Framework Analysis",
                "output": "prompt/research/biz-quality-analysis.md",
            },
        ],
    },
    "prd-generation-team": {
        "members": [
            {
                "agent": "prd-writer-core",
                "task": "Sections 1-5: Foundation & Users",
                "output": "prompt/implementation/prd-sections-1-5.md",
            },
            {
                "agent": "prd-writer-tech",
                "task": "Sections 6-8: Technical Core",
                "output": "prompt/implementation/prd-sections-6-8.md",
            },
            {
                "agent": "prd-writer-integration",
                "task": "Sections 9-12: Systems & Quality",
                "output": "prompt/implementation/prd-sections-9-12.md",
            },
            {
                "agent": "prd-writer-business",
                "task": "Sections 13-16: Business & Appendix",
                "output": "prompt/implementation/prd-sections-13-16.md",
            },
        ],
    },
}

# ---------------------------------------------------------------------------
# Output Directories (per-step phase mapping)
# ---------------------------------------------------------------------------
# Derived from DAG output paths. Used by manifest_generator.py.
STEP_OUTPUT_DIRS = {
    step_num: "/".join(info["output"].split("/")[:-1]) or "prompt"
    for step_num, info in DAG.items()
    if info["output"] != "approved-by-user"
}

# ---------------------------------------------------------------------------
# Translation Points
# ---------------------------------------------------------------------------
# Steps that produce EN+KO pairs (15 translation jobs)
TRANSLATION_STEPS = [1, 2, 3, 5, 6, 7, 9, 11, 12]

# Human checkpoint steps. Note: Step 12 is a hybrid — it's a human approval
# checkpoint that ALSO produces the final deliverable (PRD-SaaS-AutoBuilder.md)
# and triggers translation. The orchestrator handles this by performing the
# copy/translation after user approval, then registering the output in SOT.
HUMAN_STEPS = [4, 8, 12]

# Total steps
TOTAL_STEPS = 12

# Phase identifier — used by quality_gate_runner.py for subprocess routing
PHASE_NAME = "phase1"

# ---------------------------------------------------------------------------
# Step Inputs (explicit map — moved from orchestrator_actions.py for co-location)
# ---------------------------------------------------------------------------
# Maps step number (or "step:agent" for team members) to input file lists.
# Used by orchestrator_actions._get_step_inputs() and validate_l1_document.py.
STEP_INPUTS = {
    # Step 1: prd-analyst
    1: [
        "coding-resource/PRD.md",
    ],
    # Step 2: prd-analysis-team (per-member inputs)
    "2:arch-engine-specialist": [
        "prompt/research/prd-foundation-analysis.md",
        "coding-resource/PRD.md",
    ],
    "2:feature-ux-specialist": [
        "prompt/research/prd-foundation-analysis.md",
        "coding-resource/PRD.md",
    ],
    "2:biz-quality-specialist": [
        "prompt/research/prd-foundation-analysis.md",
        "coding-resource/PRD.md",
    ],
    # Step 3: research-synthesizer
    3: [
        "prompt/research/prd-foundation-analysis.md",
        "prompt/research/arch-engine-analysis.md",
        "prompt/research/feature-ux-analysis.md",
        "prompt/research/biz-quality-analysis.md",
        "coding-resource/PRD.md",
    ],
    # Step 5: prd-architect
    5: [
        "prompt/research/synthesis-and-gaps.md",
        "prompt/research/prd-foundation-analysis.md",
        "prompt/research/arch-engine-analysis.md",
        "prompt/research/feature-ux-analysis.md",
        "prompt/research/biz-quality-analysis.md",
        "coding-resource/PRD.md",
    ],
    # Step 6: intent-designer
    6: [
        "prompt/research/feature-ux-analysis.md",
        "prompt/research/synthesis-and-gaps.md",
        "prompt/research/prd-foundation-analysis.md",
        "prompt/planning/prd-architecture.md",
        "coding-resource/PRD.md",
    ],
    # Step 7: engine-planner
    7: [
        "prompt/planning/prd-architecture.md",
        "prompt/planning/intent-capture-spec.md",
    ],
    # Step 9: prd-generation-team (per-member inputs)
    "9:prd-writer-core": [
        "prompt/planning/prd-architecture.md",
        "prompt/planning/intent-capture-spec.md",
        "prompt/planning/engine-quality-specs.md",
        "prompt/research/synthesis-and-gaps.md",
        "prompt/research/prd-foundation-analysis.md",
    ],
    "9:prd-writer-tech": [
        "prompt/planning/prd-architecture.md",
        "prompt/planning/intent-capture-spec.md",
        "prompt/planning/engine-quality-specs.md",
        "prompt/research/arch-engine-analysis.md",
        "prompt/research/feature-ux-analysis.md",
    ],
    "9:prd-writer-integration": [
        "prompt/planning/prd-architecture.md",
        "prompt/planning/intent-capture-spec.md",
        "prompt/planning/engine-quality-specs.md",
        "prompt/research/arch-engine-analysis.md",
        "prompt/research/biz-quality-analysis.md",
    ],
    "9:prd-writer-business": [
        "prompt/planning/prd-architecture.md",
        "prompt/planning/intent-capture-spec.md",
        "prompt/planning/engine-quality-specs.md",
        "prompt/research/biz-quality-analysis.md",
        "prompt/research/synthesis-and-gaps.md",
    ],
    # Step 10: cross-validator
    10: [
        "prompt/implementation/prd-merged.md",
        "prompt/planning/engine-quality-specs.md",
        "prompt/planning/prd-architecture.md",
    ],
    # Step 11: reviewer + fact-checker (input is Step 10 output)
    11: [
        "prompt/implementation/prd-validated.md",
    ],
}
