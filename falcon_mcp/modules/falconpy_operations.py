"""Reusable generated FalconPy operation wrappers."""

from __future__ import annotations

import base64
import binascii
import re
from typing import Any, Callable

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


READ_OPERATION_PREFIXES = (
    "aggregate",
    "combined",
    "count",
    "download",
    "export",
    "get",
    "list",
    "postaggregates",
    "postcombined",
    "postentities",
    "query",
    "read",
    "retrieve",
    "search",
)

WRITE_OPERATION_PREFIXES = (
    "add",
    "assign",
    "cancel",
    "clone",
    "create",
    "delete",
    "execute",
    "import",
    "ingest",
    "patch",
    "populate",
    "post",
    "put",
    "remove",
    "retry",
    "run",
    "set",
    "signal",
    "start",
    "stop",
    "submit",
    "update",
    "upload",
    "upsert",
)


def operation_to_snake(operation: str) -> str:
    """Convert FalconPy operation IDs into stable MCP-friendly suffixes."""
    normalized = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", operation)
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", normalized)
    normalized = normalized.strip("_").lower()
    return normalized or "operation"


def display_name_from_module_key(module_key: str) -> str:
    """Create a human-readable display name from a FalconPy module name."""
    return module_key.replace("_", " ").title()


def field_default(value: Any) -> Any:
    """Resolve direct-call pydantic Field defaults."""
    return value.default if isinstance(value, FieldInfo) else value


def classify_operation_kind(endpoint: list[Any]) -> str:
    """Classify an endpoint into a generic MCP invocation kind."""
    method = str(endpoint[1]).upper()
    params = endpoint[5] if len(endpoint) > 5 and isinstance(endpoint[5], list) else []
    has_body = any(param.get("in") == "body" for param in params if isinstance(param, dict))
    has_form_data = any(param.get("in") == "formData" for param in params if isinstance(param, dict))
    has_file = any(
        param.get("in") == "formData" and param.get("type") == "file"
        for param in params
        if isinstance(param, dict)
    )
    has_parameters = any(
        param.get("in") in {"query", "path", "header"}
        for param in params
        if isinstance(param, dict)
    )

    if has_file or has_form_data:
        return "multipart"
    if has_body and has_parameters:
        return "params_body"
    if has_body:
        return "body"
    if method == "GET":
        return "params"
    return "params"


def is_write_operation(endpoint: list[Any]) -> bool:
    """Infer whether an endpoint mutates Falcon state."""
    method = str(endpoint[1]).upper()
    if method in {"DELETE", "PATCH", "PUT"}:
        return True
    if method == "GET":
        return False

    operation = str(endpoint[0])
    normalized = operation_to_snake(operation).replace("_", "")
    if normalized.startswith(READ_OPERATION_PREFIXES):
        return False
    return normalized.startswith(WRITE_OPERATION_PREFIXES)


def build_tool_specs(module_key: str, endpoints: list[list[Any]]) -> list[dict[str, Any]]:
    """Build generic tool specifications from a FalconPy Endpoints collection."""
    specs: list[dict[str, Any]] = []
    seen_tool_names: set[str] = set()

    for endpoint in endpoints:
        operation = str(endpoint[0])
        method = str(endpoint[1]).upper()
        params = endpoint[5] if len(endpoint) > 5 and isinstance(endpoint[5], list) else []
        kind = classify_operation_kind(endpoint)
        is_write = is_write_operation(endpoint)
        is_destructive = method == "DELETE" or operation_to_snake(operation).startswith(
            ("delete_", "remove_")
        )
        tool_base = f"{module_key}_{operation_to_snake(operation)}"
        tool_name = tool_base
        suffix = 2
        while tool_name in seen_tool_names:
            tool_name = f"{tool_base}_{suffix}"
            suffix += 1
        seen_tool_names.add(tool_name)

        specs.append(
            {
                "tool_name": tool_name,
                "operation": operation,
                "method": method,
                "path": str(endpoint[2]),
                "description": str(endpoint[3] or ""),
                "kind": kind,
                "has_body": any(
                    param.get("in") == "body" for param in params if isinstance(param, dict)
                ),
                "body_required": any(
                    param.get("in") == "body" and param.get("required")
                    for param in params
                    if isinstance(param, dict)
                ),
                "has_form_data": any(
                    param.get("in") == "formData" for param in params if isinstance(param, dict)
                ),
                "file_required": any(
                    param.get("in") == "formData"
                    and param.get("type") == "file"
                    and param.get("required")
                    for param in params
                    if isinstance(param, dict)
                ),
                "annotations": (
                    DESTRUCTIVE_WRITE_ANNOTATIONS
                    if is_destructive
                    else WRITE_ANNOTATIONS
                    if is_write
                    else None
                ),
            }
        )

    return specs


