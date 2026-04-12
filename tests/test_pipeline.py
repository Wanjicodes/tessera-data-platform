"""
tests/test_pipeline.py

Pipeline integration tests.

Tests verify that each layer of the pipeline — ingestion, validation,
merge, and serving — behaves correctly end to end.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

from ingestion.base_connector import IngestionResult
from ingestion.multi_source_loader import merge_results
from validation.data_contracts import DataContractEngine, ContractResult
from observability.monitors import PipelineMonitor
from observability.lineage import LineageTracker
from serving.metric_store import MetricStore


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_ingestion_results():
    df_a = pd.DataFrame({
        "flight_id": ["F001", "F002", "F003"],
        "flight_status": ["on_time", "delayed", "cancelled"],
        "departure_delay_minutes": [0, 45, 0],
        "origin_iata": ["DXB", "AUH", "DXB"],
        "destination_iata": ["LHR", "JFK", "SIN"],
    })
    df_b = pd.DataFrame({
        "flight_id": ["F004", "F005"],
        "flight_status": ["on_time", "delayed"],
        "departure_delay_minutes": [2, 30],
        "origin_iata": ["AUH", "DXB"],
        "destination_iata": ["LHR", "CDG"],
    })
    return {
        "source_a": IngestionResult(
            source_id="source_a",
            records_fetched=3,
            schema_version="1.0.0",
            fetched_at=datetime.utcnow(),
            success=True,
            data=df_a,
        ),
        "source_b": IngestionResult(
            source_id="source_b",
            records_fetched=2,
            schema_version="1.0.0",
            fetched_at=datetime.utcnow(),
            success=True,
            data=df_b,
        ),
    }


@pytest.fixture
def sample_contract_results():
    return {
        "source_a": ContractResult(source_id="source_a", passed=True, records_checked=3),
        "source_b": ContractResult(source_id="source_b", passed=True, records_checked=2),
    }


@pytest.fixture
def metrics_config(tmp_path):
    import yaml
    config = {
        "metrics": [
            {
                "name": "test_metric",
                "display_name": "Test Metric",
                "owner": "test-team",
                "description": "A test metric",
                "calculation": "COUNT(*)",
                "unit": "count",
                "refresh_cadence": "daily",
                "version": "1.0.0",
                "thresholds": {"warn_below": 10},
                "tags": ["test"],
                "notes": "",
            }
        ]
    }
    config_file = tmp_path / "metrics.yaml"
    config_file.write_text(yaml.dump(config))
    return config_file


# ── Ingestion tests ────────────────────────────────────────────────────────────

def test_successful_ingestion_result_has_data(sample_ingestion_results):
    result = sample_ingestion_results["source_a"]
    assert result.success is True
    assert result.records_fetched == 3
    assert not result.data.empty


def test_failed_ingestion_result_has_empty_data():
    result = IngestionResult(
        source_id="bad_source",
        records_fetched=0,
        schema_version="unknown",
        fetched_at=datetime.utcnow(),
        success=False,
        data=pd.DataFrame(),
        errors=["Connection timeout"],
    )
    assert result.success is False
    assert result.data.empty
    assert len(result.errors) == 1


# ── Merge tests ────────────────────────────────────────────────────────────────

def test_merge_combines_all_sources(sample_ingestion_results):
    merged = merge_results(sample_ingestion_results)
    assert len(merged) == 5
    assert "_source_id" in merged.columns
    assert set(merged["_source_id"].unique()) == {"source_a", "source_b"}


def test_merge_skips_failed_sources(sample_ingestion_results):
    sample_ingestion_results["source_b"].success = False
    sample_ingestion_results["source_b"].data = pd.DataFrame()
    merged = merge_results(sample_ingestion_results)
    assert len(merged) == 3
    assert "source_b" not in merged["_source_id"].values


def test_merge_adds_lineage_columns(sample_ingestion_results):
    merged = merge_results(sample_ingestion_results)
    assert "_source_id" in merged.columns
    assert "_ingested_at" in merged.columns
    assert "_schema_version" in merged.columns


def test_merge_empty_results_returns_empty_dataframe():
    merged = merge_results({})
    assert isinstance(merged, pd.DataFrame)
    assert merged.empty


# ── Monitor tests ──────────────────────────────────────────────────────────────

def test_monitor_healthy_when_all_pass(sample_ingestion_results, sample_contract_results):
    monitor = PipelineMonitor()
    report = monitor.evaluate(sample_ingestion_results, sample_contract_results, run_id="test_run")
    assert report.overall_status == "healthy"
    assert len(report.ingestion_failures) == 0
    assert len(report.contract_failures) == 0


def test_monitor_failed_when_ingestion_fails(sample_ingestion_results, sample_contract_results):
    sample_ingestion_results["source_a"].success = False
    monitor = PipelineMonitor()
    report = monitor.evaluate(sample_ingestion_results, sample_contract_results, run_id="test_run")
    assert report.overall_status == "failed"
    assert "source_a" in report.ingestion_failures


def test_monitor_degraded_when_contract_fails(sample_ingestion_results, sample_contract_results):
    sample_contract_results["source_b"].passed = False
    monitor = PipelineMonitor()
    report = monitor.evaluate(sample_ingestion_results, sample_contract_results, run_id="test_run")
    assert report.overall_status == "degraded"
    assert "source_b" in report.contract_failures


# ── Metric store tests ─────────────────────────────────────────────────────────

def test_metric_store_loads_definitions(metrics_config):
    store = MetricStore(config_path=metrics_config)
    assert len(store.list_all()) == 1


def test_metric_store_get_known_metric(metrics_config):
    store = MetricStore(config_path=metrics_config)
    metric = store.get("test_metric")
    assert metric is not None
    assert metric.owner == "test-team"


def test_metric_store_get_unknown_metric_returns_none(metrics_config):
    store = MetricStore(config_path=metrics_config)
    metric = store.get("nonexistent_metric")
    assert metric is None


def test_metric_store_validate_exists(metrics_config):
    store = MetricStore(config_path=metrics_config)
    assert store.validate_metric_exists("test_metric") is True
    assert store.validate_metric_exists("ghost_metric") is False


def test_metric_store_to_dataframe(metrics_config):
    store = MetricStore(config_path=metrics_config)
    df = store.to_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert "name" in df.columns
    assert len(df) == 1


# ── Lineage tests ──────────────────────────────────────────────────────────────

def test_lineage_tracker_records_and_retrieves(tmp_path):
    tracker = LineageTracker(log_path=tmp_path / "lineage.jsonl")
    tracker.record(
        source_id="test_source",
        run_id="run_001",
        records_in=100,
        contract_passed=True,
        schema_version="1.0.0",
        ingested_at=datetime.utcnow(),
    )
    results = tracker.get_lineage("test_source")
    assert results is not None
    assert len(results) == 1
    assert results[0]["source_id"] == "test_source"
    assert results[0]["run_id"] == "run_001"


def test_lineage_tracker_returns_none_for_unknown_source(tmp_path):
    tracker = LineageTracker(log_path=tmp_path / "lineage.jsonl")
    result = tracker.get_lineage("unknown_source")
    assert result is None


def test_lineage_tracker_get_all_empty(tmp_path):
    tracker = LineageTracker(log_path=tmp_path / "lineage.jsonl")
    assert tracker.get_all() == []
