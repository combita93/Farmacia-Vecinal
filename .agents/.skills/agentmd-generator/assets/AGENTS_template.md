<!--
==================================================================================
  AGENTS.template.md  —  Reusable multi-IDE context file
  ---------------------------------------------------------------------------------
  Purpose:
    Drop-in template for any repo that wants a single "AI contract" consumed by
    Claude Code, Cursor, Windsurf, Continue, Aider, and Google Antigravity.

  How to use:
    1. Copy this file to your repo root as AGENTS.md.
    2. Replace every {{PLACEHOLDER}} (Handlebars style). Leave optional sections
       empty or delete them — never leave raw placeholders in production.
    3. Commit. Most modern IDEs will auto-detect AGENTS.md at root.

  Placeholder index (search & replace):
    {{PROJECT_NAME}}              e.g. "Hydroginc — Dynamometer Card AI"
    {{PROJECT_SHORT_DESC}}        one-line elevator pitch
    {{DOMAIN}}                    e.g. "Oil & gas production optimization"
    {{PHASE}}                     e.g. "EDA Complete / Feature Engineering (MLOps S3)"
    {{PRIMARY_LANG}}              e.g. "Python 3.9+"
    {{CORE_LIBS}}                 comma-separated key libs
    {{DATA_FORMAT}}               e.g. "Excel .xls, JSON, Parquet"
    {{ARCH_PATTERN}}              e.g. "Medallion (Bronze/Silver/Gold)"
    {{REPO_TREE}}                 multi-line ASCII tree (inside the code fence)
    {{DOMAIN_CONCEPTS}}           bullet list of domain glossary entries
    {{WORKFLOW_COMMANDS}}         shell snippets for common workflows
    {{TARGET_REPO}}               e.g. "migration_v2/hrp-service-ml"
    {{RELATED_SERVICES}}          bullet list of sibling services
    {{SUBAGENT_TABLE}}            | name | when to delegate | rows
    {{CURSORRULES_PATHS}}         bullet list of .cursorrules locations
    {{SKILL_BUNDLE_PATH}}         e.g. ".agents/BP011-GenAI-agents/.agents/skills/"
    {{KNOWLEDGE_DOCS}}            bullet list of must-read docs
    {{BEST_PRACTICES}}            bullet list (or sub-sections) of conventions
    {{COMMON_TASKS}}              code blocks for "how do I X?" recipes
    {{MIGRATION_NOTES}}           optional, delete if not applicable
    {{OWNER_CONTACT}}             email or Slack handle of the maintainer

  Remove this whole HTML comment block once you've filled the file.
==================================================================================
-->

# AGENTS.md

This file is the single source of truth that AI coding assistants
(Claude Code, Cursor, Windsurf, Continue, Aider, Google Antigravity, etc.)
read before touching this repository. Keep it short, opinionated, and current.

---

## 1. Project Overview

**{{PROJECT_NAME}}**

{{PROJECT_SHORT_DESC}}

- **Domain:** {{DOMAIN}}
- **Current phase:** {{PHASE}}
- **Owner / contact:** {{OWNER_CONTACT}}

---

## 2. Technology Stack

- **Primary language:** {{PRIMARY_LANG}}
- **Core libraries / frameworks:** {{CORE_LIBS}}
- **Data formats:** {{DATA_FORMAT}}
- **Architecture pattern:** {{ARCH_PATTERN}}

---

## 3. Repository Layout

```
{{REPO_TREE}}
```

---

## 4. Domain Glossary

Key concepts an AI assistant must understand before generating code:

{{DOMAIN_CONCEPTS}}

---

## 5. Development Workflows

```bash
{{WORKFLOW_COMMANDS}}
```

---

## 6. Integration & Migration Notes

<!-- Delete this section if the repo is not part of a migration. -->

- **Target repository / service:** `{{TARGET_REPO}}`
- **Related services:**
{{RELATED_SERVICES}}

{{MIGRATION_NOTES}}

---

## 7. AI Agent Configuration (multi-IDE)

This repo ships with a portable agent layer so every IDE sees the same roles.

### 7.1 Claude Code — project subagents

Claude Code auto-loads Markdown files with YAML frontmatter from
`.claude/agents/`. Commit them for the whole team.

