"""
Contains Delivery Settings resources.
"""

DELIVERY_SETTINGS_USAGE_GUIDE = """
# Delivery Settings Guide

Use `falcon_get_delivery_settings` to inspect the tenant's current Delivery Settings configuration.

Use `falcon_create_delivery_settings` to create or update delivery settings records.

## Common fields

- `delivery_type`: Delivery channel or content type to configure
- `delivery_cadence`: Frequency or cadence for the delivery configuration

## Notes

- The Falcon API expects a `delivery_settings` array in the request body.
- Prefer passing the full `body` when you already have a validated payload from another workflow.
"""

DELIVERY_SETTINGS_SAFETY_GUIDE = """
# Delivery Settings Safety Guide

Delivery Settings changes affect tenant-level content delivery behavior.

## Operational guardrails

- Require `confirm_execution=true` for write operations.
- Review the current configuration with `falcon_get_delivery_settings` before making changes.
- Prefer a minimal payload and document the intended change in the surrounding workflow.
- Test changes in a non-production tenant when possible.
"""
