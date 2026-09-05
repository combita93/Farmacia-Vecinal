# Atlassian MCP — Setup Guide

Quick reference for enabling the Atlassian MCP in each supported environment.

---

## Claude.ai (claude.ai)

1. Go to **Settings → Integrations**.
2. Find **Atlassian** and click **Connect**.
3. Authorise via OAuth with your Atlassian account.
4. Select your workspace. Confirm Confluence access.

---

## Claude Code (CLI)

Add to `.claude/settings.json` in your repo root (or `~/.claude/settings.json` for global):

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "ATLASSIAN_URL": "https://your-org.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

Generate your API token at: https://id.atlassian.com/manage-profile/security/api-tokens

---

## Cursor

Add to `.cursor/mcp.json` (or `~/.cursor/mcp.json` for global):

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "ATLASSIAN_URL": "https://your-org.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

---

## Windsurf

Add to `.windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "ATLASSIAN_URL": "https://your-org.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

---

## Continue

In `.continue/config.json`, add under `contextProviders` or `mcpServers`:

```json
{
  "mcpServers": [
    {
      "name": "atlassian",
      "command": "npx -y @modelcontextprotocol/server-atlassian",
      "env": {
        "ATLASSIAN_URL": "https://your-org.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "<your-api-token>"
      }
    }
  ]
}
```

---

## Aider

Set environment variables before running:

```bash
export ATLASSIAN_URL="https://your-org.atlassian.net"
export ATLASSIAN_USERNAME="your-email@example.com"
export ATLASSIAN_API_TOKEN="<your-api-token>"

aider --mcp-server "npx -y @modelcontextprotocol/server-atlassian"
```

---

## Google Antigravity / Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "ATLASSIAN_URL": "https://your-org.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

---

## Notes

- Never commit `ATLASSIAN_API_TOKEN` to version control. Use `.env` + `.gitignore`, or
  your CI secret manager (GitHub Actions secrets, AWS SSM, etc.).
- The MCP server package `@modelcontextprotocol/server-atlassian` requires Node.js 18+.
- Confluence Cloud and Confluence Data Center (v8+) are both supported.
- For Data Center, set `ATLASSIAN_URL` to your self-hosted base URL.
