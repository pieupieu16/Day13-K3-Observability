from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.cli import configure_utf8_stdio


REQUIRED_PANEL_IDS = frozenset(
    {"latency", "traffic", "errors", "cost", "tokens", "quality"}
)
REQUIRED_PANEL_FIELDS = (
    "title",
    "source",
    "events",
    "fields",
    "aggregations",
    "query",
    "unit",
    "threshold",
)

REQUIRED_SLO_IDS = frozenset(
    {"latency_p95_ms", "error_rate_pct", "daily_cost_usd", "quality_score_avg"}
)
ALLOWED_ALERT_SEVERITIES = frozenset({"info", "warning", "critical"})
REQUIRED_ALERT_FIELDS = ("name", "severity", "condition", "type", "owner", "runbook")


class DashboardConfigError(ValueError):
    pass


class SloConfigError(ValueError):
    pass


class AlertRulesError(ValueError):
    pass


def load_dashboard_config(path: Path) -> dict:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DashboardConfigError(f"Không tìm thấy dashboard config: {path}") from exc
    except yaml.YAMLError as exc:
        raise DashboardConfigError(f"Dashboard config không phải YAML hợp lệ: {exc}") from exc

    dashboard = payload.get("dashboard") if isinstance(payload, dict) else None
    if not isinstance(dashboard, dict):
        raise DashboardConfigError("Thiếu object 'dashboard'")
    if dashboard.get("schema_version") != 1:
        raise DashboardConfigError("'dashboard.schema_version' phải bằng 1")
    if dashboard.get("time_range_minutes") != 60:
        raise DashboardConfigError("'dashboard.time_range_minutes' phải bằng 60")
    refresh_seconds = dashboard.get("refresh_seconds")
    if not isinstance(refresh_seconds, int) or not 15 <= refresh_seconds <= 30:
        raise DashboardConfigError("'dashboard.refresh_seconds' phải nằm trong khoảng 15–30")

    panels = dashboard.get("panels")
    if not isinstance(panels, list) or len(panels) != 6:
        raise DashboardConfigError("Dashboard phải có đúng 6 panel")
    panel_ids = {
        panel.get("id") for panel in panels if isinstance(panel, dict) and panel.get("id")
    }
    if panel_ids != REQUIRED_PANEL_IDS:
        missing = ", ".join(sorted(REQUIRED_PANEL_IDS - panel_ids)) or "không"
        extra = ", ".join(sorted(panel_ids - REQUIRED_PANEL_IDS)) or "không"
        raise DashboardConfigError(
            f"Panel ID không đúng; thiếu: {missing}; không hỗ trợ: {extra}"
        )

    for panel in panels:
        if not isinstance(panel, dict):
            raise DashboardConfigError("Mỗi dashboard panel phải là một YAML object")
        panel_id = panel["id"]
        for field in REQUIRED_PANEL_FIELDS:
            if panel.get(field) in (None, "", []):
                raise DashboardConfigError(f"Thiếu hoặc rỗng: {panel_id}.{field}")
        if not all(isinstance(panel[field], list) for field in ("events", "fields", "aggregations")):
            raise DashboardConfigError(
                f"'{panel_id}.events/fields/aggregations' phải là danh sách"
            )

        threshold = panel["threshold"]
        if not isinstance(threshold, dict):
            raise DashboardConfigError(f"'{panel_id}.threshold' phải là một YAML object")
        if threshold.get("aggregation") not in panel["aggregations"]:
            raise DashboardConfigError(
                f"'{panel_id}.threshold.aggregation' phải thuộc aggregations của panel"
            )
        if threshold.get("operator") not in {"lte", "gte"}:
            raise DashboardConfigError(
                f"'{panel_id}.threshold.operator' chỉ nhận 'lte' hoặc 'gte'"
            )
        if not isinstance(threshold.get("value"), (int, float)):
            raise DashboardConfigError(f"'{panel_id}.threshold.value' phải là một số")

    return payload


