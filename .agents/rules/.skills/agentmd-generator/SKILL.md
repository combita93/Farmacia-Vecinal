---
name: agentmd-generator
description: >
  Generates a production-ready AGENTS.md file at the repo root by pulling
  project context from a Confluence space via the Atlassian MCP. Use this skill whenever
  the user asks to "create an AGENTS.md", "generate
  the AI contract for this repo", "set up the coding-agent context file", "Genera el 
  archivo AGENTS.md desde mi espacio de Confluence [KEY_DEL_ESPACIO]", "Configura el 
  contexto de IA para este repo usando la skill agentmd-generator", or anything
  involving syncing Confluence documentation into an agent-ready project file. Also
  triggers when the user mentions connecting Confluence to Claude Code, Cursor, Windsurf,
  Continue, Aider, or Antigravity. Always use this skill — do not attempt to hand-craft
  AGENTS.md from scratch without it.
compatibility: >
  Requires the Atlassian MCP to be enabled (Confluence read access).
  Compatible with Claude Code, Cursor, Windsurf, Continue, Aider, Google Antigravity.
metadata:
  author: skill-creator
  version: "1.0"
  spec: https://agents.md/
  template-source: AGENTS_template.md
---

# agentmd-generator skill

Generates a fully-populated `AGENTS.md` at the root of the
current project by reading context from a Confluence space, then filling in the
canonical template that every modern AI coding assistant understands.

### Casos de uso (Triggers)
- *"Genera el archivo AGENTS.md desde mi espacio de Confluence [KEY_DEL_ESPACIO]"*
- *"Configura el contexto de IA para este repo usando la skill agentmd-generator"*

---

## Quick-reference — what this skill does

```
Confluence space
      │  (Atlassian MCP)
      ▼
Extract context (name, stack, arch, glossary…)
      │
      ▼
Fill AGENTS_template.md placeholders
      │
      ▼
Write  ./AGENTS.md
```

---

## Step 0 — Verify Atlassian MCP is available

Before doing anything else, check whether the Atlassian MCP tool is connected.

**How to check:**
Look at the tools available in the current session. Atlassian MCP tools are usually
named with a prefix like `mcp_atlassian_*` or `atlassian__*`.

**If the MCP IS available → proceed to Step 1.**

**If the MCP is NOT available:**
Stop and tell the user exactly this (adapt tone to context):

