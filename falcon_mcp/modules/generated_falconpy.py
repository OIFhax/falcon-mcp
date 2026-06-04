"""Generated all-operation modules for FalconPy service collections not hand-wrapped yet."""

from __future__ import annotations

import importlib
from typing import Any

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.falconpy_operations import (
    FalconPyOperationsBase,
    build_tool_specs,
    display_name_from_module_key,
)

logger = get_logger(__name__)

GENERATED_SERVICE_COLLECTIONS: tuple[str, ...] = (
    "admission_control_policies",
    "alerts",
    "aspm",
    "cloud_policies",
    "cloud_security_assets",
    "cloud_security_compliance",
    "cloud_security_detections",
    "cloud_snapshots",
    "configuration_assessment",
    "configuration_assessment_evaluation_logic",
    "container_alerts",
    "container_detections",
    "container_image_compliance",
    "container_images",
    "container_packages",
    "container_vulnerabilities",
    "correlation_rules_admin",
    "cspm_registration",
    "custom_storage",
    "d4c_registration",
    "data_protection_configuration",
    "faas_execution",
    "falcon_complete_dashboard",
    "falcon_container",
    "falconx_sandbox",
    "filevantage",
    "foundry_logscale",
    "image_assessment_policies",
    "intelligence_indicator_graph",
    "iocs",
    "kubernetes_container_compliance",
    "kubernetes_protection",
    "mobile_enrollment",
    "network_scan_global_configs",
    "network_scan_networks",
    "network_scan_scan_run_reports",
    "network_scan_scan_runs",
    "network_scan_scanners",
    "network_scan_scans",
    "network_scan_templates",
    "network_scan_zones",
    "ods",
    "recon",
    "report_executions",
    "saas_security",
    "sample_uploads",
    "tailored_intelligence",
    "unidentified_containers",
)

__all__: list[str] = []


def _module_key_to_class_name(module_key: str) -> str:
    return "".join(part.capitalize() for part in module_key.split("_")) + "Module"


def _load_endpoints(module_key: str) -> list[list[Any]]:
    falconpy_module = importlib.import_module(f"falconpy.{module_key}")
    endpoints = getattr(falconpy_module, "Endpoints")
    if not isinstance(endpoints, list):
        raise TypeError(f"FalconPy {module_key} Endpoints is not a list")
    return endpoints


def _build_generated_module(module_key: str) -> type[FalconPyOperationsBase]:
    tool_specs = build_tool_specs(module_key=module_key, endpoints=_load_endpoints(module_key))
    return type(
        _module_key_to_class_name(module_key),
        (FalconPyOperationsBase,),
        {
            "__module__": __name__,
            "MODULE_KEY": module_key,
            "MODULE_DISPLAY_NAME": display_name_from_module_key(module_key),
            "TOOL_SPECS": tool_specs,
        },
    )


for _module_key in GENERATED_SERVICE_COLLECTIONS:
    try:
        _module_class = _build_generated_module(_module_key)
    except Exception as exc:
        logger.warning(
            "Skipping generated FalconPy module %s: %s",
            _module_key,
            exc,
        )
        continue

    globals()[_module_class.__name__] = _module_class
    __all__.append(_module_class.__name__)
