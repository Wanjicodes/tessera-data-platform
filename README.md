# unified-data-platform

> Built by **Wanjiru Ndung'u** — Data Engineer  
> [LinkedIn](https://www.linkedin.com/in/junewanjirundungu/) · [GitHub](https://github.com/Wanjicodes)

**A production-grade data engineering platform for hostile, fragmented, multi-source environments.**

Most data engineering projects start with clean data. This one doesn't.

This platform was designed around a real operational constraint I have worked with in practice: multiple enterprise clients, each with their own source systems, inconsistent field definitions, conflicting KPI logic, and no shared data infrastructure — all requiring trusted, decision-ready outputs simultaneously, across 12 markets.

It is not a tutorial. It is not a demo. It is a reference architecture built from genuine experience structuring messy source data, standardising metric logic, and building systems that make analysis trusted, reusable and decision-ready.

---

## The problem this solves

Large organisations — in aviation, energy, fintech, and multi-market commercial operations — share a common data failure pattern:

- **Source fragmentation**: data lives in 4–10 disconnected systems with no canonical model
- **Definition conflicts**: the same metric means different things in different markets or teams
- **Trust collapse**: stakeholders stop trusting reports because numbers don't reconcile
- **Pipeline fragility**: manual fixes and workarounds become load-bearing infrastructure

This platform addresses all four at the architectural level — not as patches, but as first principles.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                         │
│   Multi-source connectors · Schema registry · Raw storage   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    VALIDATION LAYER                         │
│   Data contracts · Quality checks · Failure routing         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   TRANSFORM LAYER  (dbt)                    │
│   Staging → Intermediate → Marts · Metric definitions       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     SERVING LAYER                           │
│   FastAPI · Metric store · Lineage endpoints                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  OBSERVABILITY LAYER                        │
│   Pipeline monitors · Data lineage · Alerting               │
└─────────────────────────────────────────────────────────────┘

Orchestration: Prefect flows wrap all layers with scheduling,
retry logic, and structured failure logging.
```

---

## Stack

| Layer | Technology | Why |
|---|---|---|
| Ingestion | Python · `httpx` · `pandas` | Modular connector pattern — swap sources without touching pipeline logic |
| Validation | Custom data contracts · `great_expectations` | Contracts defined in YAML — validation is configuration, not code |
| Transform | `dbt` · DuckDB | Full staging → intermediate → mart lineage with documented metric definitions |
| Orchestration | `Prefect` | Parameterised flows, retry logic, structured failure logs |
| Serving | `FastAPI` | Data as a product — metrics and lineage exposed as versioned API endpoints |
| Observability | Custom monitors · structured logging | Pipeline health visible without external tooling dependencies |
| Testing | `pytest` · dbt tests | Contract tests, pipeline unit tests, and dbt schema tests in one run |

---

## Key design decisions

See [`/docs/decisions/`](docs/decisions/) for full Architecture Decision Records.

**ADR-001**: Why data contracts are defined in YAML, not enforced in code  
**ADR-002**: Why DuckDB over PostgreSQL for local transform  
**ADR-003**: Why Prefect over Airflow for this architecture  
**ADR-004**: Why the metric store is separated from the reporting layer  

---

## Project structure

```
unified-data-platform/
│
├── ingestion/
│   ├── base_connector.py       # Abstract connector — all sources implement this interface
│   ├── multi_source_loader.py  # Orchestrates parallel ingestion across N sources
│   └── schema_registry.py      # Source schema definitions and version tracking
│
├── validation/
│   ├── data_contracts.py       # Contract engine — loads YAML, runs checks, routes failures
│   └── quality_checks.py       # Reusable check library (nulls, ranges, referential integrity)
│
├── transform/                  # dbt project
│   ├── staging/                # Raw → typed, renamed, light cleaning only
│   ├── intermediate/           # Business logic, joins, metric building blocks
│   └── marts/                  # Decision-ready outputs by domain
│
├── serving/
│   ├── api.py                  # FastAPI app — /metrics, /lineage, /health endpoints
│   └── metric_store.py         # Metric registry with ownership, logic, and refresh cadence
│
├── orchestration/
│   └── pipeline_dag.py         # Prefect flow definitions — full pipeline end to end
│
├── observability/
│   ├── lineage.py              # Column-level lineage tracking
│   └── monitors.py             # Pipeline health checks and alerting hooks
│
├── config/
│   ├── sources.yaml            # Source system definitions
│   ├── metrics.yaml            # Metric definitions — owner, logic, thresholds, cadence
│   └── contracts.yaml          # Data contract rules per source
│
├── docs/
│   ├── decisions/              # Architecture Decision Records (ADR-001 through ADR-004)
│   └── case-studies/           # Anonymised real-world problem write-ups
│
├── tests/
│   ├── test_contracts.py       # Contract validation unit tests
│   └── test_pipeline.py        # Pipeline integration tests
│
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## Quickstart

```bash
# Clone
git clone https://github.com/Wanjicodes/unified-data-platform
cd unified-data-platform

# Install dependencies
pip install -r requirements.txt

# Run pipeline end to end (demo mode — aviation dataset)
python orchestration/pipeline_dag.py --source aviation --mode demo

# Start the serving API
uvicorn serving.api:app --reload

# Run all tests
pytest tests/

# Generate dbt docs
cd transform && dbt docs generate && dbt docs serve
```

---

## Demo dataset

The platform ships with a public aviation operations dataset (sourced from OpenFlights + BTS) as the default demo input. This illustrates the fragmentation problem concretely: two sources, different schemas, conflicting route identifiers, and inconsistent delay categorisation — unified by the platform into a single trusted operational view.

**The aviation dataset is illustrative. The architecture applies equally to:**
- Energy: multi-site consumption + pricing feeds with conflicting unit definitions
- Fintech: transaction systems with market-level rule variations
- Healthcare: patient data across clinic systems with no shared identifier

---

## Case studies

See [`/docs/case-studies/`](docs/case-studies/) for anonymised write-ups of real fragmented data environments this architecture pattern was built to solve.

---

## What this demonstrates

- **Data contracts as configuration** — validation rules defined in YAML, not buried in transformation code
- **Metric governance** — every KPI has an owner, a definition, and a test. No undocumented metrics.
- **Layer separation** — ingestion, validation, transform, and serving are independently deployable and testable
- **Production discipline** — structured failure logging, retry logic, lineage tracking, and schema versioning from day one
- **Data as a product** — outputs exposed as versioned API endpoints, not just files or tables

---

## Author

**Wanjiru Ndung'u** — Data Engineer

I build scalable data systems, metric layers and decision infrastructure for enterprise analytics and applied data science. My work sits at the intersection of data engineering, analytics engineering and business problem-solving — structuring messy source data, designing reliable transformation workflows, improving data quality, standardising metric logic, and building systems that make analysis more trusted, reusable and decision-ready.

Currently extending public proof in data engineering, analytics engineering, forecasting, experimentation and governance-minded data systems. Open to senior data engineering and analytics engineering roles in the UAE and Europe.

[LinkedIn](https://www.linkedin.com/in/junewanjirundungu/) · [GitHub](https://github.com/Wanjicodes)
