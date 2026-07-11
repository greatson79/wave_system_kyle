# InvestScan Tech Stack Analysis: Aggressive vs Conservative

> **Analysts**: Two Core Technology Researchers
> **Date**: 2026-03-28
> **System Context**: InvestScan -- LOCAL AI Investment Macro Intelligence on MacBook M5 Max 64GB. Solo pastor-developer, 2-4 hrs/week, ~3,000 LOC new Python code. Integrating EnvironmentScan (Python, SBERT, spaCy, Kiwi, JSON) + GlobalNews-Crawling (Python 3.12, BERTopic, HDBSCAN, Prophet, Parquet+SQLite). No cloud APIs for core processing.

---

## BRANCH 1.1: AGGRESSIVE Tech Stack (Cutting-Edge, 1-2 Years Old)

**Philosophy**: "Adopt the best tools available today. Accept steeper learning curves for superior capabilities. Target 9/10 scores on innovation."

---

### Layer 1: NLP / Signal Processing

#### 1.1.1 Korean NLP: Kiwi (Current) vs Newer Options

**Current**: Kiwi (지능형 한국어 형태소 분석기) -- actively maintained, morphological analysis + word segmentation.

**Aggressive Recommendation: Kiwi + eKoNLPy hybrid**

| Option | Korean Financial Text | Speed | Maintenance | Verdict |
|--------|----------------------|-------|-------------|---------|
| **Kiwi v0.17+** | Strong general Korean, no financial domain | ~200K tokens/sec | Active (March 2025 update) | Keep as base |
| **eKoNLPy** | Purpose-built for Korean economic/financial text analysis | Moderate | Active (GitHub: entelecheia/eKoNLPy) | **Add for financial domain** |
| **Okt (KoNLPy)** | General Korean, legacy | Slow (~30K tokens/sec) | Stagnant | Skip |
| **Mecab-ko** | Fast but requires C extension compilation | ~500K tokens/sec | Low maintenance | Fallback only |

**Real Cases**:
1. **KOSELF (Korean Sentiment Lexicon for Finance)**: Academic research building financial-domain Korean sentiment dictionaries -- eKoNLPy integrates this type of domain knowledge directly.
2. **Won (₩on) Model**: First Korean financial domain reasoning model (arXiv 2503.17963, March 2025) -- trained on Korean financial instruction datasets, demonstrating growing ecosystem for Korean financial NLP.
3. **Kiwi in EnvironmentScan**: Already battle-tested in the current system with 25,500 LOC of production use. Proven on Naver News financial articles.

**Benchmarks**: Kiwi achieves ~95% accuracy on general Korean morphological analysis. eKoNLPy adds ~400 financial/economic terms not in general dictionaries (재무제표, 공매도, 신용잔고, etc.).

**Learning Curve**: LOW (eKoNLPy is a drop-in supplement, not a replacement). ~2-3 hours to integrate.

**Risk**: eKoNLPy's financial dictionary may not cover emerging terms (e.g., AI-related investment vocabulary). Mitigation: custom dictionary extension mechanism built into Kiwi.

**Score**: Innovation 7/10, Practicality 9/10

---

#### 1.1.2 Embeddings: paraphrase-multilingual-MiniLM (Current) vs BGE-M3, E5-Mistral, mGTE

**Current**: `paraphrase-multilingual-MiniLM-L12-v2` -- 384-dim, 118M params, ~30ms latency, supports Korean.

**Aggressive Recommendation: BGE-M3**

| Model | MTEB Score | Dimensions | Max Tokens | Korean Support | RAM (M5 Max) | Latency | Verdict |
|-------|-----------|------------|------------|---------------|-------------|---------|---------|
| **MiniLM-L12** (current) | ~56.0 | 384 | 512 | Yes (basic) | ~0.5 GB | ~15ms | Baseline |
| **BGE-M3** | **63.0** | 1024 | **8192** | **Yes (100+ languages, SOTA multilingual)** | ~2.2 GB | ~25ms | **RECOMMENDED** |
| **E5-Mistral-7B** | ~64.6 | 4096 | 32K | Yes | **~14 GB** | ~200ms | Too heavy for pipeline |
| **mGTE-base** (Alibaba) | ~61.5 | 768 | 8192 | Yes (75 languages) | ~1.1 GB | ~20ms | Strong alternative |
| **Qwen-3-Embed-0.6B** | 64.3 (MMTEB) | 1024 | 8192 | Yes | ~1.2 GB | ~30ms | Newest, less battle-tested |

**Why BGE-M3 specifically for InvestScan**:
- **Hybrid retrieval** (dense + sparse + ColBERT in one model): InvestScan needs both semantic similarity (cross-source dedup) AND keyword matching (financial terms like "반도체" must match exactly). BGE-M3 does both simultaneously.
- **8192 token context**: GlobalNews articles can exceed MiniLM's 512-token limit. Financial analysis reports from EnvScan average ~800-1200 tokens. BGE-M3 handles full articles without truncation.
- **12.5% improvement** over MiniLM on MTEB with only ~10ms additional latency.
- **MIRACL multilingual benchmark SOTA**: Specifically validated on cross-lingual retrieval tasks -- critical when matching English GlobalNews signals against Korean EnvScan signals.

**Real Cases**:
1. **Microsoft Trending on HuggingFace (2025)**: BGE-M3 highlighted alongside PubMedBERT and MiniLM as the most-used models on Azure AI.
2. **MIRACL benchmark**: BGE-M3 dense embeddings rival the 7B-parameter E5-Mistral on English while exceeding it significantly on other languages (including Korean).
3. **GlobalNews-Crawling already uses SBERT**: Migration path is `SentenceTransformer("BAAI/bge-m3")` -- a one-line model name change with identical API.

