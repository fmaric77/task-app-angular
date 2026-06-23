#!/usr/bin/env bash
# md_to_docx.sh — Convert a Markdown file to Word (.docx) using pandoc
#
# Usage:
#   bash scripts/md_to_docx.sh INPUT.md [OUTPUT.docx]
#
# If OUTPUT is omitted, uses the same name with .docx extension.
# Optionally set REFERENCE_DOC to a .docx template for custom styling.
#
# Examples:
#   bash scripts/md_to_docx.sh MIGRATION_GUIDE.md
#   bash scripts/md_to_docx.sh MIGRATION_GUIDE.md /mnt/user-data/outputs/MIGRATION_GUIDE.docx
#   REFERENCE_DOC=template.docx bash scripts/md_to_docx.sh report.md

set -euo pipefail

INPUT="${1:?Usage: md_to_docx.sh INPUT.md [OUTPUT.docx]}"
OUTPUT="${2:-${INPUT%.md}.docx}"

if [ ! -f "$INPUT" ]; then
  echo "Error: $INPUT not found" >&2
  exit 1
fi

PANDOC_ARGS=(
  "$INPUT"
  -o "$OUTPUT"
  --from markdown
  --to docx
  --standalone
  --table-of-contents
  --toc-depth=2
  --highlight-style=tango
)

# Use a reference doc for styling if provided
if [ -n "${REFERENCE_DOC:-}" ] && [ -f "$REFERENCE_DOC" ]; then
  PANDOC_ARGS+=(--reference-doc="$REFERENCE_DOC")
fi

pandoc "${PANDOC_ARGS[@]}"

echo "Created: $OUTPUT"
