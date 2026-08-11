from __future__ import annotations

import app.metrics as metrics_module
from app.metrics import percentile


def _reset_metrics_state() -> None:
    metrics_module.REQUEST_LATENCIES.clear()
    metrics_module.REQUEST_COSTS.clear()
    metrics_module.REQUEST_TOKENS_IN.clear()
    metrics_module.REQUEST_TOKENS_OUT.clear()
    metrics_module.REQUEST_TIMESTAMPS.clear()
    metrics_module.ERRORS.clear()
    metrics_module.QUALITY_SCORES.clear()
    metrics_module.TRAFFIC = 0


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_percentile_known_values() -> None:
    assert percentile([100, 200, 300, 400], 50) == 200.0
    assert percentile([100, 200, 300, 400], 95) == 400.0
    assert percentile([100, 200, 300, 400], 100) == 400.0


def test_percentile_single_value() -> None:
    assert percentile([77], 95) == 77.0


def test_percentile_empty_returns_zero() -> None:
    assert percentile([], 50) == 0.0


def test_record_request_updates_snapshot() -> None:
    _reset_metrics_state()
    metrics_module.record_request(latency_ms=100, cost_usd=0.01, tokens_in=50, tokens_out=90, quality_score=0.8)
    metrics_module.record_request(latency_ms=200, cost_usd=0.02, tokens_in=60, tokens_out=100, quality_score=0.9)

    snap = metrics_module.snapshot()
    assert snap["traffic"] == 2
    assert snap["tokens_in_total"] == 110
    assert snap["tokens_out_total"] == 190
    assert snap["avg_cost_usd"] == 0.015
    assert snap["quality_avg"] == 0.85


def test_error_rate_pct_reflects_recorded_errors() -> None:
    _reset_metrics_state()
    metrics_module.record_request(latency_ms=100, cost_usd=0.01, tokens_in=50, tokens_out=90, quality_score=0.8)
    metrics_module.record_request(latency_ms=200, cost_usd=0.02, tokens_in=60, tokens_out=100, quality_score=0.9)
    metrics_module.record_error("RuntimeError")
    metrics_module.record_error("TimeoutError")

    snap = metrics_module.snapshot()
    assert snap["error_rate_pct"] == 100.0
    assert snap["error_breakdown"] == {"RuntimeError": 1, "TimeoutError": 1}


def test_snapshot_contains_dashboard_metric_keys() -> None:
    _reset_metrics_state()
    snap = metrics_module.snapshot()
    for key in (
        "traffic",
        "traffic_rate_per_minute",
        "latency_p50",
        "latency_p95",
        "latency_p99",
        "total_cost_usd",
        "tokens_in_total",
        "tokens_out_total",
        "error_rate_pct",
        "error_breakdown",
        "quality_avg",
    ):
        assert key in snap
