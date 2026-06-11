# tessera-data-platform

> _Where fragmented data sources become a coherent picture._

Built by **Wanjiru Ndung'u** · Data Engineer  
[LinkedIn](https://www.linkedin.com/in/junewanjirundungu/) · [GitHub](https://github.com/Wanjicodes)

---

## The idea

A tessera is a single tile in a mosaic. On its own it tells you nothing. Assembled with others, it becomes a picture.

That is the problem this platform solves. Enterprise data does not arrive whole. It arrives as fragments from systems that do not agree with each other, with conflicting definitions and inconsistent shapes. The work is not analysis. The work is assembly.

`tessera` is a reference architecture for that assembly. It takes fragmented source data and produces something coherent enough to make decisions from.


## Lineage

![dbt lineage graph](docs/images/lineage-graph.png)

*Full data flow from raw sources through staging, intermediate, and mart layers. Every model is tested, documented, and traceable.*


## What it does

Five layers, each with a single responsibility.

**Ingestion.** Pulls data from any source through a common connector interface. Adding a new source is a config entry, not a code change.

**Validation.** Runs data contracts defined in YAML. Catches source-level issues before they reach the transform layer. Contracts are configuration, not buried logic.

**Transformation.** A dbt project structured as staging, intermediate, marts. Business rules live in one place. Metric definitions are versioned and owned.

**Serving.** A FastAPI layer that exposes metrics and lineage as endpoints. Data as a product, not just a report.

**Observability.** Lineage tracking, schema drift detection, pipeline health monitors. The platform watches itself.

## Why this shape

Most data platforms treat the data as the problem. This one treats the fragmentation as the problem.

That difference shows up everywhere. The contract engine assumes sources will disagree. The metric store assumes definitions will be contested. The transformation layer separates business rules from presentation so the rules can change without rewriting outputs. Schema registries detect upstream drift before it breaks downstream models.

These are not optimisations. They are the architecture.

## Stack

| Layer | Tools |
|---|---|
| Ingestion | Python, modular connectors |
| Validation | YAML data contracts, custom rule engine |
| Transform | dbt, DuckDB locally, portable to Snowflake, BigQuery, Postgres |
| Orchestration | Prefect |
| Serving | FastAPI |
| Observability | Structured logging, JSONL lineage, schema registry |
| Testing | pytest, dbt tests, custom assertions |
| CI | GitHub Actions |

## Quickstart

```bash
git clone https://github.com/Wanjicodes/tessera-data-platform
cd tessera-data-platform

python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
python data\generate_demo_data.py

# Run the Python pipeline
set PYTHONPATH=.
python orchestration\pipeline_dag.py --source all --mode demo

# Run the dbt transform layer
cd transform
dbt deps
dbt build
dbt docs generate
dbt docs serve

# Start the API
uvicorn serving.api:app --reload
```

Endpoints once running:
- `http://localhost:8000/docs` — interactive API documentation
- `http://localhost:8000/metrics` — the governed metric registry
- `http://localhost:8000/health/metrics-audit` — governance score

## Project structure

```
tessera-data-platform/
├── ingestion/          # Source connectors, schema registry
├── validation/         # Contract engine, quality checks
├── transform/          # dbt project — staging → intermediate → marts
├── serving/            # FastAPI metric store and lineage endpoints
├── observability/      # Lineage tracker, pipeline monitors
├── orchestration/      # Prefect pipeline definitions
├── config/             # sources.yaml, metrics.yaml, contracts.yaml
├── docs/
│   ├── decisions/      # Architecture Decision Records
│   └── case-studies/   # Real fragmentation problems, anonymised
├── tests/              # pytest suite
└── data/               # Demo data generator
```

## Demo data

The platform ships with aviation operations data as the default demo input. Two CSV sources that deliberately disagree with each other — different identifier formats, intentional null values, conflicting status codes. The platform's job is to make sense of them.

The aviation data is illustrative. The same architecture pattern applies to energy, fintech, healthcare, and any sector where enterprise data arrives fragmented.

## Design decisions

The `docs/decisions/` folder contains four Architecture Decision Records explaining why this platform was built the way it was:

- ADR-001: Why contracts are defined in YAML, not in code
- ADR-002: Why DuckDB for local transform
- ADR-003: Why Prefect instead of Airflow
- ADR-004: Why the metric store sits separately from the reporting layer

These exist because the design choices matter as much as the code. If you are reviewing this project as a hiring manager or fellow engineer, the ADRs explain the thinking.

## Case study

`docs/case-studies/multi-market-fragmentation.md` walks through a real production problem this architecture pattern was built to solve. Anonymised, but every detail is from work I have actually done.

## About

I am a Data Engineer based in Dubai. I build the systems that sit underneath enterprise analytics. This platform reflects how I think about that work fragmented data as the central problem, governance as the central solution, layers that each do one thing.

If you are hiring for senior data engineering or analytics engineering roles where the data environment is genuinely complex, I would like to talk.

[LinkedIn](https://www.linkedin.com/in/junewanjirundungu/) · [GitHub](https://github.com/Wanjicodes)
