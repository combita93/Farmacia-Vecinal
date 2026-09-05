# File references

When referencing other files in your skill, use relative paths from the skill root:

```markdown SKILL.md theme={null}
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.
