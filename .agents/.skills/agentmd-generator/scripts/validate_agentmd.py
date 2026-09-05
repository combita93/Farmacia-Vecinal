#!/usr/bin/env python3
"""
validate_agentmd.py
-------------------
Validates that an AGENTS.md file has been correctly populated
by the agentmd-generator skill.

Usage:
    python scripts/validate_agentmd.py [path/to/AGENTS.md]

Exits 0 if valid, 1 if issues found.
"""

import re
import sys
from pathlib import Path

PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z_]+\}\}")

REQUIRED_SECTIONS = [
    "## 1. Project Overview",
    "## 2. Technology Stack",
    "## 3. Repository Layout",
    "## 4. Domain Glossary",
    "## 5. Development Workflows",
    "## 7. AI Agent Configuration",
    "## 8. Best Practices",
    "## 9. Knowledge",
    "## 10. Common Tasks",
    "## 11. Guardrails",
]

MIN_LENGTH = 2000  # characters — a well-populated file should be substantial


def validate(filepath: Path) -> list[str]:
    issues = []

    if not filepath.exists():
        return [f"❌ File not found: {filepath}"]

    content = filepath.read_text(encoding="utf-8")

    # Check length
    if len(content) < MIN_LENGTH:
        issues.append(
            f"⚠️  File seems too short ({len(content)} chars). "
            "Minimum expected: {MIN_LENGTH} chars."
        )

    # Check for unfilled placeholders
    placeholders = PLACEHOLDER_PATTERN.findall(content)
    if placeholders:
        unique = sorted(set(placeholders))
        issues.append(
            f"❌ Unfilled placeholders found ({len(unique)}): " + ", ".join(unique)
        )

    # Check required sections
    for section in REQUIRED_SECTIONS:
        if section not in content:
            issues.append(f"❌ Missing section: {section}")

    # Check that TODO items are disclosed
    todo_count = content.count("TODO")
    if todo_count > 0:
        issues.append(
            f"ℹ️  {todo_count} TODO item(s) found — review and fill before committing."
        )

    return issues


def main():
    path_arg = sys.argv[1] if len(sys.argv) > 1 else "AGENTS.md"
    filepath = Path(path_arg)

    print(f"Validating: {filepath.resolve()}\n")
    issues = validate(filepath)

    if not issues:
        print("✅ AGENTS.md looks good! No issues found.")
        sys.exit(0)
    else:
        print(f"Found {len(issues)} issue(s):\n")
        for issue in issues:
            print(f"  {issue}")
        # Exit 0 even with TODOs (they're warnings); exit 1 only for real errors
        has_errors = any(i.startswith("❌") for i in issues)
        sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
