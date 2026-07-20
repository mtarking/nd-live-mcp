# nd-live-mcp

Read-only **live Nexus Dashboard (ND)** client library plus an MCP server. Log into a running ND
and query fabric status/health, switches, interfaces, VRFs, networks, and the embedded template
library — for AgenticOps, live validation, and tests.

Design & rationale: [`../docs/ND_LIVE_MCP.md`](../docs/ND_LIVE_MCP.md).

## Architecture

The core is a plain Python library (`nd/`); the MCP server (`server.py`) is a thin wrapper over it.
The same library is imported directly by `tests/` and can be reused by CI / Ansible — MCP and CI
share the *code*, not the *execution path*.

```
nd/
  config.py    env/secrets, per-service base URLs, TLS + output settings
  auth.py      POST /api/v1/infra/login, JWT cache, refresh on 401
  client.py    httpx GET core (read-only), auth + single re-auth retry
  render.py    compact tables + hard output-size guard
  tools/       fabrics, switches, interfaces, vrfs, networks, templates
server.py      FastMCP server exposing the tools (stdio)
tests/         deterministic tests importing nd/ directly (no live ND, no LLM)
```

## Scope

- **Read-only (GET only)** by design. No config-push/remediation in v1.
- Compact output by default; pass `detail=true` for full JSON on a specific item.
- Every result is truncated to `ND_MAX_OUTPUT_CHARS` to protect the model's context.

## Setup

```bash
cd nd-live-mcp
uv venv --python 3.12
uv pip install -e ".[dev]"
cp .env.example .env   # then fill in ND_HOST / ND_USERNAME / ND_PASSWORD
```

Credentials are read from `ND_*` environment variables — never from tool arguments or chat. Prefer
an OS keychain that populates the environment over a plaintext `.env`.

## Run the tests (no live ND needed)

```bash
uv run pytest -q
```

## Run the server

```bash
uv run server.py        # stdio transport (default)
```

## Register with VS Code / Copilot or Claude Code

Add to the workspace `.vscode/mcp.json` (Copilot) and/or `.mcp.json` (Claude Code) with
**auto-start off**, then Start it only when doing ND ops:

```jsonc
{
  "servers": {
    "nd-live": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "${workspaceFolder}/nd-live-mcp",
      "env": {
        "ND_HOST": "https://my-nd.example.com",
        "ND_DOMAIN": "local",
        "ND_USERNAME": "admin"
      }
    }
  }
}
```

Set `ND_PASSWORD` via your shell/keychain, not in the JSON. Enable/disable per session from the
Tools picker, or Start/Stop the server to control its context cost.

## Tools

| Tool | Purpose |
| --- | --- |
| `nd_list_fabrics` / `nd_get_fabric` | Fabric inventory (Manage) |
| `nd_fabric_health` | Health/anomaly summary (Analyze) |
| `nd_list_switches` | Switch inventory (Manage) |
| `nd_switch_interfaces` | Interfaces for a switch (Manage) |
| `nd_list_vrfs` / `nd_get_vrf` | VRFs (Manage) |
| `nd_list_networks` / `nd_get_network` | Networks (Manage) |
| `nd_list_templates` / `nd_get_template` | Embedded template library (Manage) |

## Confirm at integration

- Per-service base paths default to the ND 4.2.1 `servers` blocks (`/api/v1/manage`,
  `/api/v1/analyze`, `/api/v1/infra`, `/api/v1/oneManage`); override via `ND_*_BASE` if your
  deployment differs.
- Some per-item field names are parsed defensively; verify against your ND build and adjust the
  `first([...])` key lists in `nd/tools/` if a column shows `-`.
