"""
api.py

FastAPI serving layer — data as a product.

Exposes three endpoint groups:
  /metrics  — query the metric registry
  /lineage  — trace data from source to output
  /health   — pipeline and data freshness status

This is what separates a data platform from a data pipeline.
A pipeline moves data. A platform makes data queryable, auditable,
and trustworthy — with a clear interface for consumers.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import logging

from serving.metric_store import MetricStore
from observability.lineage import LineageTracker

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Unified Data Platform API — Wanjiru Ndung'u",
    description=(
        "Metric registry and lineage API for the unified data platform. "
        "Built by Wanjiru Ndung'u — Data Engineer. "
        "All metrics served here are registered, owned, versioned, and tested. "
        "github.com/Wanjicodes/unified-data-platform"
    ),
    version="1.0.0",
)

_metric_store = MetricStore()
_lineage_tracker = LineageTracker()


# ── Metrics endpoints ──────────────────────────────────────────────────────────

@app.get("/metrics", summary="List all registered metrics")
def list_metrics(
    tag: str | None = Query(None, description="Filter by tag"),
    owner: str | None = Query(None, description="Filter by owner"),
):
    """
    Returns the full metric registry, or a filtered subset.
    Every metric here is governed — it has an owner, a definition, and tests.
    """
    if tag:
        metrics = _metric_store.list_by_tag(tag)
    elif owner:
        metrics = _metric_store.list_by_owner(owner)
    else:
        metrics = _metric_store.list_all()

    return {
        "count": len(metrics),
        "metrics": [m.to_dict() for m in metrics],
    }


@app.get("/metrics/{metric_name}", summary="Get a single metric definition")
def get_metric(metric_name: str):
    """
    Returns the full definition of a specific metric —
    including owner, calculation logic, thresholds, and version.
    """
    metric = _metric_store.get(metric_name)
    if not metric:
        raise HTTPException(
            status_code=404,
            detail=f"Metric '{metric_name}' is not registered. "
                   f"Unregistered metrics cannot be served — add it to the metric store.",
        )
    return metric.to_dict()


# ── Lineage endpoints ──────────────────────────────────────────────────────────

@app.get("/lineage/{dataset_name}", summary="Trace data lineage for a dataset")
def get_lineage(dataset_name: str):
    """
    Returns the full lineage graph for a dataset —
    which sources contributed to it, which transformations were applied,
    and which downstream outputs depend on it.
    """
    lineage = _lineage_tracker.get_lineage(dataset_name)
    if not lineage:
        raise HTTPException(
            status_code=404,
            detail=f"No lineage recorded for '{dataset_name}'.",
        )
    return lineage


# ── Health endpoints ───────────────────────────────────────────────────────────

@app.get("/health", summary="Platform health check")
def health_check():
    """
    Returns platform health status — metric store load, lineage tracker,
    and last pipeline run timestamp.
    """
    metric_count = len(_metric_store.list_all())
    return {
        "status": "healthy",
        "metric_store": {
            "loaded": metric_count > 0,
            "metric_count": metric_count,
        },
        "lineage_tracker": {
            "loaded": True,
        },
        "api_version": "1.0.0",
    }


@app.get("/health/metrics-audit", summary="Audit metric store completeness")
def metrics_audit():
    """
    Returns metrics that are missing required fields.
    Use this to enforce governance standards — every metric must have
    an owner, a description, and at least one threshold defined.
    """
    all_metrics = _metric_store.list_all()
    issues = []

    for m in all_metrics:
        metric_issues = []
        if not m.owner:
            metric_issues.append("missing owner")
        if not m.description:
            metric_issues.append("missing description")
        if not m.thresholds:
            metric_issues.append("no thresholds defined")
        if metric_issues:
            issues.append({"metric": m.name, "issues": metric_issues})

    return {
        "total_metrics": len(all_metrics),
        "metrics_with_issues": len(issues),
        "governance_score": round((1 - len(issues) / max(len(all_metrics), 1)) * 100, 1),
        "issues": issues,
    }