| Subagent | When to delegate |
| --- | --- |
{{SUBAGENT_TABLE}}

Invoke explicitly (“use the `data-science` subagent”) or let Claude Code
auto-delegate. Manage with `/agents` or `claude agents` (CLI).

### 7.2 Cursor — `.cursorrules` catalogs

Broader role catalogs (AWS, Terraform, IoT, committee-style mixes) live in:

{{CURSORRULES_PATHS}}

Each `.cursorrules` has a sibling `.agent-workflows.md` describing MLOps /
DevOps stage workflows that Cursor surfaces as slash-commands.

### 7.3 Windsurf / Continue / Aider

These IDEs read the **root `AGENTS.md`** directly — no extra
config required. Keep section 7 up to date and they inherit the agent roster.

### 7.4 Google Antigravity — requirements & AGENTS.md

Antigravity expects:

- `AGENTS.md` at repo root (this file is compatible — symlink it).
- A `requirements/` folder (or `docs/requirements/`) with one Markdown file
  per user story or capability. The Antigravity runner cites them back when
  producing code. Recommended structure:

  ```
  requirements/
  ├── REQ-001-data-ingestion.md
  ├── REQ-002-pattern-classification.md
  └── _index.md        # short catalog with status (draft/active/done)
  ```

  Each file SHOULD contain: `## Context`, `## Acceptance criteria`, and
  `## Non-goals`. Link back to ADRs or knowledge docs in section 9.

### 7.5 Skills library (BP011 bundle)

Reusable **skill** packages (Anthropic-style `SKILL.md` trees) live under:

- `{{SKILL_BUNDLE_PATH}}` — curated skills synced from upstream templates
  (see `skills-lock.json` for versions)
- `.agents/BP011-GenAI-agents/docs/skills/` — process & deployment notes

To attach a skill to a Claude Code subagent, add it to the `skills:` field in
that agent's frontmatter. Prefer **narrow skills** (testing, ADRs, release
notes) over loading the entire tree into context.

---

## 8. Best Practices & Conventions

{{BEST_PRACTICES}}

**Universal rules (do not delete):**

- Never modify files under `data/raw/` or any Bronze-layer source.
- Never commit secrets, credentials, or `.env` files.
- Never skip git hooks (`--no-verify`) or bypass code review.
- Clear notebook outputs before committing.
- Vectorise — avoid Python loops on time-series when numpy/pandas can do it.

---

## 9. Knowledge & Architecture Artifacts

**Authoritative (must read first):**

{{KNOWLEDGE_DOCS}}

**BP011 architecture templates** (fill these out for any new service):

- `.agents/architecture/template_01_vision_general.md`
- `.agents/architecture/template_03_pipeline_datos_ml.md`
- `.agents/architecture/template_05_arquitectura.md`
- `.agents/architecture/template_07_registro_adr.md` *(ADRs)*
- `.agents/architecture/template_09_ml_canvas.md`
- `.agents/architecture/template_10_model_card.md`

**Profiles & scripts** (agent tooling):

- `.agents/profiles/` — opinionated bundles (`data-ml`, `iac`, `committe`)
- `.agents/scripts/apply-profile.sh` — apply a profile to a fresh checkout
- `.agents/scripts/migrate-cursor-project.py` — port Cursor-only repos
- `.agents/scripts/validate-agents.py` — CI check for agent definitions

---

## 10. Common Tasks (copy-paste recipes)

{{COMMON_TASKS}}

---

## 11. Guardrails for AI Assistants

When an AI assistant proposes changes in this repo, it MUST:

1. Read this file **and** the top-3 docs listed in section 9 before editing.
2. Respect the medallion boundaries (`raw → stage → universal → reporting`).
3. Emit new modules under `src/` — never inline business logic in notebooks.
4. For any new pattern / feature / rule, also update the relevant
   `requirements/REQ-*.md` (if Antigravity is in use) **and** the knowledge
   doc in section 9.
5. Prefer the subagent catalog in 7.1 over generic chat for specialised work.
6. Run `.agents/scripts/validate-agents.py` before opening a PR that touches
   `.claude/agents/`, `.cursorrules`, or `AGENTS.md`.

---

*Last updated: {{LAST_UPDATED}} — maintained by {{OWNER_CONTACT}}*
