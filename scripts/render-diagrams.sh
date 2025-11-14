#!/bin/bash

# Exit on error, undefined variables, and pipe failures
set -euo pipefail

# Script to render Mermaid diagrams to PNG and PDF
echo "🎨 Rendering NTAL Architecture Diagrams..."

# Get the project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Set Puppeteer executable path if not already set
# Try common locations for chromium/chrome
if [ -z "${PUPPETEER_EXECUTABLE_PATH:-}" ]; then
    for browser in /usr/bin/chromium /usr/bin/chromium-browser /usr/bin/google-chrome; do
        if [ -x "$browser" ]; then
            export PUPPETEER_EXECUTABLE_PATH="$browser"
            break
        fi
    done
fi

# Define paths
DIAGRAMS_DIR="${PROJECT_ROOT}/docs/architecture/diagrams"
OUTPUT_DIR="${DIAGRAMS_DIR}/out"

# Ensure output directory exists
mkdir -p "${OUTPUT_DIR}"

echo "📁 Input directory: ${DIAGRAMS_DIR}"
echo "📁 Output directory: ${OUTPUT_DIR}"
echo ""

# Find all .mmd files in the diagrams directory
MMD_FILES=("${DIAGRAMS_DIR}"/*.mmd)

if [ ! -e "${MMD_FILES[0]}" ]; then
    echo "❌ No .mmd files found in ${DIAGRAMS_DIR}"
    exit 1
fi

# Counter for rendered files
count=0

# Render each Mermaid file to PNG and PDF
for mmd_file in "${MMD_FILES[@]}"; do
    if [ -f "${mmd_file}" ]; then
        filename=$(basename "${mmd_file}" .mmd)
        echo "🖼️  Rendering: ${filename}"
        
        # Render to PNG
        echo "   → Generating PNG..."
        npx mmdc \
            -i "${mmd_file}" \
            -o "${OUTPUT_DIR}/${filename}.png" \
            -b transparent \
            -w 2048 \
            -H 1536 \
            -p "${PROJECT_ROOT}/puppeteer-config.json"
        
        # Render to PDF
        echo "   → Generating PDF..."
        npx mmdc \
            -i "${mmd_file}" \
            -o "${OUTPUT_DIR}/${filename}.pdf" \
            -w 2048 \
            -H 1536 \
            -p "${PROJECT_ROOT}/puppeteer-config.json"
        
        echo "   ✅ Completed: ${filename}.png and ${filename}.pdf"
        echo ""
        count=$((count + 1))
    fi
done

echo "🎉 Successfully rendered ${count} diagram(s)!"
echo "📂 Output location: ${OUTPUT_DIR}"
echo ""
echo "Generated files:"
ls -lh "${OUTPUT_DIR}"
