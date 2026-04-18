"""
tests/test_contracts.py

Contract validation unit tests.

Tests confirm that the contract engine catches the violations it should,
passes the data it should, and produces structured results in both cases.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
from validation.data_contracts import DataContractEngine, ContractResult


MOCK_CONTRACTS = {
    "contracts": {
        "test_source": [
            {"rule": "not_null", "column": "flight_id", "severity": "error"},
            {"rule": "unique", "column": "flight_id", "severity": "error"},
            {"rule": "accepted_values", "column": "status",
             "values": ["on_time", "delayed", "cancelled"], "severity": "error"},
            {"rule": "min_value", "column": "delay_minutes", "value": 0, "severity": "warning"},
            {"rule": "not_empty", "min_rows": 2, "severity": "error"},
        ]
    }
}


@pytest.fixture
def engine(tmp_path):
    import yaml
    config_file = tmp_path / "contracts.yaml"
    config_file.write_text(yaml.dump(MOCK_CONTRACTS))
    return DataContractEngine(config_path=config_file)


@pytest.fixture
def clean_df():
    return pd.DataFrame({
        "flight_id": ["F001", "F002", "F003"],
        "status": ["on_time", "delayed", "cancelled"],
        "delay_minutes": [0, 45, 0],
    })


def test_clean_data_passes_all_contracts(engine, clean_df):
    result = engine.validate("test_source", clean_df)
    assert result.passed is True
    assert result.error_count == 0


def test_null_flight_id_raises_error(engine, clean_df):
    dirty = clean_df.copy()
    dirty.loc[0, "flight_id"] = None
    result = engine.validate("test_source", dirty)
    assert result.passed is False
    violations = [v for v in result.violations if v.rule_name == "not_null"]
    assert len(violations) == 1
    assert violations[0].failed_record_count == 1


def test_duplicate_flight_id_raises_error(engine, clean_df):
    dirty = clean_df.copy()
    dirty.loc[1, "flight_id"] = "F001"
    result = engine.validate("test_source", dirty)
    assert result.passed is False
    violations = [v for v in result.violations if v.rule_name == "unique"]
    assert len(violations) == 1


def test_invalid_status_raises_error(engine, clean_df):
    dirty = clean_df.copy()
    dirty.loc[0, "status"] = "unknown_status"
    result = engine.validate("test_source", dirty)
    assert result.passed is False
    violations = [v for v in result.violations if v.rule_name == "accepted_values"]
    assert len(violations) == 1


def test_negative_delay_is_warning_not_error(engine, clean_df):
    dirty = clean_df.copy()
    dirty.loc[0, "delay_minutes"] = -5
    result = engine.validate("test_source", dirty)
    # Warning should not cause overall failure
    assert result.passed is True
    assert result.warning_count == 1
    assert result.error_count == 0


def test_empty_dataframe_fails_not_empty_rule(engine):
    empty_df = pd.DataFrame(columns=["flight_id", "status", "delay_minutes"])
    result = engine.validate("test_source", empty_df)
    assert result.passed is False


def test_unknown_source_returns_passed_with_warning(engine):
    df = pd.DataFrame({"col": [1, 2, 3]})
    result = engine.validate("nonexistent_source", df)
    assert result.passed is True  # No contract = no failure, but logs a warning


def test_contract_result_summary_string(engine, clean_df):
    result = engine.validate("test_source", clean_df)
    summary = result.summary()
    assert "test_source" in summary
    assert "PASSED" in summary
