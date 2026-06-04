"""Generated raw wrappers for FalconPy operations not covered by hand modules."""

from __future__ import annotations

import ast
from importlib.resources import files
from pathlib import Path
from typing import Any

from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.falconpy_operations import (
    FalconPyOperationsBase,
    build_tool_specs,
    display_name_from_module_key,
)
from falcon_mcp.modules.generated_falconpy import GENERATED_SERVICE_COLLECTIONS

logger = get_logger(__name__)

RAW_MODULE_PREFIX = "raw"
__all__: list[str] = []


def _module_key_to_class_name(module_key: str) -> str:
    return "Raw" + "".join(part.capitalize() for part in module_key.split("_")) + "Module"


def _load_endpoint_module_keys() -> list[str]:
    endpoint_keys: list[str] = []
    endpoint_dir = files("falconpy._endpoint")
    for endpoint_file in endpoint_dir.iterdir():
        name = endpoint_file.name
        if not name.startswith("_") or not name.endswith(".py") or name == "__init__.py":
            continue
        endpoint_keys.append(name[1:-3])
    return sorted(endpoint_keys)


def _load_endpoints(module_key: str) -> list[list[Any]]:
    endpoint_file = files("falconpy._endpoint").joinpath(f"_{module_key}.py")
    endpoint_source = endpoint_file.read_text(encoding="utf-8")
    endpoint_tree = ast.parse(endpoint_source)
    for node in endpoint_tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.endswith("_endpoints"):
                endpoints = ast.literal_eval(node.value)
                if not isinstance(endpoints, list):
                    raise TypeError(f"FalconPy {module_key} Endpoints is not a list")
                return endpoints
    raise TypeError(f"FalconPy {module_key} Endpoints was not found")


def _operation_is_covered(operation: str) -> bool:
    modules_dir = Path(__file__).parent
    for module_file in modules_dir.glob("*.py"):
        if module_file.name == Path(__file__).name:
            continue
        try:
            source = module_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if repr(operation) in source or f'"{operation}"' in source:
            return True
    return False


def _build_raw_gap_module(module_key: str) -> type[FalconPyOperationsBase] | None:
    if module_key in GENERATED_SERVICE_COLLECTIONS:
        return None

    try:
        endpoints = _load_endpoints(module_key)
    except Exception as exc:
        logger.debug("Skipping raw FalconPy gap module %s: %s", module_key, exc)
        return None

    missing_endpoints = [
        endpoint
        for endpoint in endpoints
        if endpoint and not _operation_is_covered(str(endpoint[0]))
    ]
    if not missing_endpoints:
        return None

    raw_module_key = f"{RAW_MODULE_PREFIX}_{module_key}"
    tool_specs = build_tool_specs(module_key=raw_module_key, endpoints=missing_endpoints)
    return type(
        _module_key_to_class_name(module_key),
        (FalconPyOperationsBase,),
        {
            "__module__": __name__,
            "MODULE_KEY": raw_module_key,
            "MODULE_DISPLAY_NAME": f"Raw {display_name_from_module_key(module_key)}",
            "TOOL_SPECS": tool_specs,
        },
    )


for _module_key in _load_endpoint_module_keys():
    _module_class = _build_raw_gap_module(_module_key)
    if _module_class is None:
        continue

    globals()[_module_class.__name__] = _module_class
    __all__.append(_module_class.__name__)
