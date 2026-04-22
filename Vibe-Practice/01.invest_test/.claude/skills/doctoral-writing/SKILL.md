---
name: doctoral-writing
description: Doctoral-level academic writing skill. Implements academic writing style with both scholarly rigor and readability. Supports Korean and English, applicable across humanities, social sciences, and natural sciences. Use when the user requests "write in thesis style", "academic writing", "doctoral thesis style", "academic writing", "refine sentences for a paper", "revise to academic expression", etc. Applied to dissertations, journal submissions, research reports, and academic presentations.
---

# Doctoral-Level Academic Writing

## Overview

This skill systematically supports academic writing with doctoral-level scholarly rigor and clarity. Supports both Korean and English, reflecting academic conventions across humanities, social sciences, and natural sciences.

Core philosophy: **"Clear and concise" writing is not "simple and short" writing. It is writing that efficiently conveys complex ideas.** It is about eliminating unnecessary elements to reveal the core.

## When to Use This Skill

- Dissertation/thesis chapter review and writing
- Academic journal submission proofreading and improvement
- Research reports, academic presentation writing
- Academic writing instruction and feedback
- Applying style in Korean ↔ English academic translation
- **Primary Use Case**: Writing Phase standard for doctoral research workflows

## Absolute Standards

### Absolute Standard 1: Scholarly Quality of Final Manuscript

> **Number of revisions, workload, and length limits are completely ignored.**
> The absolute criterion for all writing/revision decisions is the **scholarly quality of the final manuscript — rigor, clarity, depth of argumentation**.
> Choose to repeat revisions to improve quality rather than finishing quickly with fewer revisions.
> Do not sacrifice scholarly depth or nuance for brevity.

### Absolute Standard 2: Manuscript Consistency — Single SOT + Hierarchical Structure

> **Consistency of terminology, argumentation, citations, and style throughout the manuscript is the foundation of scholarly credibility.**
> The manuscript itself is the single SOT (Single Source of Truth), and all revisions must preserve consistency throughout.

Design implications of this rule:
- **Terminology SOT**: Once technical terms and abbreviations are established at first use in the manuscript, they are used consistently throughout. Avoid "elegant variation."
- **Argumentation SOT**: The research questions/hypotheses in the introduction are the consistent axis threading methodology, results, and discussion. Ensure that revising one section does not conflict with argumentation in other sections.
- **Citation SOT**: Citation style (APA, Chicago, etc.) follows a single style throughout the manuscript. In-text citations and reference lists must correspond 1:1.
- **Style SOT**: Choices of person (first/third), tense, and active/passive voice are decided once according to disciplinary convention and applied consistently throughout the manuscript.

```
Bad:  Chapter 1 defines "self-efficacy (자기효능감)"
      Chapter 3 uses variant "sense of self-efficacy"  → terminology inconsistency, reduced scholarly credibility
Good: Chapter 1 defines "self-efficacy (자기효능감)"
      Used consistently as "self-efficacy" throughout  → single terminology SOT
```

### Absolute Standard 3: Code Change Protocol (CCP)

> **This is N/A in the application domain of this skill (academic writing).**

However, when modifying the skill's own code (SKILL.md, references/ files), Absolute Standard 3 applies. See AGENTS.md for the detailed protocol.

### Priority Among Absolute Standards

> **Absolute Standard 1 (quality) is supreme. Absolute Standard 2 (consistency) and Absolute Standard 3 (CCP) are co-equal means to guarantee quality.**
> Revisions that degrade scholarly accuracy or argumentation quality to maintain consistency are not permitted.
> Consistency is a means to guarantee quality, not a purpose that constrains quality.

```
Conflict Scenario 1 — Terminology Accuracy vs Terminology Consistency:
  Chapter 1 used "structural inequality," but Chapter 4 analysis reveals
  "systemic inequality" is the more academically precise concept.
  → Absolute Standard 1 takes precedence: change to the more precise term,
    and retroactively revise Chapter 1 to restore consistency.

Conflict Scenario 2 — Style Consistency vs Argumentation Quality:
  The manuscript uses third person throughout, but in the reflexivity section
  of qualitative research, first person would enhance authenticity and depth.
  → Absolute Standard 1 takes precedence: allow first person in that section
    + explicitly note the person shift rationale within the manuscript.
```

All Absolute Standards supersede the core principles below. When principles conflict, Absolute Standards always take precedence; when Absolute Standards conflict, follow **Absolute Standard 1 > (Absolute Standard 2, Absolute Standard 3)**.

---

## Core Writing Principles