> ⚠️  **Atlassian MCP not connected**
>
> This skill needs the **Atlassian MCP** to read your Confluence space.
> Please enable it:
>
> 1. Open **Claude.ai → Settings → Integrations** (or your IDE's MCP settings panel).
> 2. Find **Atlassian / Confluence** and click **Connect**.
> 3. Authorise with your Atlassian account and select the workspace.
> 4. Return here and re-run the request.
>
> If you're using Claude Code, add the MCP in `.claude/settings.json` under `mcpServers`.
> See `references/atlassian-mcp-setup.md` for the exact config snippet.

Do **not** attempt to create the file manually without real Confluence data — placeholders
left in the output break every downstream tool that reads it.

---

## Step 1 — Identify the Confluence space

**CRITICAL RULE:** Always use the space **`PM`** (Operaciones) by default.
Do not ask the user for a space key.
Proceed directly to Step 2 using the space key `PM`.

---

## Step 2 — Read Confluence context

Use the Atlassian MCP to retrieve the following. Collect as much as you can find;
mark missing fields as `TODO` — never leave the raw `{{PLACEHOLDER}}` syntax.

### 2a — Space homepage / overview page
Read the root page of the space. Extract:
- **Project name** → `{{PROJECT_NAME}}`
- **One-line description** → `{{PROJECT_SHORT_DESC}}`
- **Domain / industry** → `{{DOMAIN}}`
- **Current phase** → `{{PHASE}}`
- **Owner / maintainer contact** → `{{OWNER_CONTACT}}`
- **Last updated date** → `{{LAST_UPDATED}}`

### 2b — Tech stack / architecture pages
Search for pages titled like "Architecture", "Tech Stack", "Stack", "ADR", "Design".
Extract:
- **Primary language** → `{{PRIMARY_LANG}}`
- **Core libraries** → `{{CORE_LIBS}}`
- **Data formats** → `{{DATA_FORMAT}}`
- **Architecture pattern** → `{{ARCH_PATTERN}}`

### 2c — Repository / structure pages
Search for pages titled like "Repository", "Repo", "Folder Structure", "Codebase".
Extract or infer:
- **Repo tree** → `{{REPO_TREE}}` (ASCII tree, 2-3 levels deep)
- **Target repo** → `{{TARGET_REPO}}`
- **Related services** → `{{RELATED_SERVICES}}`

### 2d — Glossary / domain concepts
Search for pages titled like "Glossary", "Concepts", "Domain", "Terminology".
Extract bullet list → `{{DOMAIN_CONCEPTS}}`

### 2e — Development workflows
Search for pages titled like "Development", "Workflow", "Getting Started", "CI", "Runbook".
Extract shell commands → `{{WORKFLOW_COMMANDS}}`

### 2f — Best practices & conventions
Search for pages titled like "Conventions", "Style", "Best Practices", "Standards".
Extract bullet list → `{{BEST_PRACTICES}}`

### 2g — Knowledge / architecture artefacts
Search for pages tagged as ADR, ML Canvas, Model Card, Knowledge Base.
Build a bullet list → `{{KNOWLEDGE_DOCS}}`

### 2h — Migration notes (optional)
Search for pages titled like "Migration", "v2", "Upgrade". If found:
- `{{MIGRATION_NOTES}}`
If none found, delete the Migration section from the output.

### 2i — Subagent table & common tasks (infer if not in Confluence)
Based on the domain and tech stack gathered above, synthesise reasonable defaults:
- `{{SUBAGENT_TABLE}}` — at least 3 rows: `data-science`, `backend`, `devops`
- `{{COMMON_TASKS}}` — 3-5 copy-paste recipes relevant to the stack

---

## Step 3 — Fill the template

Read the template from `assets/AGENTS_template.md`.

Replace **every** `{{PLACEHOLDER}}` with the value collected in Step 2.
Rules:
- Replace with `TODO — not found in Confluence` if data is genuinely missing.
- Never leave `{{PLACEHOLDER}}` syntax in the output.
- Keep all universal guardrails in §8 and §11 unchanged.
- Keep the HTML comment block at the top **removed** (it's a template-only note).
- Update the frontmatter comment block → remove entirely from final file.
- Set `{{LAST_UPDATED}}` to today's date in `YYYY-MM-DD` format.

---

## Step 4 — Write the output files

Write the filled content to the **project root**:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Primary — read by Codex, Jules, Aider, Goose, Cursor, Windsurf, VS Code, Devin, Junie, Warp, RooCode, Amp, Gemini CLI, Copilot, Augment, Claude Code |

If an `AGENTS.md` already exists, show a diff summary and ask the user
whether to overwrite, merge, or abort before writing.

```
# Pseudocode
if file_exists("AGENTS.md"):
    show_diff(existing, new_content)
    ask: "Overwrite? [y/N/merge]"

write("AGENTS.md", filled_content)
```

---

## Step 5 — Validate & report

After writing:

1. **Placeholder check** — scan output for any remaining `{{` patterns. If found, list
   them and ask the user to supply the missing values.

2. **Section completeness check** — verify all 11 sections exist and are non-empty.

3. **Report to user:**

```
✅ AGENTS.md written successfully.

📋 Summary:
  • Project: <PROJECT_NAME>
  • Space: <SPACE_KEY>
  • Sections populated: X / 11
  • Missing data (TODO items): N fields

⚡ Next steps:
  1. Review the file and fill any TODO items.
  2. Commit AGENTS.md to the repo root.
  3. Add .claude/agents/ subagents for Claude Code (see §7.1 of the file).
```

---

## Edge cases & fallbacks

| Situation | Behaviour |
|-----------|-----------|
| MCP not connected | Stop, show setup instructions (Step 0) |
| Space key not found | Ask user to verify the key; list available spaces via MCP |
| Page not found for a section | Mark as `TODO — not found in Confluence` |
| File already exists | Show diff, ask before overwriting |
| Confluence returns empty space | Warn user; offer to create a minimal file from user input |
| No migration pages found | Delete §6 from output entirely |

---

## Reference files

- `REFERENCES.md` — Índice de referencias disponibles
- `references/atlassian-mcp-setup.md` — How to configure the Atlassian MCP in each IDE
- `references/agents-md-spec.md` — agents.md format specification summary
- `assets/AGENTS_template.md` — The canonical template (fill this, don't modify it)

---

## Do NOT

- Do not invent project details that aren't in Confluence.
- Do not leave `{{PLACEHOLDER}}` tokens in the written files.
- Do not skip Step 0 (MCP check) — a file without real data is worse than no file.
- Do not write to subdirectories — output must go to the **project root**.
- Do not remove the universal guardrails in §8 and §11 of the template.
