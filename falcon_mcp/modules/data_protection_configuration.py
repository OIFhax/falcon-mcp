"""
Data Protection Configuration module for Falcon MCP Server.

This module wraps FalconPy's DataProtectionConfiguration service collection with
read/write tools for Falcon Data Protection policy, classification, and DLP
supporting configuration objects.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.data_protection_configuration import (
    DATA_PROTECTION_CONFIGURATION_GUIDE,
    DATA_PROTECTION_CONFIGURATION_SAFETY_GUIDE,
)

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

DataProtectionResourceType = Literal[
    "classification",
    "cloud_application",
    "content_pattern",
    "enterprise_account",
    "file_type",
    "sensitivity_label",
    "local_application_group",
    "local_application",
    "policy",
    "web_location",
]

_RESOURCE_OPERATIONS: dict[str, dict[str, str | None]] = {
    "classification": {
        "query": "queries_classification_get_v2",
        "get": "entities_classification_get_v2",
        "create": "entities_classification_post_v2",
        "update": "entities_classification_patch_v2",
        "delete": "entities_classification_delete_v2",
    },
    "cloud_application": {
        "query": "queries_cloud_application_get_v2",
        "get": "entities_cloud_application_get",
        "create": "entities_cloud_application_create",
        "update": "entities_cloud_application_patch",
        "delete": "entities_cloud_application_delete",
    },
    "content_pattern": {
        "query": "queries_content_pattern_get_v2",
        "get": "entities_content_pattern_get",
        "create": "entities_content_pattern_create",
        "update": "entities_content_pattern_patch",
        "delete": "entities_content_pattern_delete",
    },
    "enterprise_account": {
        "query": "queries_enterprise_account_get_v2",
        "get": "entities_enterprise_account_get",
        "create": "entities_enterprise_account_create",
        "update": "entities_enterprise_account_patch",
        "delete": "entities_enterprise_account_delete",
    },
    "file_type": {
        "query": "queries_file_type_get_v2",
        "get": "entities_file_type_get",
        "create": None,
        "update": None,
        "delete": None,
    },
    "sensitivity_label": {
        "query": "queries_sensitivity_label_get_v2",
        "get": "entities_sensitivity_label_get_v2",
        "create": "entities_sensitivity_label_create_v2",
        "update": None,
        "delete": "entities_sensitivity_label_delete_v2",
    },
    "local_application_group": {
        "query": "queries_local_application_group_get",
        "get": "entities_local_application_group_get",
        "create": "entities_local_application_group_create",
        "update": "entities_local_application_group_patch",
        "delete": "entities_local_application_group_delete",
    },
    "local_application": {
        "query": "queries_local_application_get",
        "get": "entities_local_application_get",
        "create": "entities_local_application_create",
        "update": "entities_local_application_patch",
        "delete": "entities_local_application_delete",
    },
    "policy": {
        "query": "queries_policy_get_v2",
        "get": "entities_policy_get_v2",
        "create": "entities_policy_post_v2",
        "update": "entities_policy_patch_v2",
        "delete": "entities_policy_delete_v2",
    },
    "web_location": {
        "query": "queries_web_location_get_v2",
        "get": "entities_web_location_get_v2",
        "create": "entities_web_location_create_v2",
        "update": "entities_web_location_patch_v2",
        "delete": "entities_web_location_delete_v2",
    },
}


class DataProtectionConfigurationModule(BaseModule):
    """Module for Falcon Data Protection Configuration operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server, self.query_data_protection_resources, "query_data_protection_resources")
        self._add_tool(server, self.get_data_protection_resources, "get_data_protection_resources")
        self._add_tool(
            server,
            self.create_data_protection_resource,
            "create_data_protection_resource",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.update_data_protection_resource,
            "update_data_protection_resource",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.delete_data_protection_resources,
            "delete_data_protection_resources",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

        self._add_tool(server, self.query_data_protection_policy_ids, "query_data_protection_policy_ids")
        self._add_tool(server, self.get_data_protection_policies, "get_data_protection_policies")
        self._add_tool(
            server,
            self.create_data_protection_policy,
            "create_data_protection_policy",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.update_data_protection_policy,
            "update_data_protection_policy",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.delete_data_protection_policies,
            "delete_data_protection_policies",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.set_data_protection_policy_precedence,
            "set_data_protection_policy_precedence",
            annotations=WRITE_ANNOTATIONS,
        )

        self._add_tool(
            server,
            self.query_data_protection_classification_ids,
            "query_data_protection_classification_ids",
        )
        self._add_tool(
            server,
            self.get_data_protection_classifications,
            "get_data_protection_classifications",
        )
        self._add_tool(
            server,
            self.create_data_protection_classification,
            "create_data_protection_classification",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.update_data_protection_classifications,
            "update_data_protection_classifications",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.delete_data_protection_classifications,
            "delete_data_protection_classifications",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

        self._add_tool(
            server,
            self.query_data_protection_content_pattern_ids,
            "query_data_protection_content_pattern_ids",
        )
        self._add_tool(
            server,
            self.get_data_protection_content_patterns,
            "get_data_protection_content_patterns",
        )
        self._add_tool(
            server,
            self.create_data_protection_content_pattern,
            "create_data_protection_content_pattern",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.update_data_protection_content_pattern,
            "update_data_protection_content_pattern",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.delete_data_protection_content_patterns,
            "delete_data_protection_content_patterns",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

        self._register_resource_family_tools(
            server,
            "cloud_application",
            self.query_data_protection_cloud_application_ids,
            self.get_data_protection_cloud_applications,
            self.create_data_protection_cloud_application,
            self.update_data_protection_cloud_application,
            self.delete_data_protection_cloud_applications,
        )
        self._register_resource_family_tools(
            server,
            "enterprise_account",
            self.query_data_protection_enterprise_account_ids,
            self.get_data_protection_enterprise_accounts,
            self.create_data_protection_enterprise_account,
            self.update_data_protection_enterprise_account,
            self.delete_data_protection_enterprise_accounts,
        )
        self._add_tool(
            server,
            self.query_data_protection_file_type_ids,
            "query_data_protection_file_type_ids",
        )
        self._add_tool(
            server,
            self.get_data_protection_file_types,
            "get_data_protection_file_types",
        )
        self._add_tool(
            server,
            self.query_data_protection_sensitivity_label_ids,
            "query_data_protection_sensitivity_label_ids",
        )
        self._add_tool(
            server,
            self.get_data_protection_sensitivity_labels,
            "get_data_protection_sensitivity_labels",
        )
        self._add_tool(
            server,
            self.create_data_protection_sensitivity_label,
            "create_data_protection_sensitivity_label",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.delete_data_protection_sensitivity_labels,
            "delete_data_protection_sensitivity_labels",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._register_resource_family_tools(
            server,
            "local_application_group",
            self.query_data_protection_local_application_group_ids,
            self.get_data_protection_local_application_groups,
            self.create_data_protection_local_application_group,
            self.update_data_protection_local_application_group,
            self.delete_data_protection_local_application_groups,
        )
        self._register_resource_family_tools(
            server,
            "local_application",
            self.query_data_protection_local_application_ids,
            self.get_data_protection_local_applications,
            self.create_data_protection_local_application,
            self.update_data_protection_local_application,
            self.delete_data_protection_local_applications,
        )
        self._register_resource_family_tools(
            server,
            "web_location",
            self.query_data_protection_web_location_ids,
            self.get_data_protection_web_locations,
            self.create_data_protection_web_location,
            self.update_data_protection_web_location,
            self.delete_data_protection_web_locations,
        )

    def _register_resource_family_tools(
        self,
        server: FastMCP,
        resource_slug: str,
        query_method: Any,
        get_method: Any,
        create_method: Any,
        update_method: Any,
        delete_method: Any,
    ) -> None:
        self._add_tool(
            server,
            query_method,
            f"query_data_protection_{resource_slug}_ids",
        )
        self._add_tool(
            server,
            get_method,
            f"get_data_protection_{resource_slug}s",
        )
        self._add_tool(
            server,
            create_method,
            f"create_data_protection_{resource_slug}",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            update_method,
            f"update_data_protection_{resource_slug}",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            delete_method,
            f"delete_data_protection_{resource_slug}s",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP Server."""
        config_guide = TextResource(
            uri=AnyUrl("falcon://data-protection-configuration/guide"),
            name="falcon_data_protection_configuration_guide",
            description="Guidance for Falcon Data Protection Configuration tools.",
            text=DATA_PROTECTION_CONFIGURATION_GUIDE,
        )
        safety_guide = TextResource(
            uri=AnyUrl("falcon://data-protection-configuration/safety-guide"),
            name="falcon_data_protection_configuration_safety_guide",
            description="Safety guidance for Falcon Data Protection Configuration write tools.",
            text=DATA_PROTECTION_CONFIGURATION_SAFETY_GUIDE,
        )
        self._add_resource(server, config_guide)
        self._add_resource(server, safety_guide)

    def query_data_protection_resources(
        self,
        resource_type: DataProtectionResourceType = Field(
            description="Data Protection resource type to query.",
        ),
        filter: str | None = Field(default=None, description="Optional resource-specific FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default=None, description="Optional sort expression."),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Additional query parameters such as platform_name or type.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection Configuration resource IDs."""
        operation = _operation_for(resource_type, "query")
        query_params = _merge_parameters(
            parameters,
            {
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
        )
        result = self._base_query_api_call(
            operation=operation,
            query_params=query_params,
            error_message=f"Failed to query Data Protection {resource_type} IDs",
            default_result=[],
        )
        return [result] if self._is_error(result) else result

    def get_data_protection_resources(
        self,
        resource_type: DataProtectionResourceType = Field(
            description="Data Protection resource type to retrieve.",
        ),
        ids: list[str] | None = Field(default=None, description="Resource IDs to retrieve."),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Additional query parameters such as platform_name.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection Configuration resources by ID."""
        operation = _operation_for(resource_type, "get")
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve Data Protection resources.",
                    operation=operation,
                )
            ]
        query_params = _merge_parameters(parameters, {"ids": ids})
        result = self._base_query_api_call(
            operation=operation,
            query_params=query_params,
            error_message=f"Failed to retrieve Data Protection {resource_type} resources",
            default_result=[],
        )
        return [result] if self._is_error(result) else result

    def create_data_protection_resource(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        resource_type: DataProtectionResourceType = Field(
            description="Data Protection resource type to create.",
        ),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Additional query parameters such as platform_name.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection Configuration resource with an explicit body."""
        return self._write_resource_operation(
            "create",
            resource_type,
            confirm_execution=confirm_execution,
            query_params=parameters,
            body=body,
            body_required=True,
        )

    def update_data_protection_resource(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        resource_type: DataProtectionResourceType = Field(
            description="Data Protection resource type to update.",
        ),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Additional query parameters such as id or platform_name.",
        ),
    ) -> list[dict[str, Any]]:
        """Update a Data Protection Configuration resource with an explicit body."""
        return self._write_resource_operation(
            "update",
            resource_type,
            confirm_execution=confirm_execution,
            query_params=parameters,
            body=body,
            body_required=True,
        )

    def delete_data_protection_resources(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        resource_type: DataProtectionResourceType = Field(
            description="Data Protection resource type to delete.",
        ),
        ids: list[str] | None = Field(default=None, description="Resource IDs to delete."),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Additional query parameters such as platform_name.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection Configuration resources."""
        operation = _operation_for(resource_type, "delete")
        if not confirm_execution:
            return [_format_error_response("This operation requires `confirm_execution=true`.", operation=operation)]
        if not ids:
            return [_format_error_response("`ids` is required for delete operations.", operation=operation)]
        query_params = _merge_parameters(parameters, {"ids": ids})
        result = self._base_query_api_call(
            operation=operation,
            query_params=query_params,
            error_message=f"Failed to delete Data Protection {resource_type} resources",
            default_result=[],
        )
        return [result] if self._is_error(result) else result

    def query_data_protection_policy_ids(
        self,
        platform_name: Literal["win", "mac"] = Field(description="Policy platform name: `win` or `mac`."),
        filter: str | None = Field(default=None, description="Optional policy FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="precedence.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection policy IDs."""
        return self.query_data_protection_resources(
            resource_type="policy",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            parameters={"platform_name": platform_name},
        )

    def get_data_protection_policies(
        self,
        ids: list[str] | None = Field(default=None, description="Policy IDs to retrieve."),
        platform_name: Literal["win", "mac"] | None = Field(
            default=None,
            description="Optional policy platform name.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection policies by ID."""
        parameters = {"platform_name": platform_name} if platform_name else None
        return self.get_data_protection_resources("policy", ids=ids, parameters=parameters)

    def create_data_protection_policy(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        platform_name: Literal["win", "mac"] = Field(description="Policy platform name: `win` or `mac`."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
        name: str | None = Field(default=None, description="Policy name."),
        description: str | None = Field(default=None, description="Policy description."),
        policy_properties: dict[str, Any] | None = Field(default=None, description="Policy properties."),
        precedence: int | None = Field(default=None, description="Policy precedence."),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection policy."""
        request_body = body or _resource_body(
            {
                "name": name,
                "description": description,
                "policy_properties": policy_properties,
                "precedence": precedence,
            }
        )
        if request_body is None:
            return [
                _format_error_response(
                    "`body` or at least one policy field is required.",
                    operation="entities_policy_post_v2",
                )
            ]
        return self._write_resource_operation(
            "create",
            "policy",
            confirm_execution=confirm_execution,
            query_params={"platform_name": platform_name},
            body=request_body,
            body_required=True,
        )

    def update_data_protection_policy(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        platform_name: Literal["win", "mac"] = Field(description="Policy platform name: `win` or `mac`."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
        id: str | None = Field(default=None, description="Policy ID to include in body when convenience fields are used."),
        name: str | None = Field(default=None, description="Updated policy name."),
        description: str | None = Field(default=None, description="Updated policy description."),
        policy_properties: dict[str, Any] | None = Field(default=None, description="Updated policy properties."),
        precedence: int | None = Field(default=None, description="Updated policy precedence."),
    ) -> list[dict[str, Any]]:
        """Update a Data Protection policy."""
        request_body = body or _resource_body(
            {
                "id": id,
                "name": name,
                "description": description,
                "policy_properties": policy_properties,
                "precedence": precedence,
            }
        )
        if request_body is None:
            return [
                _format_error_response(
                    "`body` or at least one policy field is required.",
                    operation="entities_policy_patch_v2",
                )
            ]
        return self._write_resource_operation(
            "update",
            "policy",
            confirm_execution=confirm_execution,
            query_params={"platform_name": platform_name},
            body=request_body,
            body_required=True,
        )

    def delete_data_protection_policies(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Policy IDs to delete."),
        platform_name: Literal["win", "mac"] = Field(description="Policy platform name: `win` or `mac`."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection policies."""
        return self.delete_data_protection_resources(
            confirm_execution=confirm_execution,
            resource_type="policy",
            ids=ids,
            parameters={"platform_name": platform_name},
        )

    def set_data_protection_policy_precedence(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        platform_name: Literal["win", "mac"] = Field(description="Policy platform name: `win` or `mac`."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
        ids: list[str] | None = Field(default=None, description="Ordered policy IDs."),
    ) -> list[dict[str, Any]]:
        """Update Data Protection policy precedence."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="entities_policy_precedence_post_v1",
                )
            ]
        request_body = body or ({"ids": ids} if ids else None)
        if not request_body:
            return [
                _format_error_response(
                    "`body` or `ids` is required for precedence updates.",
                    operation="entities_policy_precedence_post_v1",
                )
            ]
        result = self._base_query_api_call(
            operation="entities_policy_precedence_post_v1",
            query_params={"platform_name": platform_name},
            body_params=request_body,
            error_message="Failed to update Data Protection policy precedence",
            default_result=[],
        )
        return [result] if self._is_error(result) else result

    def query_data_protection_classification_ids(
        self,
        filter: str | None = Field(default=None, description="Optional classification FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="name.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection classification IDs."""
        return self.query_data_protection_resources("classification", filter, limit, offset, sort)

    def get_data_protection_classifications(
        self,
        ids: list[str] | None = Field(default=None, description="Classification IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection classifications by ID."""
        return self.get_data_protection_resources("classification", ids=ids)

    def create_data_protection_classification(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
        name: str | None = Field(default=None, description="Classification name."),
        classification_properties: dict[str, Any] | None = Field(
            default=None,
            description="Classification properties.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection classification."""
        request_body = body or _resource_body(
            {
                "name": name,
                "classification_properties": classification_properties,
            }
        )
        return self._write_resource_operation(
            "create",
            "classification",
            confirm_execution=confirm_execution,
            query_params=None,
            body=request_body,
            body_required=True,
        )

    def update_data_protection_classifications(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Update Data Protection classifications."""
        return self._write_resource_operation(
            "update",
            "classification",
            confirm_execution=confirm_execution,
            query_params=None,
            body=body,
            body_required=True,
        )

    def delete_data_protection_classifications(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Classification IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection classifications."""
        return self.delete_data_protection_resources(confirm_execution, "classification", ids)

    def query_data_protection_content_pattern_ids(
        self,
        filter: str | None = Field(default=None, description="Optional content-pattern FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="created_at.desc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection content-pattern IDs."""
        return self.query_data_protection_resources("content_pattern", filter, limit, offset, sort)

    def get_data_protection_content_patterns(
        self,
        ids: list[str] | None = Field(default=None, description="Content-pattern IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection content patterns by ID."""
        return self.get_data_protection_resources("content_pattern", ids=ids)

    def create_data_protection_content_pattern(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
        name: str | None = Field(default=None, description="Pattern name."),
        category: str | None = Field(default=None, description="Pattern category."),
        description: str | None = Field(default=None, description="Pattern description."),
        example: str | None = Field(default=None, description="Example matching value."),
        min_match_threshold: int | None = Field(default=None, description="Minimum match threshold."),
        regexes: list[str] | None = Field(default=None, description="Regex list."),
        region: str | None = Field(default=None, description="Pattern region."),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection content pattern."""
        request_body = body or _direct_body(
            {
                "name": name,
                "category": category,
                "description": description,
                "example": example,
                "min_match_threshold": min_match_threshold,
                "regexes": regexes,
                "region": region,
            }
        )
        return self._write_resource_operation(
            "create",
            "content_pattern",
            confirm_execution=confirm_execution,
            query_params=None,
            body=request_body,
            body_required=True,
        )

    def update_data_protection_content_pattern(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        id: str | None = Field(default=None, description="Content-pattern ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Update a Data Protection content pattern."""
        if not id:
            return [
                _format_error_response(
                    "`id` is required for content-pattern updates.",
                    operation="entities_content_pattern_patch",
                )
            ]
        return self._write_resource_operation(
            "update",
            "content_pattern",
            confirm_execution=confirm_execution,
            query_params={"id": id},
            body=body,
            body_required=True,
        )

    def delete_data_protection_content_patterns(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Content-pattern IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection content patterns."""
        return self.delete_data_protection_resources(confirm_execution, "content_pattern", ids)

    def query_data_protection_cloud_application_ids(
        self,
        filter: str | None = Field(default=None, description="Optional cloud-application FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="name.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection cloud-application IDs."""
        return self.query_data_protection_resources(
            "cloud_application",
            filter,
            limit,
            offset,
            sort,
            parameters=None,
        )

    def get_data_protection_cloud_applications(
        self,
        ids: list[str] | None = Field(default=None, description="Cloud-application IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection cloud applications."""
        return self.get_data_protection_resources("cloud_application", ids=ids)

    def create_data_protection_cloud_application(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection cloud application."""
        return self._write_resource_operation(
            "create",
            "cloud_application",
            confirm_execution=confirm_execution,
            query_params=None,
            body=body,
            body_required=True,
        )

    def update_data_protection_cloud_application(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        id: str | None = Field(default=None, description="Cloud-application ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Update a Data Protection cloud application."""
        return self._patch_resource_with_id("cloud_application", confirm_execution, id, body)

    def delete_data_protection_cloud_applications(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Cloud-application IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection cloud applications."""
        return self.delete_data_protection_resources(confirm_execution, "cloud_application", ids)

    def query_data_protection_enterprise_account_ids(
        self,
        filter: str | None = Field(default=None, description="Optional enterprise-account FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="name.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection enterprise-account IDs."""
        return self.query_data_protection_resources(
            "enterprise_account",
            filter,
            limit,
            offset,
            sort,
            parameters=None,
        )

    def get_data_protection_enterprise_accounts(
        self,
        ids: list[str] | None = Field(default=None, description="Enterprise-account IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection enterprise accounts."""
        return self.get_data_protection_resources("enterprise_account", ids=ids)

    def create_data_protection_enterprise_account(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection enterprise account."""
        return self._write_resource_operation(
            "create",
            "enterprise_account",
            confirm_execution=confirm_execution,
            query_params=None,
            body=body,
            body_required=True,
        )

    def update_data_protection_enterprise_account(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        id: str | None = Field(default=None, description="Enterprise-account ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Update a Data Protection enterprise account."""
        return self._patch_resource_with_id("enterprise_account", confirm_execution, id, body)

    def delete_data_protection_enterprise_accounts(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Enterprise-account IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection enterprise accounts."""
        return self.delete_data_protection_resources(confirm_execution, "enterprise_account", ids)

    def query_data_protection_file_type_ids(
        self,
        filter: str | None = Field(default=None, description="Optional file-type FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="name.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection file-type IDs."""
        return self.query_data_protection_resources(
            "file_type",
            filter,
            limit,
            offset,
            sort,
            parameters=None,
        )

    def get_data_protection_file_types(
        self,
        ids: list[str] | None = Field(default=None, description="File-type IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection file types."""
        return self.get_data_protection_resources("file_type", ids=ids)

    def query_data_protection_sensitivity_label_ids(
        self,
        filter: str | None = Field(default=None, description="Optional sensitivity-label FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="display_name.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection sensitivity-label IDs."""
        return self.query_data_protection_resources(
            "sensitivity_label",
            filter,
            limit,
            offset,
            sort,
            parameters=None,
        )

    def get_data_protection_sensitivity_labels(
        self,
        ids: list[str] | None = Field(default=None, description="Sensitivity-label IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection sensitivity labels."""
        return self.get_data_protection_resources("sensitivity_label", ids=ids)

    def create_data_protection_sensitivity_label(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection sensitivity label."""
        return self._write_resource_operation(
            "create",
            "sensitivity_label",
            confirm_execution=confirm_execution,
            query_params=None,
            body=body,
            body_required=True,
        )

    def delete_data_protection_sensitivity_labels(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Sensitivity-label IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection sensitivity labels."""
        return self.delete_data_protection_resources(confirm_execution, "sensitivity_label", ids)

    def query_data_protection_local_application_group_ids(
        self,
        filter: str | None = Field(default=None, description="Optional local-application-group FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="name.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection local-application-group IDs."""
        return self.query_data_protection_resources(
            "local_application_group",
            filter,
            limit,
            offset,
            sort,
            parameters=None,
        )

    def get_data_protection_local_application_groups(
        self,
        ids: list[str] | None = Field(default=None, description="Local-application-group IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection local application groups."""
        return self.get_data_protection_resources("local_application_group", ids=ids)

    def create_data_protection_local_application_group(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection local application group."""
        return self._write_resource_operation(
            "create",
            "local_application_group",
            confirm_execution=confirm_execution,
            query_params=None,
            body=body,
            body_required=True,
        )

    def update_data_protection_local_application_group(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        id: str | None = Field(default=None, description="Local-application-group ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Update a Data Protection local application group."""
        return self._patch_resource_with_id("local_application_group", confirm_execution, id, body)

    def delete_data_protection_local_application_groups(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Local-application-group IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection local application groups."""
        return self.delete_data_protection_resources(confirm_execution, "local_application_group", ids)

    def query_data_protection_local_application_ids(
        self,
        filter: str | None = Field(default=None, description="Optional local-application FQL filter."),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="name.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection local-application IDs."""
        return self.query_data_protection_resources(
            "local_application",
            filter,
            limit,
            offset,
            sort,
            parameters=None,
        )

    def get_data_protection_local_applications(
        self,
        ids: list[str] | None = Field(default=None, description="Local-application IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection local applications."""
        return self.get_data_protection_resources("local_application", ids=ids)

    def create_data_protection_local_application(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection local application."""
        return self._write_resource_operation(
            "create",
            "local_application",
            confirm_execution=confirm_execution,
            query_params=None,
            body=body,
            body_required=True,
        )

    def update_data_protection_local_application(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        id: str | None = Field(default=None, description="Local-application ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Update a Data Protection local application."""
        return self._patch_resource_with_id("local_application", confirm_execution, id, body)

    def delete_data_protection_local_applications(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Local-application IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection local applications."""
        return self.delete_data_protection_resources(confirm_execution, "local_application", ids)

    def query_data_protection_web_location_ids(
        self,
        filter: str | None = Field(default=None, description="Optional web-location FQL filter."),
        type: Literal["predefined", "custom"] | None = Field(
            default=None,
            description="Optional web-location type.",
        ),
        limit: int = Field(default=100, ge=1, le=500, description="Maximum IDs to return. [1-500]"),
        offset: int = Field(default=0, ge=0, description="Result offset."),
        sort: str | None = Field(default="name.asc", description="Optional sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query Data Protection web-location IDs."""
        parameters = {"type": type} if type else None
        return self.query_data_protection_resources(
            "web_location",
            filter,
            limit,
            offset,
            sort,
            parameters=parameters,
        )

    def get_data_protection_web_locations(
        self,
        ids: list[str] | None = Field(default=None, description="Web-location IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve Data Protection web locations."""
        return self.get_data_protection_resources("web_location", ids=ids)

    def create_data_protection_web_location(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Create a Data Protection web location."""
        return self._write_resource_operation(
            "create",
            "web_location",
            confirm_execution=confirm_execution,
            query_params=None,
            body=body,
            body_required=True,
        )

    def update_data_protection_web_location(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        id: str | None = Field(default=None, description="Web-location ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Update a Data Protection web location."""
        return self._patch_resource_with_id("web_location", confirm_execution, id, body)

    def delete_data_protection_web_locations(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute."),
        ids: list[str] | None = Field(default=None, description="Web-location IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete Data Protection web locations."""
        return self.delete_data_protection_resources(confirm_execution, "web_location", ids)

    def _patch_resource_with_id(
        self,
        resource_type: str,
        confirm_execution: bool,
        id: str | None,
        body: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        operation = _operation_for(resource_type, "update")
        id = _clean_optional(id)
        body = _clean_optional(body)
        if not id:
            return [
                _format_error_response(
                    "`id` is required for this update operation.",
                    operation=operation,
                )
            ]
        return self._write_resource_operation(
            "update",
            resource_type,
            confirm_execution=confirm_execution,
            query_params={"id": id},
            body=body,
            body_required=True,
        )

    def _write_resource_operation(
        self,
        action: Literal["create", "update", "delete"],
        resource_type: str,
        *,
        confirm_execution: bool,
        query_params: dict[str, Any] | None,
        body: dict[str, Any] | None,
        body_required: bool,
    ) -> list[dict[str, Any]]:
        operation = _operation_for(resource_type, action)
        if not confirm_execution:
            return [_format_error_response("This operation requires `confirm_execution=true`.", operation=operation)]
        if body_required and not body:
            return [_format_error_response("`body` is required for this operation.", operation=operation)]
        result = self._base_query_api_call(
            operation=operation,
            query_params=query_params,
            body_params=body,
            error_message=f"Failed to {action} Data Protection {resource_type} resource",
            default_result=[],
        )
        return [result] if self._is_error(result) else result


def _operation_for(resource_type: str, action: str) -> str:
    operations = _RESOURCE_OPERATIONS.get(resource_type)
    operation = operations.get(action) if operations else None
    if not operation:
        raise ValueError(f"Data Protection {resource_type} does not support {action}.")
    return operation


def _merge_parameters(
    base: dict[str, Any] | None,
    overlay: dict[str, Any],
) -> dict[str, Any]:
    base = _clean_optional(base)
    merged = dict(base or {}) if isinstance(base, dict) else {}
    for key, value in overlay.items():
        value = _clean_optional(value)
        if value is not None:
            merged[key] = value
    return merged


def _direct_body(values: dict[str, Any]) -> dict[str, Any] | None:
    resource = {
        key: value
        for key, raw_value in values.items()
        if (value := _clean_optional(raw_value)) is not None
    }
    return resource or None


def _resource_body(values: dict[str, Any]) -> dict[str, Any] | None:
    resource = _direct_body(values)
    if not resource:
        return None
    return {"resources": [resource]}


def _clean_optional(value: Any) -> Any:
    return None if isinstance(value, FieldInfo) else value
