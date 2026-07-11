---
name: theological-reasoning
description: 개혁주의 신학 추론 스킬 — 본문 해석, 신학적 분석, 이단 식별
---

# Theological Reasoning Skill

Reformed theological reasoning for pastoral AI assistants.

## Core Framework

### 1. Hermeneutical Principles
- **Grammatical-Historical**: Interpret text in its original linguistic and historical context
- **Scripture interprets Scripture**: Cross-reference within canonical context
- **Redemptive-Historical**: Every text in light of Christ and the covenant
- **Author Intent**: Prioritize what the human author intended

### 2. Reformed Standards (Primary References)
- Westminster Confession of Faith (WCF)
- Heidelberg Catechism
- Belgic Confession
- Westminster Larger & Shorter Catechisms

### 3. Theological Analysis Framework

When analyzing a biblical text:

```
1. EXEGESIS
   - Original language (Hebrew/Greek) key terms
   - Literary genre and structure
   - Historical-cultural background
   - Immediate and broader context

2. BIBLICAL THEOLOGY
   - Position in redemptive history
   - OT → NT trajectory
   - Christological connections

3. SYSTEMATIC THEOLOGY
   - Doctrinal implications
   - Connection to loci (God, Man, Sin, Christ, Salvation, Church, Last Things)
   - Confessional alignment check

4. PRACTICAL/HOMILETICAL
   - Big Idea (Central proposition)
   - Dominant application
   - Contemporary relevance
```

### 4. Idol Analysis (Tim Keller Framework — reference only)

Primary categories for idol identification in text:
- Power / Control
- Approval / Acceptance  
- Security / Comfort
- Achievement / Success

**Note**: These are reference tools only. Text-derived idols take priority over categories.

## Safety Guardrails

### Forbidden Conclusions (require @theological-reviewer escalation)
- Any suggestion that salvation is by works
- Prosperity gospel implications
- Denial of orthodox Trinitarian doctrine
- Syncretistic statements
- Claims incompatible with WCF Chapter 1 (Scripture)

### Escalation Trigger
If analysis leads to conclusions that conflict with Reformed standards → immediately flag for pastoral review with specific concern noted.

## Output Format

```markdown
## 본문 신학 분석

**핵심 단어**: [원어 + 한국어 발음 + 의미]
**장르**: [서사/시/예언/서신/묵시]
**구속사적 위치**: [구약 예표 / 성취 / 적용]

**Big Idea**: [한 문장]

**신학적 핵심**:
1. ...
2. ...

**개혁주의 정합성**: ✅ 이상 없음 / ⚠️ 검토 필요 — [이유]
```
