from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_validator(
    config_path: Path,
    *,
    slo_config: Path | None = None,
    alerts_config: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "validate_dashboard.py"),
        "--config",
        str(config_path),
    ]
    if slo_config is not None:
        command += ["--slo-config", str(slo_config)]
    if alerts_config is not None:
        command += ["--alerts-config", str(alerts_config)]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_repository_dashboard_contract_is_valid() -> None:
    result = run_validator(REPO_ROOT / "config" / "dashboard.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "6/6 panel" in result.stdout


def test_validator_rejects_panel_without_threshold(tmp_path: Path) -> None:
    payload = yaml.safe_load(
        (REPO_ROOT / "config" / "dashboard.yaml").read_text(encoding="utf-8")
    )
    del payload["dashboard"]["panels"][0]["threshold"]
    invalid_config = tmp_path / "dashboard.yaml"
    invalid_config.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    result = run_validator(invalid_config)

    assert result.returncode == 1
    assert "latency.threshold" in result.stdout


def test_validator_rejects_panel_without_query_example(tmp_path: Path) -> None:
    payload = yaml.safe_load(
        (REPO_ROOT / "config" / "dashboard.yaml").read_text(encoding="utf-8")
    )
    payload["dashboard"]["panels"][0].pop("query", None)
    invalid_config = tmp_path / "dashboard.yaml"
    invalid_config.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    result = run_validator(invalid_config)

    assert result.returncode == 1
    assert "latency.query" in result.stdout


def test_repository_slo_config_is_valid() -> None:
    result = run_validator(REPO_ROOT / "config" / "dashboard.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "SLO config" in result.stdout


def test_validator_rejects_slo_missing_required_sli(tmp_path: Path) -> None:
    payload = yaml.safe_load(
        (REPO_ROOT / "config" / "slo.yaml").read_text(encoding="utf-8")
    )
    del payload["slis"]["quality_score_avg"]
    invalid_slo = tmp_path / "slo.yaml"
    invalid_slo.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    result = run_validator(REPO_ROOT / "config" / "dashboard.yaml", slo_config=invalid_slo)

    assert result.returncode == 1
    assert "quality_score_avg" in result.stdout


def test_repository_alert_rules_are_valid() -> None:
    result = run_validator(REPO_ROOT / "config" / "dashboard.yaml")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Alert rules" in result.stdout


def test_validator_rejects_alert_rule_still_todo(tmp_path: Path) -> None:
    payload = yaml.safe_load(
        (REPO_ROOT / "config" / "alert_rules.yaml").read_text(encoding="utf-8")
    )
    payload["alerts"][0]["severity"] = "TODO"
    invalid_alerts = tmp_path / "alert_rules.yaml"
    invalid_alerts.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    result = run_validator(
        REPO_ROOT / "config" / "dashboard.yaml", alerts_config=invalid_alerts
    )

    assert result.returncode == 1
    assert "TODO" in result.stdout
