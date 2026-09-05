# agents.md — Format Specification Reference

Source: https://agents.md/ and https://agents.md/spec

---

## What is AGENTS.md?

A plain Markdown file placed at the **repo root** that gives AI coding agents the
context they need to work on your project. Think of it as a README for agents.

Used by **60k+ open-source projects** and supported by every major AI coding tool:
Codex, Jules, Aider, Goose, Cursor, Windsurf, VS Code Copilot, Devin, Junie, Warp,
RooCode, Amp, Gemini CLI, Augment Code, Continue, and Claude Code.

---

## File names accepted by each tool

| File name | Tools that read it |
|-----------|-------------------|
| `AGENTS.md` | Codex, Jules, Aider, Goose, Devin, Junie, Warp, RooCode, Amp, Gemini CLI, Augment, Continue, GitHub Copilot, Cursor, Windsurf, VS Code, Claude Code |

**Recommendation**: maintain a single `AGENTS.md`.

---

## Recommended sections

There is no enforced schema — write whatever helps agents. Commonly used sections:

```markdown
## Project overview
## Tech stack
## Repository structure
## Domain glossary
## Development workflows / setup commands
## Code style & conventions
## Testing instructions
## PR / commit guidelines
## AI agent configuration
## Architecture references
## Common tasks (recipes)
## Guardrails
```

---

## Best practices

- **Be specific** — vague instructions ("write clean code") are useless to agents.
- **Include runnable commands** — agents can execute them directly.
- **List what NOT to do** — guardrails prevent costly mistakes.
- **Keep it updated** — stale context is worse than none.
- **Commit it** — AGENTS.md benefits the whole team, not just you.
- **Use headings and code blocks** — agents parse structure better than prose.

---

## Multi-IDE compatibility checklist

- [ ] `AGENTS.md` exists at repo root
- [ ] No `{{PLACEHOLDER}}` tokens remain
- [ ] All shell commands are tested and runnable
- [ ] Secrets are NOT included — only references to env var names
- [ ] File is committed to the default branch

---

## Relation to AGENTS_template.md template (this skill's template)

The `AGENTS_template.md` used by this skill is a superset of the basic `AGENTS.md`
format. It adds:
- Multi-IDE agent configuration (§7)
- Subagent catalog for Claude Code (§7.1)
- Cursor `.cursorrules` integration (§7.2)
- Google Antigravity `requirements/` folder spec (§7.4)
- Skills library integration (§7.5)
- Medallion data architecture guardrails (§8, §11)

These extras are ignored gracefully by tools that don't understand them, making
the file fully backwards-compatible.
