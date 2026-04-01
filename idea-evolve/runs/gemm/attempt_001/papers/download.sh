#!/bin/bash
# Download an academic paper and extract text for LLM consumption.
#
# Usage: ./download.sh <arxiv_id|doi|url> [output_name]
#
# Saves PDF to papers/pdf/ and extracts readable text to papers/md/
# The md/ version is what agents should read (faster, cheaper than PDF parsing).
#
# Examples:
#   ./download.sh 2301.12345
#   ./download.sh 10.1090/proc/12345
#   ./download.sh https://arxiv.org/pdf/2301.12345.pdf

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PDF_DIR="$SCRIPT_DIR/pdf"
MD_DIR="$SCRIPT_DIR/md"
mkdir -p "$PDF_DIR" "$MD_DIR"

INPUT="$1"
OUTPUT_NAME="${2:-}"

# Detect input type and normalize
if [[ "$INPUT" =~ ^[0-9]{4}\.[0-9]{4,5}(v[0-9]+)?$ ]]; then
    ARXIV_ID="$INPUT"
    URL="https://arxiv.org/pdf/${ARXIV_ID}.pdf"
    [ -z "$OUTPUT_NAME" ] && OUTPUT_NAME="arxiv_${ARXIV_ID//\//_}"
elif [[ "$INPUT" =~ arxiv.org/(abs|pdf)/([0-9]{4}\.[0-9]{4,5}) ]]; then
    ARXIV_ID="${BASH_REMATCH[2]}"
    URL="https://arxiv.org/pdf/${ARXIV_ID}.pdf"
    [ -z "$OUTPUT_NAME" ] && OUTPUT_NAME="arxiv_${ARXIV_ID//\//_}"
elif [[ "$INPUT" =~ ^10\. ]]; then
    DOI="$INPUT"
    [ -z "$OUTPUT_NAME" ] && OUTPUT_NAME="doi_${DOI//\//_}"
    for mirror in "https://sci-hub.se" "https://sci-hub.st" "https://sci-hub.ru"; do
        echo "Trying ${mirror}/${DOI} ..."
        if curl -sL -o "$PDF_DIR/${OUTPUT_NAME}.pdf" -w "%{http_code}" "${mirror}/${DOI}" | grep -q "200"; then
            if file "$PDF_DIR/${OUTPUT_NAME}.pdf" | grep -q PDF; then
                echo "Downloaded: $PDF_DIR/${OUTPUT_NAME}.pdf"
                URL="done"
                break
            fi
        fi
    done
    if [ "$URL" != "done" ]; then
        echo "ERROR: Could not download DOI $DOI"
        rm -f "$PDF_DIR/${OUTPUT_NAME}.pdf"
        exit 1
    fi
elif [[ "$INPUT" =~ ^https?:// ]]; then
    URL="$INPUT"
    [ -z "$OUTPUT_NAME" ] && OUTPUT_NAME="paper_$(echo "$INPUT" | md5sum | head -c 12)"
else
    echo "ERROR: Unrecognized format. Use arXiv ID, DOI, or URL."
    exit 1
fi

# Download PDF (if not already done by DOI handler)
if [ "${URL:-}" != "done" ]; then
    echo "Downloading: $URL"
    curl -sL -o "$PDF_DIR/${OUTPUT_NAME}.pdf" "$URL"
    if ! file "$PDF_DIR/${OUTPUT_NAME}.pdf" | grep -q PDF; then
        echo "WARNING: Downloaded file may not be a valid PDF"
        file "$PDF_DIR/${OUTPUT_NAME}.pdf"
    fi
fi

# Extract text to markdown
# Try pdftotext first (poppler-utils), fall back to python
MD_FILE="$MD_DIR/${OUTPUT_NAME}.md"
if command -v pdftotext &>/dev/null; then
    echo "Extracting text with pdftotext..."
    pdftotext -layout "$PDF_DIR/${OUTPUT_NAME}.pdf" - > "$MD_FILE" 2>/dev/null
elif python3 -c "import subprocess" &>/dev/null; then
    echo "Extracting text with python..."
    python3 -c "
import subprocess, sys
try:
    result = subprocess.run(['pdftotext', '-layout', '$PDF_DIR/${OUTPUT_NAME}.pdf', '-'],
                          capture_output=True, text=True)
    print(result.stdout)
except FileNotFoundError:
    print('# Could not extract text — pdftotext not available')
    print('# Read the PDF directly: $PDF_DIR/${OUTPUT_NAME}.pdf')
" > "$MD_FILE"
fi

# Add metadata header
if [ -f "$MD_FILE" ]; then
    TMPFILE=$(mktemp)
    {
        echo "---"
        echo "source: $INPUT"
        echo "pdf: $PDF_DIR/${OUTPUT_NAME}.pdf"
        echo "downloaded: $(date -Iseconds)"
        echo "---"
        echo ""
        cat "$MD_FILE"
    } > "$TMPFILE"
    mv "$TMPFILE" "$MD_FILE"
    echo "Text extracted: $MD_FILE"
else
    echo "WARNING: Text extraction failed. Read the PDF directly."
fi

echo ""
echo "=== Files ==="
echo "  PDF: $PDF_DIR/${OUTPUT_NAME}.pdf"
echo "  Text: $MD_FILE"
echo ""
echo "To read: use Read tool on $MD_FILE (preferred) or $PDF_DIR/${OUTPUT_NAME}.pdf"
