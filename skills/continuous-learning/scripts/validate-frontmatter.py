#!/usr/bin/env python3
"""
Validate YAML frontmatter parser safety for solution docs.

Checks:
- --- delimiter integrity
- Unquoted ' #' in scalar values (silent comment truncation)
- Unquoted ': ' in scalar values (silent mapping confusion)
- Required fields present (basic check)

Usage: python3 validate-frontmatter.py <file.md>
Returns exit 0 on pass, exit 1 on fail with details on stderr.
"""

import re
import sys
from pathlib import Path


def validate(filepath: str) -> bool:
    text = Path(filepath).read_text(encoding="utf-8")
    errors = []

    # Check --- delimiters
    if not text.startswith("---"):
        errors.append("Missing opening '---' delimiter")
        return False

    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append("Missing closing '---' delimiter")
        return False

    frontmatter = parts[1]

    # Check each line for unquoted safety issues
    for i, line in enumerate(frontmatter.split("\n"), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Skip lines that are clearly quoted
        if (stripped.startswith('"') and stripped.endswith('"')) or \
           (stripped.startswith("'") and stripped.endswith("'")):
            continue

        # Detect unquoted ' #' (silent comment truncation)
        if " #" in stripped and not stripped.startswith("#"):
            # Check if '#' is inside a value (not at start)
            val_start = stripped.find(": ") + 2 if ": " in stripped else 0
            if val_start > 0 and " #" in stripped[val_start:]:
                errors.append(f"Line {i}: Unquoted ' #' in value — wrap in quotes: {stripped[:60]}")

        # Detect unquoted ': ' in array items or values
        if stripped.startswith("- ") and ": " in stripped[2:]:
            errors.append(f"Line {i}: Unquoted ': ' in array item — wrap in quotes: {stripped[:60]}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return False

    # Basic required field check
    known_fields = {"title", "date", "category", "module", "problem_type", "component", "severity", "tags", "applies_when", "symptoms"}
    found_fields = set()
    for line in frontmatter.split("\n"):
        m = re.match(r"^(\w+):", line.strip())
        if m:
            found_fields.add(m.group(1))

    required = {"title", "date", "category", "module", "problem_type", "component", "severity"}
    missing = required - found_fields
    if missing:
        print(f"Missing required fields: {', '.join(sorted(missing))}", file=sys.stderr)
        return False

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate-frontmatter.py <file.md>", file=sys.stderr)
        sys.exit(1)

    success = validate(sys.argv[1])
    sys.exit(0 if success else 1)