**Benchmarks**: BGE-M3 at 63.0 MTEB vs MiniLM at ~56.0 = **+12.5% quality improvement**. On MIRACL cross-lingual retrieval (which maps directly to InvestScan's English-Korean signal matching), BGE-M3 is the open-source SOTA.

**Learning Curve**: LOW (~2 hours). Same `sentence-transformers` API. Model swap only.

**Risk**: 2.2 GB RAM vs 0.5 GB for MiniLM. On 64GB M5 Max, this is negligible (3.4% of total RAM). Inference is ~10ms slower per batch -- invisible in a weekly batch pipeline.

**Score**: Innovation 9/10, Practicality 9/10

---

#### 1.1.3 Topic Modeling: BERTopic (Current) vs Alternatives

**Current**: BERTopic with HDBSCAN -- used in GlobalNews-Crawling's 8-stage NLP pipeline.

**Aggressive Recommendation: Keep BERTopic, upgrade to representation model stack**

| Option | Quality (vs BERTopic) | Korean Support | Maintenance | Verdict |
|--------|----------------------|----------------|-------------|---------|
| **BERTopic v0.16+** (current) | Baseline SOTA | Via multilingual embeddings | Very active (Maarten Grootendorst) | **Keep + upgrade** |
| **Top2Vec** | -34.2% worse on clustering benchmarks | Via embeddings | Low maintenance | Skip |
| **LDA (Gensim)** | Much worse on short text | Manual pre-processing | Stable but outdated | Skip |
| **NMF** | Decent but no contextual understanding | Via TF-IDF only | Stable | Skip |

**Why upgrade BERTopic rather than replace it**:
BERTopic v0.16+ supports a **representation model stack** -- chain multiple representation methods:
```
BERTopic(
    embedding_model="BAAI/bge-m3",          # Upgrade from MiniLM
    representation_model=[
        KeyBERTInspired(),                    # Keyword extraction
        MaximalMarginalRelevance(),           # Diversity
    ]
)
```

**Real Cases**:
1. **Springer 2024 study**: BERTopic outperforms Top2Vec by 34.2% on both Chinese and English text clustering tasks (directly relevant to InvestScan's bilingual signal corpus).
2. **Neural Processing Letters 2025**: Comprehensive 5-model comparison across multilingual corpora confirmed BERTopic's superiority for short-to-medium text (news headlines and abstracts = InvestScan's signal format).
3. **GlobalNews-Crawling**: Already uses BERTopic for 56 analysis techniques across 116 sites. Proven at scale.

**Benchmarks**: BERTopic consistently achieves highest coherence scores (c_v > 0.65) and topic separation (NPMI > 0.08) across benchmarks. Top2Vec trails by 20-40% depending on corpus.

**Learning Curve**: MINIMAL (~1 hour). Upgrading the representation model stack is additive -- existing BERTopic code remains unchanged.

**Risk**: VERY LOW. This is an upgrade within the same framework, not a migration.

**Score**: Innovation 8/10, Practicality 10/10

---

#### 1.1.4 Financial Sentiment: FinBERT-KR / KcELECTRA Options

**Aggressive Recommendation: KcELECTRA-base-v2022 fine-tuned with SetFit**

| Model | Korean Financial Accuracy | Size | Training Data | Verdict |
|-------|--------------------------|------|---------------|---------|
| **FinBERT (ProsusAI)** | Good English, no Korean | 110M | Financial Phrasebank | English only -- skip |
| **KcELECTRA-base-v2022** | Strong Korean sentiment (~90% on NSMC) | 110M | 17.3 GB Korean news comments (180M+ sentences) | **Base model** |
| **KcELECTRA + SetFit** | **Korean financial sentiment with 8-32 labeled examples** | 110M | Few-shot fine-tuning | **RECOMMENDED** |
| **Won (₩on)** | Korean financial reasoning | Large | Financial competition data | Experimental, too new |

**Why SetFit + KcELECTRA**:
- **SetFit achieves GPT-3-level classification with only 8 examples per class** -- the developer can manually label 24-48 financial news sentences (bullish/bearish/neutral) in ~30 minutes, and SetFit produces a production-quality classifier.
- **Training takes 30 seconds on consumer hardware** (demonstrated on NVIDIA V100; M5 Max is faster for small models via MPS).
- **KcELECTRA is pre-trained on 180M+ Korean news comments** -- the base model already understands Korean news discourse patterns, financial terminology in news context, and sentiment expressions.
- **30x more efficient than fine-tuning a 3B+ model** (SetFit paper benchmark).

**Real Cases**:
1. **SetFit on RAFT benchmark**: 110M parameter SetFit outperforms GPT-3 (175B) and matches average human performance on few-shot classification.
2. **KcELECTRA NSMC benchmark**: 90%+ accuracy on Korean sentiment classification (Naver Sentiment Movie Corpus), demonstrating strong Korean sentiment understanding transferable to financial domain.
3. **KOSELF project**: Korean Sentiment Lexicon for Finance provides the labeled seed data needed for SetFit fine-tuning -- 24-48 examples can be sourced from KOSELF's validated financial sentiment annotations.

**Benchmarks**: SetFit with 32 samples per class matches RoBERTa-Large fine-tuned on 3,000+ samples (Customer Reviews benchmark). KcELECTRA achieves F1 ~0.90 on Korean sentiment tasks.

**Learning Curve**: MEDIUM (~8-10 hours total). 2 hours to understand SetFit API, 1 hour to label 48 examples, 5-7 hours to iterate on financial domain adaptation.

**Risk**: MEDIUM. The developer must create labeled data (though only 24-48 examples). If financial sentiment is poorly defined for macro signals (which are often neutral/analytical rather than sentiment-bearing), the model may underperform. Mitigation: start with rule-based sentiment, add SetFit when rule-based accuracy drops below 70%.

**Score**: Innovation 9/10, Practicality 7/10

---

### Layer 2: Signal Classification & Evolution

#### 1.1.5 Classification Approach: ML vs Rule-Based vs LLM

**Aggressive Recommendation: SetFit few-shot classification (ML-based)**

| Approach | Accuracy (est.) | Setup Time | Maintenance | Adaptability | Verdict |
|----------|-----------------|-----------|-------------|-------------|---------|
| **Rule-based** (keyword matching) | 70-80% | 4-6 hours | Manual rule updates | Low | Conservative baseline |
| **SetFit few-shot** | **85-92%** | 8-10 hours | Re-label 10 examples/quarter | High | **RECOMMENDED** |
| **Zero-shot LLM** (Ollama + Qwen2.5) | 75-85% | 2-3 hours | Prompt tuning | Medium | Fallback option |
| **Full fine-tuned BERT** | 88-95% | 40+ hours | Requires 1000+ labels | Very high | Over-engineered for 3K LOC |

**Why SetFit for InvestScan's classification tasks**:

InvestScan needs to classify signals along three taxonomies:
1. **STEEPs** (S/T/E/E_env/P/s) -- 6 classes
2. **Signal Layer** (L1_fad through L5_singularity) -- 5 classes
3. **Investment Direction** (bullish/bearish/neutral) -- 3 classes

SetFit with 8-32 labeled examples per class means:
- STEEPs: 48-192 labeled examples (1-2 hours of manual work)
- Signal Layer: 40-160 labeled examples (1-2 hours)
- Direction: 24-96 labeled examples (30-60 minutes)

**Total labeling effort**: 3-5 hours for all three classifiers, achieving 85-92% accuracy.

**Real Cases**:
1. **Hugging Face SetFit blog**: Demonstrated competitive performance with GPT-3 using only 8 examples per class on CR sentiment dataset.
2. **RAFT benchmark (2023-2025)**: SetFit consistently outperforms zero-shot approaches and matches few-shot GPT-3 on specialized classification tasks.
3. **Financial text classification (FinNLP 2025)**: FinBERT + domain adaptation achieves macro F1 = 0.707, while SetFit-style approaches on similar tasks achieve comparable results with 100x less labeled data.

**Benchmarks**: SetFit with 32 samples achieves equivalent performance to models trained on full datasets (3000+ examples). Training time: 30 seconds on GPU. Inference: ~5ms per classification.

**Learning Curve**: MEDIUM (8-10 hours including labeling time).

**Risk**: If signal text is too short or ambiguous (e.g., "AI chip exports increase"), classification may be unreliable. Mitigation: use confidence thresholds and fall back to rule-based for low-confidence predictions (hybrid approach).

**Score**: Innovation 9/10, Practicality 8/10

---

#### 1.1.6 Time-Series Storage: InfluxDB vs TimescaleDB vs Parquet

**Aggressive Recommendation: DuckDB + Parquet (append-only)**

| Option | Query Speed (analytical) | Setup Complexity | Parquet Integration | Solo Dev Maintenance | Verdict |
|--------|--------------------------|-----------------|--------------------|--------------------|---------|
| **InfluxDB 3.0** | Fast (ingestion-optimized) | Medium (server process) | Native (uses Parquet internally) | Needs daemon management | Over-engineered |
| **TimescaleDB** | 3.5-71x faster than InfluxDB on complex queries | High (PostgreSQL extension) | Via COPY | Requires PostgreSQL | Over-engineered |
| **SQLite + Parquet** (current approach) | Moderate | Low | Via PyArrow read | Minimal | Current baseline |
| **DuckDB + Parquet** | **10-100x faster than SQLite on analytics** | **Low (embedded, zero config)** | **Native (queries Parquet in-place)** | **Zero daemon, file-only** | **RECOMMENDED** |

**Why DuckDB for InvestScan's signal evolution tracking**:
- **Queries Parquet files directly** without import: `SELECT * FROM 'signals/2026-03-*.parquet' WHERE steeps = 'T'` -- GlobalNews already outputs Parquet, so DuckDB reads them with zero ETL.
- **10-100x faster aggregation** than SQLite: Signal evolution requires GROUP BY week, category, source queries across months of accumulated data. SQLite is row-oriented; DuckDB is columnar.
- **Embedded, serverless**: Like SQLite, DuckDB is a single file or in-memory -- no daemon, no configuration, no port management. `import duckdb; conn = duckdb.connect()`.
- **50%+ YoY developer growth (2025)**: The ecosystem is maturing rapidly with strong community support.
- **1 TB Parquet in 30 seconds** on a standard laptop: InvestScan's signal data will be <100 MB even after years -- effectively instant queries.

**Real Cases**:
1. **DuckDB + Parquet as "SQLite of Analytics" (2025-2026)**: Multiple industry analyses position DuckDB as the standard for local analytical workloads, specifically replacing SQLite for analytical queries.
2. **GlobalNews-Crawling already uses Parquet**: Zero migration cost for existing data format. DuckDB reads the same files.
3. **DataCamp 2026 comparison**: "For analytics-heavy workloads, DuckDB's design makes it 10-100x faster" -- InvestScan's signal evolution queries (trend detection, weekly deltas, cross-source aggregation) are textbook analytical workloads.

**Benchmarks**: DuckDB aggregation queries run 10-100x faster than SQLite on the same data. TPC-H benchmarks show DuckDB matching or exceeding dedicated OLAP databases. Memory-efficient: processes data larger than RAM via streaming.

**Learning Curve**: LOW (~3-4 hours). SQL is identical to SQLite. The only new concept is `read_parquet()` function for direct file queries.

**Risk**: LOW. DuckDB is embedded and file-based, same deployment model as SQLite. If it fails, fall back to SQLite + PyArrow (the current approach) with zero data migration since both read the same Parquet files.

**Score**: Innovation 9/10, Practicality 9/10

---

#### 1.1.7 Graph DB for Cross-Domain Impact: Neo4j vs NetworkX

**Aggressive Recommendation: NetworkX (in-memory graph library)**

| Option | Performance (50-100K nodes) | Setup | Python Integration | Solo Dev Maintenance | Verdict |
|--------|---------------------------|-------|-------------------|--------------------|---------|
| **Neo4j Desktop** | Fast (Java, parallel) | Medium (JVM, Cypher lang) | Via driver | Requires daemon | Over-engineered |
| **Neo4j Community** | Same | High (Docker/install) | Via driver | Server management | Over-engineered |
| **NetworkX** | Adequate for <100K nodes | **Zero (pip install)** | **Native Python** | **Zero** | **RECOMMENDED** |
| **igraph** | Faster than NetworkX (C backend) | Low (pip install) | Good | Low | Fallback if NetworkX slow |

**Why NetworkX, not Neo4j, for InvestScan**:
- InvestScan's cross-domain impact graph will have ~50-200 signal nodes per week, ~500-2000 edges -- this is a **tiny graph**. NetworkX handles millions of nodes; this workload is trivial.
- **Zero infrastructure**: `import networkx as nx; G = nx.Graph()`. No server, no JVM, no Cypher query language to learn.
- **Rich algorithm library**: PageRank, community detection, shortest path, centrality -- all available as one-line function calls for discovering hidden signal relationships.
- **Serialization**: `nx.write_graphml(G, "signals.graphml")` for persistence between runs. No database needed.

**Real Cases**:
1. **NetworkX 9.1K GitHub stars**: More popular than Neo4j's Python driver, indicating stronger community support for Python-native graph analysis.
2. **Academic financial network analysis**: Most published research on financial signal correlation networks uses NetworkX for analysis, not graph databases (graph databases are for production services with concurrent users, not batch analysis).
3. **InvestScan's use case**: Weekly batch analysis of ~100-200 signals with cross-domain edges. This is a textbook NetworkX use case -- build graph in memory, run algorithms, serialize results, discard.

**Benchmarks**: For graphs under 100K nodes, NetworkX completes centrality calculations in <1 second. Neo4j's advantage appears only at 50K-100K+ nodes with complex traversals.

**Learning Curve**: LOW (~3-4 hours). Pure Python API, extensive documentation, thousands of tutorials.

**Risk**: VERY LOW. If graph analysis proves too slow (unlikely at <1000 nodes), igraph is a drop-in replacement with C backend providing 10-100x speedup.

**Score**: Innovation 7/10, Practicality 10/10

---

### Layer 3: Report Generation

#### 1.1.8 Local LLM (Ollama) vs Template-Based (Jinja2)

**Aggressive Recommendation: Jinja2 templates + Ollama/Qwen2.5-32B for narrative enhancement**

| Approach | Output Quality (Korean) | Latency | Determinism | Maintenance | Verdict |
|----------|------------------------|---------|-------------|-------------|---------|
| **Jinja2 templates only** | Consistent, structured, no hallucination | <1 sec | 100% deterministic | Template updates | Conservative baseline |
| **Ollama + Qwen2.5-32B only** | Fluent Korean, may hallucinate | 1-2 min | Non-deterministic | Model updates, prompt tuning | Risky for financial |
| **Jinja2 + Ollama hybrid** | **Structured + fluent narrative sections** | ~2-3 min | Deterministic structure, LLM-enhanced prose | Both | **RECOMMENDED** |

**Why the hybrid approach**:

InvestScan reports have two distinct sections:
1. **Data tables, heatmaps, evidence chains** -- MUST be deterministic. Jinja2 renders these from structured data with zero hallucination risk.
2. **Executive summary, narrative interpretation** -- BENEFITS from natural language generation. "This week's technology sector signals converge on semiconductor supply chain disruption..." is better written by an LLM than a template.

**The hybrid pattern**:
```python
# Step 1: Jinja2 renders ALL data-driven sections (tables, charts, evidence)
structured_report = jinja2_env.get_template("weekly.md.j2").render(data=synthesis)

# Step 2: Ollama generates ONLY the narrative summary (200-500 words)
narrative = ollama.generate(
    model="qwen2.5:32b",
    prompt=f"Based on this data summary, write a 300-word Korean investment briefing:\n{data_summary}",
    options={"temperature": 0.3}  # Low temp for factual consistency
)

# Step 3: Insert narrative into template slot
final_report = structured_report.replace("{{NARRATIVE}}", narrative)
```

**Qwen2.5-32B Korean quality on M5 Max 64GB**:
- RAM: ~30-34 GB (fits comfortably in 64 GB with room for the pipeline)
- Speed: 1-2 minutes per response
- Korean quality: Supports 29+ languages including Korean; significant advances in long-text generation (8K+ tokens) and structured data understanding
- **Alternative**: Qwen2.5-14B uses ~16 GB RAM at 2x speed with slightly lower quality

**Real Cases**:
1. **Simon Willison (2025)**: Ran Qwen2.5-Coder-32B on MacBook Pro M3 with 36GB RAM -- confirmed practical local execution. M5 Max 64GB has nearly 2x headroom.
2. **Qwen2.5 multilingual benchmarks**: Matches GPT-4o on coding tasks; Korean language quality rated among top open-source models.
3. **Hybrid template+LLM pattern**: Used in enterprise report generation (automatic report generators combining structured data with LLM narrative) as documented in AI security research.

**Benchmarks**: Qwen2.5-32B generates ~500 Korean tokens in 60-90 seconds on M-series Macs. Quality is subjective but rated "near-GPT-4" on Korean by community evaluations. Jinja2 renders complete reports in <1 second.

**Learning Curve**: MEDIUM-HIGH (~12-15 hours). Jinja2 templates: 3-4 hours. Ollama setup + Qwen2.5: 2-3 hours. Prompt engineering for consistent Korean financial narratives: 5-8 hours of iteration.

**Risk**: MEDIUM. LLM-generated financial narrative could contain subtle inaccuracies or inappropriate confidence levels. Mitigation: (a) low temperature (0.3), (b) narrative section clearly marked as AI-generated, (c) data tables are always Jinja2-rendered with zero LLM involvement.

**Score**: Innovation 9/10, Practicality 7/10

---

### Layer 4: Orchestration

#### 1.1.9 workflow.md vs Python Orchestrator vs Snakemake

**Aggressive Recommendation: Snakemake**

| Option | DAG Support | Resumability | Error Handling | Learning Curve | Verdict |
|--------|------------|-------------|----------------|---------------|---------|
| **workflow.md (Claude Code)** | Manual | None | Manual | Zero | Current approach |
| **Python subprocess + cron** | Manual | Manual checkpoint | try/except | Low | Conservative baseline |
| **Snakemake** | **Automatic DAG** | **Built-in (skip completed steps)** | **Per-rule retry** | Medium | **RECOMMENDED** |
| **Prefect / Airflow** | Full DAG | Built-in | Enterprise-grade | High | Over-engineered |
| **Make (GNU Make)** | File-based DAG | Built-in | Basic | Low | Ugly syntax for data pipelines |

**Why Snakemake for InvestScan**:
- **Pythonic syntax**: Rules are essentially Python functions with declared inputs/outputs. The developer already writes Python.
- **Automatic skip of completed steps**: If EnvScan completed but GlobalNews failed, re-running skips EnvScan. For a weekly pipeline that takes ~4 hours, this saves 2+ hours on retry.
- **Built-in Conda environment support**: Each rule can declare its own conda env, preventing dependency conflicts between the SBERT pipeline and the report generator.
- **Scales from laptop to cluster**: If InvestScan ever needs to process more data, Snakemake scales without rewriting the pipeline.

**InvestScan Snakefile example**:
```python
rule all:
    input: "output/{date}/invest-report-{date}-ko.md"

rule run_envscan:
    output: "output/{date}/envscan_signals.json"
    shell: "cd ../EnvironmentScan && python main.py --date {wildcards.date}"

rule run_globalnews:
    output: "output/{date}/globalnews_signals.parquet"
    shell: "cd ../GlobalNews-Crawling && python main.py --mode full --date {wildcards.date}"

rule normalize:
    input:
        env="output/{date}/envscan_signals.json",
        gnews="output/{date}/globalnews_signals.parquet"
    output: "output/{date}/unified_signals.json"
    script: "invest_pipeline/normalize_signals.py"

rule synthesize:
    input: "output/{date}/unified_signals.json"
    output: "output/{date}/investment_synthesis.json"
    script: "invest_pipeline/synthesize_investment.py"

rule report:
    input: "output/{date}/investment_synthesis.json"
    output: "output/{date}/invest-report-{date}-ko.md"
    script: "invest_pipeline/generate_report.py"
```

**Real Cases**:
1. **Snakemake Workflow Catalog**: Thousands of shared scientific pipelines demonstrate Snakemake's dominance in Python-based data processing orchestration.
2. **Bioinformatics 2025 survey**: Snakemake recommended as the best balance of simplicity and power for solo developers and small teams.
3. **Galaxy Training Network**: Positions Snakemake as the natural evolution of Makefiles for data science workflows.

**Benchmarks**: Snakemake adds ~2-3 seconds overhead per rule execution (negligible in a 4-hour pipeline). DAG resolution for 5-10 rules is instantaneous.

**Learning Curve**: MEDIUM (~6-8 hours). The Snakefile syntax is intuitive for Python developers. Main learning: understanding input/output declarations and wildcard patterns.

**Risk**: MEDIUM. Adds a dependency and a new concept (DAG-based execution) that the developer must maintain. If Snakemake introduces bugs or version conflicts, debugging requires understanding both Snakemake and the pipeline. Mitigation: the pipeline scripts remain standalone Python -- Snakemake is only the orchestration layer, easily replaced with a shell script if needed.

**Score**: Innovation 8/10, Practicality 7/10

---

### Branch 1.1 Summary: Aggressive Stack

| Layer | Recommendation | Innovation | Practicality | Risk |
|-------|---------------|------------|-------------|------|
| Korean NLP | Kiwi + eKoNLPy | 7/10 | 9/10 | LOW |
| Embeddings | **BGE-M3** | 9/10 | 9/10 | LOW |
| Topic Modeling | BERTopic + representation stack upgrade | 8/10 | 10/10 | VERY LOW |
| Financial Sentiment | KcELECTRA + SetFit | 9/10 | 7/10 | MEDIUM |
| Classification | SetFit few-shot | 9/10 | 8/10 | MEDIUM |
| Time-Series Storage | **DuckDB + Parquet** | 9/10 | 9/10 | LOW |
| Graph Analysis | NetworkX | 7/10 | 10/10 | VERY LOW |
| Report Generation | Jinja2 + Ollama/Qwen2.5 hybrid | 9/10 | 7/10 | MEDIUM |
| Orchestration | Snakemake | 8/10 | 7/10 | MEDIUM |

**Aggregate**: Innovation 8.3/10, Practicality 8.4/10

---
---

## BRANCH 1.2: CONSERVATIVE Tech Stack (5+ Years Proven)

**Philosophy**: "Use only what has been battle-tested for 5+ years. Accept lower capability ceilings for zero surprises. Target 10/10 stability scores."

---

### Layer 1: NLP / Signal Processing

#### 1.2.1 Korean NLP: Stick with Kiwi

**Conservative Recommendation: Kiwi only (no additions)**

**Stability Record**:
- Kiwi has been actively maintained since 2018 (8+ years)
- Used in EnvironmentScan's 25,500 LOC production system across 4 workflows
- Processes Naver News articles daily without failures
- Python bindings are stable across Python 3.8-3.12

**Enterprise Examples**:
1. **EnvironmentScan production**: 37 agents use Kiwi for Korean text processing. Zero Kiwi-related bugs in the production history.
2. **Korean NLP academic research**: Kiwi is the default tokenizer in dozens of published papers on Korean NLP since 2020.
3. **Naver News processing**: Handles the exact text format InvestScan will encounter (Korean financial news articles).

**Why NOT add eKoNLPy**: Adding a second NLP library creates dependency conflicts, increases the surface area for bugs, and requires understanding two APIs. Kiwi handles 95%+ of Korean text correctly. The 5% improvement from financial terminology is not worth the complexity for a solo developer maintaining 3,000 LOC.

**Score**: Stability 10/10, Capability 7/10

---

#### 1.2.2 Embeddings: Stick with paraphrase-multilingual-MiniLM

**Conservative Recommendation: Keep MiniLM-L12-v2**

**Stability Record**:
- Released 2021, stable for 5+ years
- 100M+ downloads on HuggingFace
- Used in GlobalNews-Crawling's production pipeline
- SentenceTransformers library provides rock-solid API

**Enterprise Examples**:
1. **GlobalNews-Crawling production**: Uses MiniLM for cross-source signal similarity in the 8-stage NLP pipeline. Proven on 116 news sites.
2. **Microsoft Azure AI**: MiniLM is among the most-deployed embedding models on Azure, used by thousands of enterprise applications.
3. **HuggingFace Trending (2025)**: Still listed as a "trending" model alongside newer options, indicating continued widespread adoption.

**Why NOT upgrade to BGE-M3**: The 12.5% MTEB improvement is real but may not translate to meaningful quality differences in InvestScan's specific use case (cross-source dedup and signal similarity). MiniLM's 512-token limit is adequate if signals are summarized before embedding (which both source systems already do). Upgrading introduces a new model checkpoint (2.2 GB vs 0.5 GB), potentially different similarity score distributions requiring threshold recalibration, and a model that has been in production for only ~2 years vs MiniLM's 5+.

**Counter-argument acknowledged**: The 8192-token context window of BGE-M3 is a genuine capability gap. If full-article embedding (not just summary embedding) proves necessary, this conservative choice should be revisited.

**Score**: Stability 10/10, Capability 7/10

---

#### 1.2.3 Topic Modeling: Stick with BERTopic + HDBSCAN

**Conservative Recommendation: BERTopic with current configuration**

**Stability Record**:
- BERTopic released 2022, now 4+ years of production use
- HDBSCAN: original paper 2013, Python library stable since 2017 (9+ years)
- Combined: the most-cited neural topic modeling approach in academic literature

**Enterprise Examples**:
1. **GlobalNews-Crawling**: BERTopic drives 56 analysis techniques across the pipeline. No BERTopic-related production failures documented.
2. **Frontiers in Sociology (2022)**: BERTopic used to analyze 200K+ Twitter posts, demonstrating scalability and reliability.
3. **Springer 2024 benchmark**: Confirmed BERTopic as SOTA across multiple corpora -- no reason to change.

**Why NOT upgrade the representation model stack**: The current BERTopic configuration works. Adding KeyBERTInspired or MaximalMarginalRelevance representation models changes topic quality in ways that require re-evaluation of all downstream processing that depends on topic labels. For a weekly pipeline where the developer reads every report, incremental quality improvements are less valuable than consistency.

**Score**: Stability 10/10, Capability 8/10

---

#### 1.2.4 Financial Sentiment: Rule-Based Keyword Matching

**Conservative Recommendation: Keyword dictionary + regex rules**

| Approach | Accuracy | Implementation Time | Maintenance | Stability |
|----------|----------|-------------------|-------------|-----------|
| **Keyword dictionary** | 65-75% | 3-4 hours | Manual dictionary updates | **Decades-proven** |
| **KcELECTRA + SetFit** | 85-92% | 8-10 hours | Model version management | 2-3 years proven |

**Implementation**:
```python
BULLISH_KEYWORDS = {"상승", "호재", "성장", "확대", "수혜", "반등", "강세", ...}
BEARISH_KEYWORDS = {"하락", "악재", "위축", "감소", "리스크", "약세", ...}

def classify_sentiment(text: str) -> str:
    bull_count = sum(1 for kw in BULLISH_KEYWORDS if kw in text)
    bear_count = sum(1 for kw in BEARISH_KEYWORDS if kw in text)
    if bull_count > bear_count: return "bullish"
    if bear_count > bull_count: return "bearish"
    return "neutral"
```

**Enterprise Examples**:
1. **KOSELF (Korean Sentiment Lexicon for Finance)**: Academic-grade financial sentiment dictionary for Korean -- provides a validated starting point for keyword lists.
2. **Traditional quantitative finance**: Rule-based sentiment was the industry standard for 20+ years before ML approaches. Bloomberg's early news sentiment was rule-based.
3. **EnvironmentScan's pSST scoring**: Uses rule-based scoring that has proven adequate for macro-level signal assessment.

**Why rule-based for solo developer maintainability**: When a keyword classifier produces wrong output, the developer opens `keywords.yaml`, adds/removes a word, and the fix is immediate and permanent. When a ML model produces wrong output, the developer must: (a) diagnose whether it is a training data issue, model issue, or input distribution shift, (b) relabel data, (c) retrain, (d) validate. For a 2-4 hrs/week developer, rule-based fixes take 5 minutes; ML fixes take 2-5 hours.

**Limitation acknowledged**: Rule-based cannot handle negation ("반도체 상승세가 꺾였다" = bearish despite containing "상승"), sarcasm, or complex multi-clause sentences. Accuracy ceiling is ~75%.

**Score**: Stability 10/10, Capability 6/10

---

### Layer 2: Signal Classification & Evolution

#### 1.2.5 Classification: Rule-Based (Keyword + Regex)

**Conservative Recommendation: Hierarchical keyword rules**

**Implementation pattern** (proven in EnvironmentScan's STEEPs classifier):
```python
STEEPS_RULES = {
    "T": {"keywords": ["AI", "반도체", "양자", "로봇", "5G", "배터리", ...], "weight": 1.0},
    "E": {"keywords": ["GDP", "금리", "환율", "인플레이션", "고용", ...], "weight": 1.0},
    "S": {"keywords": ["인구", "고령화", "교육", "문화", "이민", ...], "weight": 1.0},
    # ...
}

def classify_steeps(text: str) -> str:
    scores = {}
    for category, rule in STEEPS_RULES.items():
        scores[category] = sum(w for kw in rule["keywords"] if kw in text for w in [rule["weight"]])
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "unknown"
```

**Stability Record**: Rule-based classification has been used in information retrieval for 30+ years (TF-IDF-based classifiers date to the 1970s). The pattern is universally understood by any developer.

**Enterprise Examples**:
1. **EnvironmentScan's native STEEPs classification**: Already implemented and tested with 37 agents across 4 workflows. Accuracy at ~70-80% confirmed through manual review.
2. **EnvScan's FSSF 8-type signal classification**: Another rule-based classifier operating in production.
3. **Bloomberg Terminal sector classification (legacy)**: Early versions used keyword-based sector assignment before ML migration.

**Why rule-based is better for solo dev maintainability**: The entire classification logic fits in a single YAML file + 50-line Python function. Any developer can read, modify, and debug it. No model checkpoints, no training infrastructure, no GPU dependency.

**Score**: Stability 10/10, Capability 7/10

---

#### 1.2.6 Storage: SQLite + Parquet (Current Stack)

**Conservative Recommendation: Keep SQLite (FTS5) + Parquet (ZSTD)**

**Stability Record**:
- **SQLite**: Released 2000. 25+ years of production stability. Most deployed database in the world (billions of instances). Used in every iPhone, Android, and macOS device.
- **Parquet**: Apache project since 2013. 12+ years of production use. The columnar storage standard.
- **PyArrow**: Apache Arrow's Python binding, stable since 2017 (8+ years).

**Enterprise Examples**:
1. **GlobalNews-Crawling**: Uses Parquet (ZSTD) for signal storage + SQLite (FTS5) for full-text search. Handles 116 sites without issues.
2. **Every mobile application**: SQLite powers data storage in iOS and Android -- demonstrated reliability at planetary scale.
3. **Hadoop/Spark ecosystem**: Parquet is the default storage format for petabyte-scale analytical workloads.

**Why SQLite + Parquet is sufficient for evolution tracking**:
- **Weekly signal volume**: ~100-300 signals/week. After 2 years: ~10,000-30,000 signals. SQLite handles millions of rows effortlessly.
- **Query complexity**: "Show me all Technology signals from the last 4 weeks" = simple SQL. No columnar analytics engine needed.
- **FTS5 for text search**: `SELECT * FROM signals WHERE signals MATCH 'semiconductor'` -- full-text search built into SQLite, no additional engine needed.
- **Parquet for archival**: Compressed storage (~10:1 ratio), schema-preserving, readable by any data tool.

**Why NOT DuckDB**: DuckDB's 10-100x query speed advantage is meaningless when SQLite returns results in <100ms for InvestScan's data volume. The incremental learning curve and additional dependency provide zero practical benefit until data exceeds 1M+ rows (estimated: year 5+ of operation).

**Score**: Stability 10/10, Capability 8/10

---

#### 1.2.7 Graph Analysis: Skip Entirely (Relational Joins)

**Conservative Recommendation: No graph database or library. Use SQL JOINs.**

**Rationale**: Cross-domain signal relationships can be expressed as SQL queries:
```sql
-- Find signals that share keywords across domains
SELECT a.title, b.title, a.steeps_category, b.steeps_category
FROM signals a, signals b
WHERE a.signal_id != b.signal_id
  AND a.steeps_category != b.steeps_category
  AND a.detected_week = b.detected_week
  AND similarity(a.embedding, b.embedding) > 0.7
```

**Why skip graph entirely**: Adding NetworkX (or any graph library) introduces a new paradigm (graph thinking) into a codebase that is otherwise purely tabular (DataFrames, SQL, JSON). For a solo developer maintaining 3,000 LOC, conceptual consistency matters more than capability. Cross-domain impact analysis via SQL JOINs covers 90% of the use cases.

**When to reconsider**: If the developer finds themselves writing 4+ table JOINs to answer a single question about signal relationships, graph modeling becomes worth the cognitive overhead.

**Score**: Stability 10/10, Capability 5/10

---

### Layer 3: Report Generation

#### 1.2.8 Report Generation: Jinja2 Templates (Zero ML Dependency)

**Conservative Recommendation: Jinja2 only**

**Stability Record**:
- Jinja2: Released 2008. 18+ years of production stability.
- Used by Flask, Django (as DTL), Ansible, Kubernetes (Helm), and SaltStack -- some of the most critical infrastructure tools in computing.
- Version 3.1.x: Stable, no breaking changes in years.

**Implementation**:
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("weekly_report.md.j2")

report = template.render(
    date=report_date,
    signals=unified_signals,
    sector_heatmap=sector_scores,
    steeps_summary=steeps_summary,
    evidence_chains=evidence_chains,
    risk_matrix=risk_matrix,
)
```

**Enterprise Examples**:
1. **Ansible**: The world's most-used infrastructure automation tool runs entirely on Jinja2 templates. Manages millions of servers.
2. **Kubernetes Helm**: Every Kubernetes deployment uses Jinja2-style templating (Go templates, but same paradigm). Manages containerized workloads at Google/AWS/Azure scale.
3. **EnvironmentScan's existing reports**: Markdown reports generated through template-based approaches. Proven format for the developer's reading workflow.

**Why NOT add Ollama/LLM**:
- **Determinism**: Financial reports MUST be reproducible. "Run the pipeline twice, get the same report" is a non-negotiable requirement for investment decision support. LLMs cannot guarantee this.
- **No hallucination risk**: A Jinja2 template renders exactly what the data says. An LLM might embellish, soften alarming signals, or invent correlations.
- **Zero RAM overhead**: Jinja2 uses ~10 MB. Qwen2.5-32B uses ~30 GB. This is 3000x more RAM for marginal narrative improvement.
- **Maintenance**: Template updates are 5-minute text edits. LLM prompt engineering is multi-hour experimentation.

**Limitation acknowledged**: Template-generated reports lack natural narrative flow. "Signal X detected in Technology sector with confidence 0.85, direction: bullish" reads like data, not insight. The developer must add interpretive commentary manually.

**Score**: Stability 10/10, Capability 6/10

---

### Layer 4: Orchestration

#### 1.2.9 Orchestration: Python subprocess + cron/launchd

**Conservative Recommendation: Plain Python script + launchd (macOS native scheduler)**

**Stability Record**:
- **subprocess module**: Part of Python standard library since Python 2.4 (2004). 22+ years.
- **cron**: UNIX utility since 1975. 51+ years of reliability.
- **launchd**: macOS native scheduler since 2005. 21+ years, Apple-maintained.

**Implementation**:
```python
#!/usr/bin/env python3
"""investscan_run.py -- Daily pipeline orchestrator"""
import subprocess, sys, logging
from pathlib import Path
from datetime import date

def run_step(name: str, cmd: list[str], cwd: Path) -> bool:
    logging.info(f"Starting: {name}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=7200)
    if result.returncode != 0:
        logging.error(f"FAILED: {name}\n{result.stderr}")
        return False
    logging.info(f"Completed: {name}")
    return True

def main():
    today = date.today().isoformat()
    steps = [
        ("EnvScan", ["python", "main.py", "--date", today], ENVSCAN_ROOT),
        ("GlobalNews", ["python", "main.py", "--mode", "full", "--date", today], GNEWS_ROOT),
        ("Normalize", ["python", "-m", "invest_pipeline.normalize_signals", "--date", today], PROJECT_ROOT),
        ("Synthesize", ["python", "-m", "invest_pipeline.synthesize_investment", "--date", today], PROJECT_ROOT),
        ("Report", ["python", "-m", "invest_pipeline.generate_report", "--date", today], PROJECT_ROOT),
    ]
    for name, cmd, cwd in steps:
        if not run_step(name, cmd, cwd):
            logging.error(f"Pipeline stopped at {name}")
            sys.exit(1)
    logging.info("Pipeline completed successfully")

if __name__ == "__main__":
    main()
```

**Enterprise Examples**:
1. **Every UNIX system in existence**: cron + shell scripts have orchestrated batch processing since the 1970s. Banks, hospitals, governments, and military systems run on this pattern.
2. **macOS launchd**: Powers every scheduled task on macOS, including Apple's own system maintenance. The developer's M5 Max already runs dozens of launchd jobs.
3. **EnvironmentScan**: Already orchestrated by Claude Code slash commands, which are ultimately Python subprocess calls.

**Why NOT Snakemake**: Snakemake solves three problems InvestScan does not have:
1. **Complex DAGs with branching**: InvestScan is a linear 5-step pipeline. No branching, no parallelism needed.
2. **Large-scale cluster execution**: InvestScan runs on one MacBook.
3. **Dozens of rules with complex dependencies**: InvestScan has 5 sequential steps.

Adding Snakemake to a 5-step linear pipeline is like adding Kubernetes to deploy one container. The overhead (new syntax, new dependency, new debugging surface) exceeds the benefit.

**When to reconsider**: If the pipeline grows to 10+ steps with conditional branches (e.g., "skip KRX data if market is closed"), Snakemake's DAG management becomes valuable.

**Score**: Stability 10/10, Capability 6/10

---

### Branch 1.2 Summary: Conservative Stack

| Layer | Recommendation | Stability | Capability | Risk |
|-------|---------------|-----------|-----------|------|
| Korean NLP | Kiwi only | 10/10 | 7/10 | ZERO |
| Embeddings | MiniLM-L12-v2 (keep current) | 10/10 | 7/10 | ZERO |
| Topic Modeling | BERTopic + HDBSCAN (keep current) | 10/10 | 8/10 | ZERO |
| Financial Sentiment | Keyword dictionary + regex | 10/10 | 6/10 | ZERO |
| Classification | Hierarchical keyword rules | 10/10 | 7/10 | ZERO |
| Storage | SQLite + Parquet (keep current) | 10/10 | 8/10 | ZERO |
| Graph Analysis | Skip (SQL JOINs) | 10/10 | 5/10 | ZERO |
| Report Generation | Jinja2 templates only | 10/10 | 6/10 | ZERO |
| Orchestration | Python subprocess + launchd | 10/10 | 6/10 | ZERO |

**Aggregate**: Stability 10/10, Capability 6.7/10

---
---

## FINAL: Head-to-Head Comparison for InvestScan's Specific Situation

### Context Recap

| Factor | Value | Implication |
|--------|-------|------------|
| Developer | Solo pastor, 2-4 hrs/week | Every hour of learning curve costs 2-4 weeks of calendar time |
| New code | ~3,000 LOC | Small enough that any tech choice can be replaced entirely |
| Hardware | M5 Max 64GB | No hardware constraints -- aggressive options are all feasible |
| Existing stack | SBERT + BERTopic + Kiwi + Parquet + SQLite | Migration cost is real but not prohibitive |
| Pipeline frequency | Weekly batch | Not real-time -- latency differences are irrelevant |
| Data volume | ~100-300 signals/week, <100 MB/year | Tiny -- database performance differences are irrelevant |
| Quality requirement | Investment decisions ride on output | Correctness matters more than capability |

---

### Layer-by-Layer Verdict

| Layer | Aggressive | Conservative | **InvestScan Verdict** | **Rationale** |
|-------|-----------|-------------|----------------------|---------------|
| **Korean NLP** | Kiwi + eKoNLPy | Kiwi only | **Conservative** | eKoNLPy adds marginal value for ~400 financial terms. Kiwi handles 95%+ of text correctly. Add eKoNLPy only when specific financial terms cause classification errors. |
| **Embeddings** | BGE-M3 | MiniLM-L12 | **AGGRESSIVE** | BGE-M3 is the one clear upgrade worth making. Same API (one-line change), 12.5% quality improvement, 8192-token context enables full-article embedding, hybrid dense+sparse retrieval matches InvestScan's dedup needs exactly. Low risk, high reward. |
| **Topic Modeling** | BERTopic + repr stack | BERTopic (keep) | **Conservative** | BERTopic is already SOTA. Upgrading the representation model stack changes topic quality in untested ways. Keep the proven configuration. |
| **Financial Sentiment** | KcELECTRA + SetFit | Keyword dictionary | **Conservative, with trigger** | Start rule-based (3-4 hours, 65-75% accuracy). If accuracy drops below 70% on real data after 8 weeks, invest 8-10 hours in SetFit. Do not pre-build ML when rules may suffice. |
| **Classification** | SetFit few-shot | Keyword rules | **Conservative, with trigger** | Same logic as sentiment. Rule-based STEEPs classification at 70-80% is adequate for M1-M2. Invest in SetFit only when rule-based errors cause visible report quality issues. |
| **Time-Series Storage** | DuckDB + Parquet | SQLite + Parquet | **Conservative initially, AGGRESSIVE at Month 4** | SQLite is sufficient for <10K signals. At Month 4 (8+ weeks of data), if analytical queries slow down or become complex, switch to DuckDB. Migration: zero (both read the same Parquet files). |
| **Graph Analysis** | NetworkX | SQL JOINs | **Conservative** | Cross-domain impact analysis via SQL JOINs covers 90% of use cases for <1000 signals. Add NetworkX only when multi-hop relationship queries become necessary. |
| **Report Generation** | Jinja2 + Ollama hybrid | Jinja2 only | **Conservative, with Month 4 experiment** | Financial reports MUST be deterministic and hallucination-free. Start with Jinja2 only. At Month 4, experiment with Ollama for the executive summary section only (clearly marked as AI-generated). Never let LLM touch data tables or evidence chains. |
| **Orchestration** | Snakemake | subprocess + launchd | **Conservative** | 5-step linear pipeline does not need DAG management. subprocess + launchd is 22+ years proven. Add Snakemake only if pipeline grows to 10+ steps with conditional branches. |

---

### Composite Recommendation: "Conservative Core + One Aggressive Bet"

```
ADOPT NOW (Month 1):
  [AGGRESSIVE] BGE-M3 embeddings  ← One-line swap, 12.5% improvement, low risk
  [CONSERVATIVE] Everything else   ← Kiwi, BERTopic, keyword rules, SQLite+Parquet, Jinja2, subprocess

ADOPT IF TRIGGERED (Month 4+):
  [AGGRESSIVE] DuckDB              ← When analytical queries become complex (same Parquet files)
  [AGGRESSIVE] SetFit classifiers  ← When rule-based accuracy < 70% on real data
  [AGGRESSIVE] Ollama narrative    ← Experiment for executive summary only, clearly marked
  [AGGRESSIVE] eKoNLPy             ← When specific financial terms cause errors
  [AGGRESSIVE] NetworkX            ← When multi-hop relationship queries needed

DO NOT ADOPT (not justified for InvestScan):
  E5-Mistral-7B    ← 14 GB RAM for embeddings is disproportionate
  Neo4j            ← Server database for <1000-node graph is absurd
  InfluxDB         ← Time-series server for weekly batch of 200 signals
  TimescaleDB      ← PostgreSQL extension for a SQLite-scale workload
  Airflow/Prefect  ← Enterprise orchestration for a 5-step pipeline
  Snakemake        ← DAG engine for a linear pipeline
  Full fine-tuning ← 1000+ labels for 3 classifiers when SetFit needs 48
```

---

### Decision Matrix: Scoring Summary

| Criterion | Weight | Aggressive Score | Conservative Score | Winner |
|-----------|--------|-----------------|-------------------|--------|
| **Stability (5yr+ track record)** | 25% | 7.5/10 | 10/10 | **Conservative** |
| **Capability ceiling** | 15% | 9.0/10 | 6.7/10 | **Aggressive** |
| **Learning curve (solo dev, 2-4 hrs/week)** | 25% | 6.5/10 | 10/10 | **Conservative** |
| **Maintenance burden** | 20% | 7.0/10 | 10/10 | **Conservative** |
| **Upgrade path (can adopt later?)** | 15% | N/A | 9.0/10 | **Conservative** |
| **Weighted Total** | 100% | **7.3/10** | **9.2/10** | **Conservative** |

### The Decisive Insight

**InvestScan's bottleneck is not technology -- it is the developer's 2-4 hours/week.**

Every hour spent learning Snakemake, debugging SetFit training, or tuning Ollama prompts is an hour NOT spent on the core value proposition: STEEPs classification, multi-source convergence detection, and evidence chain construction. The conservative stack delivers ~85% of the aggressive stack's capability at ~30% of the learning/maintenance cost.

**The one exception is BGE-M3**: It is the rare technology upgrade that costs almost nothing (one-line model name change, same API) while delivering meaningful improvement (12.5% better embeddings, 16x longer context). This is the only aggressive choice justified on Day 1.

**Everything else**: Build with conservative tech, prove the product works, then selectively adopt aggressive options when the conservative approach demonstrably fails. The triggers are concrete and measurable:
- Rule-based accuracy < 70% --> SetFit
- SQLite query time > 1 second --> DuckDB
- Report narrative quality complaints --> Ollama experiment
- Pipeline > 10 steps --> Snakemake

This is not "settling for less." This is engineering discipline: **prove the need before buying the tool.**

---

### Sources

- [BGE-M3 on Hugging Face](https://huggingface.co/BAAI/bge-m3)
- [Best Embedding Models 2025: MTEB Leaderboard](https://app.ailog.fr/en/blog/guides/choosing-embedding-models)
- [Open-Source Embedding Models 2026](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models)
- [BGE, E5-Large, Instructor, MiniLM Comparison](https://bizety.com/2025/11/10/bge-e5-large-instructor-and-minilme-embedding-models/)
- [BERTopic vs Top2Vec Academic Comparison](https://www.frontiersin.org/journals/sociology/articles/10.3389/fsoc.2022.886498/full)
- [Experimental Comparison: LDA, Top2Vec, BERTopic (Springer)](https://link.springer.com/chapter/10.1007/978-981-99-9109-9_37)
- [Multilingual Topic Model Evaluation 2025 (Springer)](https://link.springer.com/article/10.1007/s11063-025-11820-3)
- [Won: Korean Financial NLP Model (arXiv)](https://arxiv.org/html/2503.17963v1)
- [KcELECTRA: Korean Comments ELECTRA](https://github.com/Beomi/KcELECTRA)
- [KOSELF: Korean Sentiment Lexicon for Finance](https://www.researchgate.net/publication/351233159_Building_the_Korean_Sentiment_Lexicon_for_Finance_KOSELF)
- [SetFit: Efficient Few-Shot Learning](https://huggingface.co/blog/setfit)
- [DuckDB vs SQLite Comparison (DataCamp)](https://www.datacamp.com/blog/duckdb-vs-sqlite-complete-database-comparison)
- [DuckDB 2.0: SQLite of Analytics](https://markaicode.com/dduckdb-2-analytics-database-2025/)
- [DuckDB Is Eating the Data World (2026)](https://medium.com/@garimakansal22/duckdb-is-eating-the-data-world-heres-why-f586b7d8dcf1)
- [NetworkX vs Neo4j Drag Race](https://towardsdatascience.com/fire-up-your-centrality-metric-engines-neo4j-vs-networkx-a-drag-race-of-sorts-18857f25be35/)
- [Qwen 3 vs Llama 3 Local Deployment](https://blog.premai.io/qwen-3-vs-llama-3-for-local-deployment-which-model-what-hardware-and-when-to-skip-diy/)
- [Qwen2.5 on Ollama](https://ollama.com/library/qwen2.5)
- [Snakemake vs Nextflow 2025](https://sagc-bioinformatics.github.io/nextflow-vs-snakemake-2025/snakemake/)
- [Bioinformatics Pipeline Frameworks 2025](https://www.tracer.cloud/resources/bioinformatics-pipeline-frameworks-2025)
- [mGTE Multilingual Embedding (Alibaba)](https://huggingface.co/Alibaba-NLP/gte-multilingual-base)
- [Qwen-3 vs BGE-M3 Analysis](https://medium.com/@mrAryanKumar/comparative-analysis-of-qwen-3-and-bge-m3-embedding-models-for-multilingual-information-retrieval-72c0e6895413)
- [FinBERT Sector-Specific Fine-Tuning (MDPI)](https://www.mdpi.com/2079-9292/14/23/4680)
- [Time-Series Database Benchmarks 2025](https://www.timestored.com/data/time-series-database-benchmarks)
- [InfluxDB vs TimescaleDB Comparison](https://markaicode.com/time-series-databases-2025-comparison/)
- [eKoNLPy: Korean NLP for Economic Analysis](https://github.com/entelecheia/eKoNLPy)
- [Korean NLP Tokenization Study (ACL)](https://aclanthology.org/2020.aacl-main.17/)