> The following 4 core principles are **subordinate to all Absolute Standards (1. Quality, 2. Consistency, 3. CCP)**. When principles conflict, Absolute Standards take precedence.

### 1. Clarity

Convey core ideas precisely so readers do not have to guess the author's intent.

**Key Requirements**:
- Clear subject-predicate alignment
- Clarity of key terms and key sentences
- Technical terms must be defined at first use
- Prefer active voice (where appropriate)
- Precise word selection

**Common Issues**:
- Ambiguous pronouns/demonstratives
- Relational confusion from multiple clauses
- Undefined technical terms/abbreviations
- Unclear antecedent in long sentences

### 2. Conciseness

Express ideas with minimum words without losing meaning or nuance.

**Key Requirements**:
- One sentence = one idea (One Sentence, One Idea)
- Three-tier sentence length standard:
  - **Recommended**: Korean 20-40 characters, English 15-25 words
  - **Caution**: Korean over 40 chars, English over 25 words → consider splitting
  - **Maximum**: Korean 60 chars, English 30 words — must split
- Remove unnecessary modifiers, adjectives, adverbs
- Replace redundant expressions and verbose constructions

**Common Issues**:
- Verbose sentences with multiple parentheticals and elaborations
- Redundant expressions (e.g., "past history", "future plans")
- Overuse of weak copula constructions
- Excessive prepositional phrases

### 3. Academic Rigor

Maintain scholarly standards and accuracy while writing accessibly for target academic audiences.

**Key Requirements**:
- Use technical terms only when necessary
- Define important concepts at first use
- Follow disciplinary conventions
- Support claims with evidence and citations
- Maintain formal academic tone (typically third person)
- Choose verbs that precisely describe actions and relationships

### 4. Logical Flow

Ideas develop in clear and logical order, with explicit connections between sentences and paragraphs.

**Key Requirements**:
- One main idea per paragraph
- Clear topic sentence
- Effective transition expressions
- Consistent argumentation structure
- Explicit relationship between claims and evidence

## Quick Reference: Practical Revision Rules

### Expressions to Delete

| Type | Target | Replacement/Action |
|------|----------|----------|
| Modifier excess | various, several, diverse | Replace with specific numbers or categories |
| Adverb overuse | very, considerably, somewhat, relatively | Replace with quantitative expression |
| Passive habit | "it is considered that", "it is found that" | Convert to active form |
| Indirect expressions | "it is deemed that", "it can be seen that" | Shorten to direct statement |
| Redundancies | "approximately ~degree", "most optimal" | Use only one |

### Conversion Examples (Korean academic writing)

```
❌ 본 연구에서는 다양한 요인들에 대한 분석을 통해 그 결과를 도출하고자 하였다.
✅ 본 연구는 세 가지 요인을 분석하여 인과관계를 규명하였다.

❌ 매우 다양한 선행연구들에서 이러한 현상이 발견되어진 바 있다.
✅ 12편의 선행연구에서 이 현상을 보고하였다.

❌ 비교적 상당히 긍정적인 결과가 도출된 것으로 사료된다.
✅ 효과크기 0.65로 중간 수준의 긍정적 결과를 얻었다.
```

### Conjunction Usage Principles

**Permitted conjunctions**:
- **Causal**: therefore (따라서), thus (그러므로), accordingly (이에)
- **Contrast**: however (그러나), whereas (반면), meanwhile (한편)
- **Elaboration**: that is (즉), in other words (다시 말해)
- **Sequential**: first/second, first/next

**Conjunctions to minimize**:
- "and" / "그리고" (replace with parallel structure)
- "so" / "그래서" (replace with "therefore")
- "also" / "또한" (integrate sentences or delete)
- "additionally" / "아울러, 더불어" (integrate into parallel structure)

```
❌ 설문조사를 실시하였다. 그리고 인터뷰도 진행하였다. 또한 관찰도 수행하였다.
✅ 설문조사, 인터뷰, 참여관찰을 실시하였다.
```

### Academic Vocabulary Selection

**Colloquial → Academic conversion**:

| Colloquial | Academic |
|--------|------------|
| ~해서 | ~하여, ~함으로써 |
| 알아보다 | 분석하다, 검토하다, 고찰하다 |
| 보여주다 | 나타내다, 시사하다, 제시하다 |
| 생각하다 | 판단하다, 사료하다, 추론하다 |
| 쓰이다 | 사용되다, 활용되다, 적용되다 |

**Vagueness → Specificity**:

