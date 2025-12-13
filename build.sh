#!/bin/bash
# Build .ankiaddon package

set -e

ADDON_DIR="break_reminder"
OUTPUT="break_reminder.ankiaddon"

rm -f "$OUTPUT"

cd "$ADDON_DIR"
zip -r "../$OUTPUT" . \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x "meta.json" \
    -x ".DS_Store"
cd ..

echo "Created $OUTPUT"
unzip -l "$OUTPUT"
