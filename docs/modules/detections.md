<!-- meta:title Detections -->
<!-- meta:description Detections module for CrowdStrike Falcon. -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Detections module for CrowdStrike Falcon.

## API Scopes

- `Alerts:read`
- `Alerts:write`

## Tools

### `falcon_search_detections`

**Required scopes:** `Alerts:read`

Find detections by criteria and return their complete details.

**Example prompts:**

- "Show me new high severity detections from the last 7 days"
- "Find all unassigned critical detections"

### `falcon_search_detections_combined`

**Required scopes:** `Alerts:read`

Search detections using PostCombinedAlertsV1.

### `falcon_query_detection_ids_v1`

**Required scopes:** `Alerts:read`

Query detection IDs using GetQueriesAlertsV1.

### `falcon_query_detection_ids_v2`

**Required scopes:** `Alerts:read`

Query detection IDs using GetQueriesAlertsV2.

### `falcon_get_detection_details`

**Required scopes:** `Alerts:read`

Backward-compatible alias for PostEntitiesAlertsV2 details retrieval.

**Example prompts:**

- "Get me the details for this detection"

### `falcon_get_detection_details_v1`

**Required scopes:** `Alerts:read`

Retrieve detection details using PostEntitiesAlertsV1.

### `falcon_get_detection_details_v2`

**Required scopes:** `Alerts:read`

Retrieve detection details using PostEntitiesAlertsV2.

### `falcon_aggregate_detections_v1`

**Required scopes:** `Alerts:read`

Run detection aggregation queries using PostAggregatesAlertsV1.

### `falcon_aggregate_detections_v2`

**Required scopes:** `Alerts:read`

Run detection aggregation queries using PostAggregatesAlertsV2.

### `falcon_update_detections_v1`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Alerts:write`

Perform detection update actions using PatchEntitiesAlertsV1.

### `falcon_update_detections_v2`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Alerts:write`

Perform detection update actions using PatchEntitiesAlertsV2.

### `falcon_update_detections_v3`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Alerts:write`

Perform detection update actions using PatchEntitiesAlertsV3.

### `falcon_aggregate_detections`

**Required scopes:** `Alerts:read`

Count and summarize detections (also called alerts) without retrieving each record.

Use this for "how many" and "top N" questions — alerts per severity, status,
tactic, or host, distinct host counts, and alert volume over time — instead of
paging through falcon_search_detections. Consult
falcon://detections/search/fql-guide before constructing filter expressions.
Returns one aggregation per request holding `buckets`, which key on `label`
with a `count`; single-value aggregations (`cardinality`, `max`, `min`, `avg`,
`sum`) report their answer as `value` instead.

**Example prompts:**

- "How many detections do we have by severity?"
- "What are the top 10 hosts by alert count this week?"
- "Show me alert volume per day for the last 30 days"
- "How many distinct hosts have critical alerts?"

### `falcon_update_detections`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Alerts:write`

Update the status, assignment, visibility, comments, and tags of one or more detections.

Use to change status (new, in_progress, reopened, closed), assign to a user by UUID,
email address, or full name, unassign, append a comment, hide/show detections in the UI,
or add/remove tags. Resolution is tag-based: applying the conventional tags true_positive,
false_positive, or ignored is what populates the console's Resolution view. At least one
update parameter must be provided. Requests covering more than 1000 detection IDs are
chunked automatically so none are silently dropped. Returns `[]` (empty list) on success, or
`{"result": [], "hint": "..."}` when closing without adding a resolution tag in this call;
returns an error dict on failure. If a later chunk fails after earlier chunks already
applied, the error dict carries a `partial_success` block listing the already-updated ids so
the caller can retry only the remainder rather than re-applying non-idempotent actions.

**Example prompts:**

- "Mark detection abc123 as in_progress"
- "Assign detection abc123 to analyst@example.com"
- "Close these detections and add a comment: resolved via playbook"
- "Mark detection abc123 as a true positive and close it"
- "Remove all fc/ prefixed tags from this detection"

## Resources

- **`falcon://detections/search/fql-guide`**: Contains the guide for the `filter` param used by detections query/search tools.
- **`falcon://detections/aggregation/guide`**: Guidance and body examples for detections aggregate tools.
- **`falcon://detections/update-actions/guide`**: Safety and action-parameter guidance for detections update tools.