| Vague | Specific |
|------|------|
| many studies | 37 studies |
| recently | since 2020 |
| most | 78.3% |
| significant difference | t(45)=2.31, p<.05 |

### Argumentation Tone

```
❌ 나는 이 결과가 매우 중요하다고 생각한다.
✅ 이 결과는 기존 이론의 확장에 기여한다.

❌ 이것은 정말 놀라운 발견이다.
✅ 이 발견은 선행연구와 상이한 패턴을 보인다.
```

**Hedging expressions** (use appropriately):
- ~로 해석된다 / ~가능성을 시사한다
- ~으로 추정된다 / ~것으로 판단된다

## Workflow

### Step 1: Understand the Context

Before providing feedback or revisions, first identify:

1. **Document type and audience**:
   - Dissertation chapter, journal article, conference presentation, thesis?
   - Target journal or academic audience?
   - Discipline (humanities, social sciences, natural sciences)?

2. **Scope of work**:
   - Full manuscript review?
   - Sentence/paragraph-level proofreading?
   - Educational feedback?
   - Style guide compliance check?

3. **Language and style requirements**:
   - Korean or English?
   - APA, Chicago, MLA, or other style guide?
   - Disciplinary conventions?

### Step 2: Apply Clarity Checklist

Load `references/clarity-checklist.md` for systematic evaluation:
- Subject-verb agreement and clarity
- Sentence structure and length
- Technical term definitions
- Logical flow and transitions
- Active/passive voice usage

### Step 3: Identify Common Issues

Refer to `references/common-issues.md` to recognize and correct:
- Verbose expressions and redundancies
- Weak verb choices
- Unclear pronoun references
- Excessive nominalization
- Hedging overuse

### Step 4: Provide Revisions or Feedback

**When revising manuscript**:
- Present Before/After comparisons
- Explain rationale for major changes
- Preserve the author's voice and argumentation structure
- Maintain disciplinary terminology and standards

**When providing educational feedback**:
- Identify patterns rather than individual cases
- Explain why specific constructions reduce clarity
- Use concrete examples from `references/before-after-examples.md`

**When writing for specific disciplines**:
- Reference `references/discipline-guides.md` for disciplinary conventions
- Check differences in citation styles, voice usage, and structural norms
- Respect disciplinary terminology and conceptual frameworks

### Step 5: Verify Improvements

After revision, confirm:

**Absolute Standard Verification (top priority)**:
- ✓ **[Absolute Standard 1]** Has scholarly quality improved (rigor, clarity, argumentation depth)?
- ✓ **[Absolute Standard 2]** Does the revision maintain consistency with other sections (terminology/argumentation/citation/style SOT)?
- ✓ **[Priority]** Is there any part where quality was sacrificed for consistency?

**Core Principle Verification**:
- ✓ Meaning and nuance preserved
- ✓ Clarity improved
- ✓ Conciseness strengthened
- ✓ Logical flow improved
- ✓ Style guide compliance (where applicable)

## Key Techniques

### Sentence Structure Optimization

**Subject-Verb-Object clarification**:
- Place subject near the beginning of the sentence
- Keep subject and verb close together
- Prevent long interpolations between subject and verb
- Use parallel structure for related ideas

**Example (Korean)**:
- ❌ "본 연구는, 도시와 농촌 지역을 아우르는 5개의 서로 다른 연구 현장에서 여러 차례의 데이터 수집 단계를 거쳐 3년의 기간 동안 수행된 종단 연구로서, 다음과 같은 관계를 조사했다."
- ✅ "본 3년간 종단 연구는 다음 관계를 조사했다. 연구는 도시와 농촌의 5개 현장에서 여러 단계로 데이터를 수집했다."

**Example (English)**:
- ❌ "The study, which was conducted over a period of three years in multiple locations across five different countries, examined the impact of..."
- ✅ "This three-year study examined the impact of... The research spanned five countries."

### Eliminating Verbosity (Paramedic Method)

1. Identify prepositional phrases (of, in, for) / Korean particles (~의, ~에서, ~에 대한)
2. Identify "to be" verbs / Korean copulas (~이다, ~있다)
3. Find the core action and convert to a strong verb
4. Move subject close to verb
5. Remove unnecessary words
6. Eliminate redundancies

### Terminology Management

**Define at first use**:
- Provide definitions when introducing technical terms
- Spell out abbreviations at first use: "Structural Equation Modeling (SEM)"
- Provide brief context for discipline-specific concepts

**Consistency**:
- Use the same term for the same concept throughout
- Avoid "elegant variation" for technical terms
- Maintain terminology consistent with cited literature

