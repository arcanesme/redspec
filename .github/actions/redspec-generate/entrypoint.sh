#!/usr/bin/env bash
set -euo pipefail

YAML_PATTERN="${1:-**/*.yaml}"
OUTPUT_DIR="${2:-./redspec-output}"
FORMAT="${3:-svg}"

mkdir -p "$OUTPUT_DIR"

echo "=== Redspec Generate ==="
echo "Pattern: $YAML_PATTERN"
echo "Output:  $OUTPUT_DIR"
echo "Format:  $FORMAT"

# Find YAML files matching pattern
YAML_FILES=$(find . -name "*.yaml" -o -name "*.yml" | grep -v node_modules | grep -v .git || true)

if [ -z "$YAML_FILES" ]; then
    echo "No YAML files found matching pattern"
    exit 0
fi

SUCCESS=0
FAIL=0

for file in $YAML_FILES; do
    echo "Processing: $file"
    basename=$(basename "$file" .yaml)
    basename=$(echo "$basename" | sed 's/.yml$//')
    output_file="$OUTPUT_DIR/${basename}.${FORMAT}"

    if redspec generate "$file" -o "$output_file" --format "$FORMAT" 2>/dev/null; then
        echo "  OK: $output_file"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "  SKIP: $file (not a valid redspec file or generation failed)"
        FAIL=$((FAIL + 1))
    fi
done

echo ""
echo "=== Results ==="
echo "Generated: $SUCCESS"
echo "Skipped:   $FAIL"