def load_slo_config(path: Path) -> dict:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SloConfigError(f"Không tìm thấy SLO config: {path}") from exc
    except yaml.YAMLError as exc:
        raise SloConfigError(f"SLO config không phải YAML hợp lệ: {exc}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("slis"), dict):
        raise SloConfigError("Thiếu object 'slis'")
    service = payload.get("service")
    if not isinstance(service, str) or not service.strip():
        raise SloConfigError("'service' phải là chuỗi không rỗng")
    window = payload.get("window")
    if not isinstance(window, str) or not window.strip():
        raise SloConfigError("'window' phải là chuỗi không rỗng")

    slis = payload["slis"]
    sli_ids = set(slis)
    if sli_ids != REQUIRED_SLO_IDS:
        missing = ", ".join(sorted(REQUIRED_SLO_IDS - sli_ids)) or "không"
        extra = ", ".join(sorted(sli_ids - REQUIRED_SLO_IDS)) or "không"
        raise SloConfigError(f"SLI không đúng; thiếu: {missing}; không hỗ trợ: {extra}")

    for sli_id, spec in slis.items():
        if not isinstance(spec, dict):
            raise SloConfigError(f"'slis.{sli_id}' phải là một YAML object")
        if not isinstance(spec.get("objective"), (int, float)):
            raise SloConfigError(f"'slis.{sli_id}.objective' phải là một số")
        target = spec.get("target")
        if not isinstance(target, (int, float)) or not 0 < target <= 100:
            raise SloConfigError(f"'slis.{sli_id}.target' phải nằm trong khoảng 0–100")

    return payload


def load_alert_rules(path: Path) -> dict:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AlertRulesError(f"Không tìm thấy alert rules: {path}") from exc
    except yaml.YAMLError as exc:
        raise AlertRulesError(f"Alert rules không phải YAML hợp lệ: {exc}") from exc

    alerts = payload.get("alerts") if isinstance(payload, dict) else None
    if not isinstance(alerts, list) or not alerts:
        raise AlertRulesError("'alerts' phải là danh sách không rỗng")

    for index, alert in enumerate(alerts):
        if not isinstance(alert, dict):
            raise AlertRulesError(f"alerts[{index}] phải là một YAML object")
        for field in REQUIRED_ALERT_FIELDS:
            value = alert.get(field)
            if not isinstance(value, str) or not value.strip() or "TODO" in value:
                raise AlertRulesError(f"alerts[{index}].{field} bị thiếu hoặc vẫn là TODO")
        if alert["severity"] not in ALLOWED_ALERT_SEVERITIES:
            raise AlertRulesError(
                f"alerts[{index}].severity chỉ nhận 'info', 'warning' hoặc 'critical'"
            )

    return payload


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Kiểm tra dashboard contract của Day 13")
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "config" / "dashboard.yaml",
        help="Đường dẫn tới dashboard YAML",
    )
    parser.add_argument(
        "--slo-config",
        type=Path,
        default=REPO_ROOT / "config" / "slo.yaml",
        help="Đường dẫn tới SLO YAML",
    )
    parser.add_argument(
        "--alerts-config",
        type=Path,
        default=REPO_ROOT / "config" / "alert_rules.yaml",
        help="Đường dẫn tới alert rules YAML",
    )
    args = parser.parse_args()

    dashboard_ok = True
    try:
        load_dashboard_config(args.config)
    except DashboardConfigError as exc:
        dashboard_ok = False
        print(f"KHÔNG HỢP LỆ dashboard: {exc}")

    slo_ok = True
    try:
        load_slo_config(args.slo_config)
    except SloConfigError as exc:
        slo_ok = False
        print(f"KHÔNG HỢP LỆ slo: {exc}")

    alerts_ok = True
    try:
        load_alert_rules(args.alerts_config)
    except AlertRulesError as exc:
        alerts_ok = False
        print(f"KHÔNG HỢP LỆ alerts: {exc}")

    if not (dashboard_ok and slo_ok and alerts_ok):
        return 1

    print(f"HỢP LỆ: {len(REQUIRED_PANEL_IDS)}/6 panel có trong dashboard contract.")
    print("HỢP LỆ: SLO config.")
    print("HỢP LỆ: Alert rules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