### Active/Passive Voice

**Use active voice**:
- When describing your own research actions
- When making direct claims
- When gaining clarity and saving words

**Passive voice permitted** (explicit exceptions to active voice preference):
- When the agent is unknown or unimportant
- When the action/object deserves more emphasis than the agent
- When following disciplinary convention (some science fields' methods sections)
- **Results reporting sections**: "~으로 나타났다", "~이 관찰되었다" — passive is natural per academic convention
- **Methodology descriptions**: Procedural descriptions like "participants were randomly assigned"

> **P9 intersection resolution**: When "prefer active voice" conflicts with "respect disciplinary convention," **disciplinary convention takes precedence**. This is because scholarly accuracy is a higher principle than stylistic preference.

## Language-Specific Guidance

### Korean Academic Writing

**Key principles**:
- Clearly align subject and predicate
- Do not include multiple topics in one sentence
- Remove unnecessary modifiers and conjunctions
- Define technical terms at first use

**Common issues**:
- Excessively long sentences (3+ clauses per sentence)
- Overuse of passive expressions
- Unclear subject
- Unnecessary idioms such as "~에 있어서", "~에 대하여"
- Consecutive use of "의" (3 or more prohibited)

**Person usage**: Strong preference for third person
- "본 연구는 ~을 분석했다" (O)
- "연구자는 ~을 확인했다" (O)
- "나는 ~을 분석했다" (X)

### English Academic Writing

**Key principles**:
- Prefer active voice where appropriate
- Keep sentences under 25 words when possible
- Define technical terms on first use
- Use transitions to connect ideas explicitly

**Common issues**:
- Excessive nominalization (turning verbs into nouns)
- Overuse of "there is/are" constructions
- Weak verbs (is, has, does) where stronger verbs exist
- Hedging overload (perhaps, possibly, might, etc.)

## Review Checklist

Check the following after writing:

- [ ] Does every sentence have a clear subject?
- [ ] Is sentence length within the three-tier standard (recommended 40 chars/25w, maximum 60 chars/30w)?
- [ ] Have unnecessary adjectives/adverbs been removed?
- [ ] Have passive constructions been converted to active?
- [ ] Have vague expressions been made specific?
- [ ] Has "various", "diverse", "many" been replaced with numbers?
- [ ] Have conjunctions "and" / "also" been minimized?
- [ ] Does each paragraph address a single point?
- [ ] Have technical terms been defined at first use?
- [ ] Are claims supported by evidence/citations?
- [ ] Does the writing follow the disciplinary style guide?

## Resources

### references/

Comprehensive reference materials included in this skill:

- **clarity-checklist.md**: Systematic checklist for evaluating clarity, conciseness, and scholarly rigor (bilingual Korean/English)
- **common-issues.md**: Catalog of common academic writing issues — with Before/After examples
- **before-after-examples.md**: Actual doctoral dissertation revision cases — practical examples by section
- **discipline-guides.md**: Writing conventions by field (humanities/social sciences/natural sciences), citation styles, multilingual translation guide
- **korean-quick-reference.md**: ❌/✅ conversion examples by paper section, disciplinary vocabulary, common error patterns (Korean-only quick reference)

> **Role separation among files (P4 cross-reference guide)**:
> Some topics (e.g., missing subject, passive overuse, nominalization) appear in multiple files. This is role separation, not duplication:
> - **SKILL.md**: Principles and judgment criteria (WHY)
> - **common-issues.md**: Systematic catalog of problem types + solutions (WHAT)
> - **korean-quick-reference.md**: Korean-only quick reference patterns (HOW — Korean)
> - **before-after-examples.md**: Actual paper revision cases (HOW — practical)
> - **clarity-checklist.md**: Review checklist (VERIFY)

Load into context as needed during the review and revision process.

## Notes

- **Absolute Standard 1 application**: Prioritize content over style — do not sacrifice meaning for brevity. Repeat revisions if necessary.
- **Absolute Standard 2 application**: When revising part of a manuscript, verify that the revision does not create inconsistency with terminology, argumentation, or citations in other sections.
- **Absolute Standard 3 application**: N/A in the academic writing domain. However, when modifying this skill's SKILL.md or references/ files, apply CCP (Intent Capture → Impact Scope Analysis → Change Design).
- Respect the author's voice and disciplinary conventions.
- Provide constructive, educational feedback that helps improve writing.
- When in doubt, refer to disciplinary style guides and exemplary publications.
- "Clear and concise" writing is not "simple and short" — it is efficient delivery of complex ideas.