class FalconPyOperationsBase(BaseModule):
    """Base class for generated all-operation FalconPy service collection modules."""

    MODULE_KEY = "falconpy"
    MODULE_DISPLAY_NAME = "FalconPy"
    TOOL_SPECS: list[dict[str, Any]] = []

    def __init__(self, client: Any):
        super().__init__(client)
        self._build_generated_tools()

    def _build_generated_tools(self) -> None:
        for spec in self.TOOL_SPECS:
            setattr(self, spec["tool_name"], self._make_operation_tool(spec))

    def register_tools(self, server: FastMCP) -> None:
        for spec in self.TOOL_SPECS:
            self._add_tool(
                server=server,
                method=getattr(self, spec["tool_name"]),
                name=spec["tool_name"],
                annotations=spec["annotations"],
            )

    def register_resources(self, server: FastMCP) -> None:
        resource_key = self.MODULE_KEY.replace("_", "-")
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl(f"falcon://{resource_key}/operations-guide"),
                name=f"falcon_{self.MODULE_KEY}_operations_guide",
                description=f"Operation guide for Falcon {self.MODULE_DISPLAY_NAME}.",
                text=self._build_operations_guide(),
            ),
        )

    def _make_operation_tool(self, spec: dict[str, Any]) -> Callable[..., Any]:
        operation = spec["operation"]

        def tool(
            parameters: dict[str, Any] | None = Field(
                default=None,
                description="FalconPy query, path, or header parameters for this operation.",
            ),
            body: dict[str, Any] | list[dict[str, Any]] | None = Field(
                default=None,
                description="FalconPy JSON body payload for this operation.",
            ),
            form_data: dict[str, Any] | None = Field(
                default=None,
                description="Form-data fields for multipart FalconPy operations.",
            ),
            file_name: str | None = Field(
                default=None,
                description="Logical file name for multipart upload operations.",
            ),
            file_data_base64: str | None = Field(
                default=None,
                description="Base64-encoded file content for multipart upload operations.",
            ),
            file_field: str | None = Field(
                default=None,
                description="Optional multipart file field name. Defaults to `file`.",
            ),
            include_binary_base64: bool = Field(
                default=False,
                description="Include base64 response content for binary Falcon responses.",
            ),
            max_inline_bytes: int = Field(
                default=2_000_000,
                ge=1,
                le=20_000_000,
                description="Maximum binary response size to include inline as base64.",
            ),
        ) -> Any:
            parameters = field_default(parameters)
            body = field_default(body)
            form_data = field_default(form_data)
            file_name = field_default(file_name)
            file_data_base64 = field_default(file_data_base64)
            file_field = field_default(file_field)
            include_binary_base64 = field_default(include_binary_base64)
            max_inline_bytes = field_default(max_inline_bytes)

            if spec["body_required"] and body is None:
                return [
                    _format_error_response(
                        "Provide `body` to execute this FalconPy operation.",
                        operation=operation,
                    )
                ]
            if spec["file_required"] and not file_data_base64:
                return [
                    _format_error_response(
                        "Provide `file_data_base64` to execute this FalconPy file operation.",
                        operation=operation,
                    )
                ]

            call_args = self._build_call_args(
                parameters=parameters,
                body=body,
                form_data=form_data,
                file_name=file_name,
                file_data_base64=file_data_base64,
                file_field=file_field,
                operation=operation,
            )
            if isinstance(call_args, dict) and "error" in call_args:
                return [call_args]

            response = self.client.command(operation, **call_args)
            return self._handle_operation_response(
                response=response,
                operation=operation,
                include_binary_base64=include_binary_base64,
                max_inline_bytes=max_inline_bytes,
            )

        tool.__name__ = f"{operation_to_snake(operation)}_tool"
        tool.__doc__ = self._build_tool_docstring(spec)
        return tool

    def _build_call_args(
        self,
        *,
        parameters: dict[str, Any] | None,
        body: dict[str, Any] | list[dict[str, Any]] | None,
        form_data: dict[str, Any] | None,
        file_name: str | None,
        file_data_base64: str | None,
        file_field: str | None,
        operation: str,
    ) -> dict[str, Any]:
        call_args: dict[str, Any] = {}
        prepared_parameters = dict(parameters or {})

        if form_data:
            prepared_parameters.update(form_data)

        if prepared_parameters:
            call_args["parameters"] = prepare_api_parameters(prepared_parameters)

        if body is not None:
            call_args["body"] = prepare_api_parameters(body) if isinstance(body, dict) else body

        if file_data_base64:
            try:
                file_bytes = base64.b64decode(file_data_base64, validate=True)
            except (ValueError, binascii.Error):
                return _format_error_response(
                    "`file_data_base64` must be valid base64-encoded content.",
                    operation=operation,
                )

            field_name = file_field or "file"
            upload_name = file_name or f"{operation_to_snake(operation)}.bin"
            call_args["files"] = [(field_name, (upload_name, file_bytes))]

        return call_args

    def _handle_operation_response(
        self,
        *,
        response: Any,
        operation: str,
        include_binary_base64: bool,
        max_inline_bytes: int,
    ) -> Any:
        if isinstance(response, bytes):
            result: dict[str, Any] = {
                "operation": operation,
                "binary_response": True,
                "size_bytes": len(response),
            }
            if include_binary_base64:
                if len(response) > max_inline_bytes:
                    return [
                        _format_error_response(
                            "Binary response exceeds `max_inline_bytes`.",
                            details={"size_bytes": len(response), "max_inline_bytes": max_inline_bytes},
                            operation=operation,
                        )
                    ]
                result["binary_base64"] = base64.b64encode(response).decode("ascii")
            return [result]

        if not isinstance(response, dict):
            return [
                {
                    "operation": operation,
                    "raw_response_type": type(response).__name__,
                    "raw_response": str(response),
                }
            ]

        result = handle_api_response(
            response,
            operation=operation,
            error_message=f"Failed to execute {operation}",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def _build_tool_docstring(self, spec: dict[str, Any]) -> str:
        description = spec["description"].strip() or f"Execute FalconPy operation {spec['operation']}."
        return (
            f"{description}\n\n"
            f"FalconPy operation: {spec['operation']}\n"
            f"HTTP method: {spec['method']}\n"
            f"Path: {spec['path']}"
        )

    def _build_operations_guide(self) -> str:
        lines = [
            f"# Falcon {self.MODULE_DISPLAY_NAME} Operations",
            "",
            "This generated module exposes every FalconPy operation for this service collection.",
            "Risk level does not gate tool availability; use API scopes and separate MCP instances to control access.",
            "",
            "Pass FalconPy query, path, and header values through `parameters`.",
            "Pass JSON request bodies through `body`.",
            "For multipart uploads, provide `file_data_base64`, optional `file_name`, optional `file_field`, and any extra `form_data`.",
            "",
            "| Tool | Operation | Method | Path |",
            "|---|---|---|---|",
        ]
        for spec in self.TOOL_SPECS:
            lines.append(
                f"| `falcon_{spec['tool_name']}` | `{spec['operation']}` | "
                f"`{spec['method']}` | `{spec['path']}` |"
            )
        return "\n".join(lines)
