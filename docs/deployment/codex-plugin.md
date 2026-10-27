<!-- meta:title Codex Plugin -->
<!-- meta:description Install Falcon MCP as a local Codex plugin with required Falcon API credentials and no Docker dependency. -->
<!-- meta:section deployment -->
<!-- meta:link-base /falcon-mcp/ -->

The Falcon MCP plugin runs the Python server locally over stdio. Codex starts and stops the server;
Docker and a separately hosted HTTP endpoint are unnecessary. The plugin includes the server from
this repository and uses its locked Python dependencies.

## Prerequisites

- Codex with plugin support (`codex plugin --help`).
- [uv](https://docs.astral.sh/uv/getting-started/installation/) available on the PATH used by Codex.
- Python 3.11 or higher. uv can download a compatible Python runtime when one is unavailable locally.
- A Falcon API **client ID and client secret**, created in Falcon's API Clients and Keys page, with
  the [scopes needed by your modules](../../README.md#required-api-scopes-by-module).
- Network access to download Python dependencies on first launch and to reach your Falcon API region.

Falcon uses the client ID and secret together to obtain its API access token. Both are required.
The existing `FALCON_MCP_API_KEY` setting protects an MCP HTTP endpoint; it is not a Falcon API
credential and is not used by this stdio plugin.

## Configure your Falcon connection

Choose one fork as your installation source. Both publish the plugin on `codex/falcon-codex-plugin`.
For OIFhax:

```bash
git clone --branch codex/falcon-codex-plugin https://github.com/OIFhax/falcon-mcp.git
cd falcon-mcp
```

For HTS-CyberSecurity, use this clone command instead:

```bash
git clone --branch codex/falcon-codex-plugin https://github.com/hts-cybersecurity/falcon-mcp.git
cd falcon-mcp
```

From the cloned repository, run the setup helper in your terminal:

```bash
uv run --locked --no-dev --no-env-file python -m falcon_mcp.codex_plugin --configure
```

Enter your client ID, client secret, and Falcon API base URL at the prompts. Credential input is
hidden. The helper saves the connection in `~/.config/falcon-mcp/codex.json`, outside the repository
and plugin cache, with owner-only file permissions (`0600` on POSIX systems). This lets Codex launched
from the desktop use the saved connection without inheriting your terminal's environment. Keep this
file private; it contains your Falcon API credentials.

Check the saved configuration without making a Falcon API request:

```bash
uv run --locked --no-dev --no-env-file python -m falcon_mcp.codex_plugin --check-config
```

This checks local configuration only. Complete the connectivity check below after installation to
verify the credentials with Falcon. The plugin reports a setup error and does not start if the
required credentials are absent.

## Install in Codex

Add the same fork you cloned as a marketplace. For OIFhax:

```bash
codex plugin marketplace add OIFhax/falcon-mcp --ref codex/falcon-codex-plugin
```

For HTS-CyberSecurity, use this command instead:

```bash
codex plugin marketplace add hts-cybersecurity/falcon-mcp --ref codex/falcon-codex-plugin
```

Then install the plugin:

```bash
codex plugin add falcon-mcp@falcon-mcp
codex plugin list --marketplace falcon-mcp
```

If an older CLI rejects a reasoning setting written by the desktop app, such as
`unknown variant ultra`, update the CLI or use a per-command override. For example:

```bash
codex -c 'model_reasoning_effort="high"' plugin add falcon-mcp@falcon-mcp
```

Use the same override for the marketplace and list commands if needed. This does not change your
saved model settings.

Choose only one fork source: both use the marketplace name `falcon-mcp` and plugin name `falcon-mcp`.
Restart the Codex desktop app, then open a new local chat. You can also find the plugin under the
Falcon MCP marketplace in the plugin browser and install it there after adding the marketplace.
This plugin runs on your computer and requires a local chat with access to uv and the credential file.

## Verify connectivity

In a new chat, ask:

> Use the Falcon MCP plugin to run `falcon_startup_check`. Report whether Falcon is connected, which
> API region is active, and which modules are enabled.

`falcon_startup_check` is a read-only check. Confirm `connected` is `true` and that the region and
enabled modules match your intended connection. All server modules are available; module selection,
API scopes, and any configured tool restrictions determine which operations you can use.

If authentication fails, check the API region and credentials, then run `--configure` again. A
permission error from a particular tool may require updating that API client's scopes. The
[credentials guide](../getting-started/credentials.md) explains Falcon API client setup.

## Configuration sources

The plugin reads its explicit configuration file and supported environment variables. It does not
automatically load `.env` files from the repository, plugin cache, or current project.

- The default configuration file is `~/.config/falcon-mcp/codex.json`.
- Set `FALCON_MCP_CONFIG_FILE` to an **absolute path** to use another configuration file. Set it for
  both the setup command and the Codex process that launches the plugin.
- A complete `FALCON_CLIENT_ID` and `FALCON_CLIENT_SECRET` environment pair overrides the saved
  credentials. A partial pair is an error, so credentials from different sources cannot be mixed.
- Supported non-credential environment options override their saved values individually.

Environment variables must be present in the Codex process environment. For a desktop app launched
from the dock or application menu, the default saved configuration is usually the simplest setup.
After changing credentials or options, start a new chat so the server reloads them. Run `--configure`
to replace stored credentials when rotating your Falcon API secret.

### Optional settings

The configuration file uses the same `FALCON_*` names as environment variables, and every value must
be a JSON string. To select a child CID, limit modules, or enable read-only tools, add the relevant
fields to your existing saved JSON object. For example, these optional fields can be merged into it:

```json
{
  "FALCON_MEMBER_CID": "your-child-cid",
  "FALCON_MCP_MODULES": "detections,hosts,intel",
  "FALCON_MCP_READ_ONLY": "true"
}
```

Preserve the existing `FALCON_CLIENT_ID`, `FALCON_CLIENT_SECRET`, and `FALCON_BASE_URL` fields when
editing optional settings. Omit `FALCON_MEMBER_CID` when connecting to the API client's home CID.
Boolean options use strings such as `"true"`; module and tool lists use comma-separated strings.
The plugin also accepts `FALCON_PROXY_URL`, `FALCON_MCP_DYNAMIC`, `FALCON_MCP_TOOLS`,
`FALCON_MCP_EXCLUDE_TOOLS`, `FALCON_MCP_DEBUG`, `FALCON_MCP_USER_AGENT_COMMENT`, and the server's
HTTP timeout and retry options. See the [configuration guide](../getting-started/configuration.md)
for their behavior. Run `--check-config` after editing; rerunning `--configure` preserves optional
settings while replacing the prompted credentials and API URL.

## Move from Docker

1. Configure and install the plugin, then verify `falcon_startup_check` from the plugin server.
2. Disable the old Docker-backed Falcon MCP entry in your Codex MCP settings. If you manage it in
   `~/.codex/config.toml`, set `enabled = false` in that existing server's `[mcp_servers.<name>]` table.
3. Restart Codex and open a new chat. Verify that Falcon tools come from the installed plugin.
4. Stop the old Falcon MCP container when no other client uses it.

Docker's `--env-file` configuration is not copied automatically. Enter the same intended Falcon API
client and region through `--configure`, and preserve any module or tool restrictions you need.

## Local development

From a checkout of this branch, configure credentials with the setup helper, then build a local
marketplace in a fresh output directory outside the checkout:

```bash
python3 scripts/build_codex_plugin.py --output /absolute/path/to/falcon-plugin-marketplace
codex plugin marketplace add /absolute/path/to/falcon-plugin-marketplace
codex plugin add falcon-mcp@falcon-mcp
```

The builder creates a self-contained `plugins/falcon-mcp` bundle and a local marketplace catalog
that points to it. Use this generated marketplace to test checkout changes. The repository's own
marketplace catalog installs the published Git branch from its respective fork.

The plugin's `.codex-plugin/plugin.json` declares `.mcp.json`, which launches the local Python server
through uv. Codex installs a copy in its plugin cache, so editing the checkout does not directly edit
the running plugin. Rebuild into a fresh output directory and refresh or reinstall the local plugin
after changes, restart Codex, and test in a new chat.

See OpenAI's [plugin packaging guide](https://developers.openai.com/plugins/build/plugins) for
marketplace behavior and [local MCP server documentation](https://developers.openai.com/plugins/deploy/desktop-only)
for stdio plugin execution.
