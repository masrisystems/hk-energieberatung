#!/usr/bin/env bash
set -e

DATE_STR=$(date +%Y-%m-%d)
TIME_STR=$(date +%H:%M)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
TICKET_ID=$(echo "$CURRENT_BRANCH" | grep -oE '[A-Za-z]+-[0-9]+' | tr '[:lower:]' '[:upper:]' || true)

DO_POST=false
HOURS=""
ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --post) DO_POST=true; shift ;;
        --hours) HOURS="$2"; shift 2 ;;
        *) ARGS+=("$1"); shift ;;
    esac
done

SUMMARY="${ARGS[*]}"
if [ -z "$SUMMARY" ]; then
    SUMMARY="Development work on $CURRENT_BRANCH"
fi

TICKET_TAG=""
if [ -n "$TICKET_ID" ]; then
    TICKET_TAG="[$TICKET_ID] "
fi

# Scribe dir: $KIMAI_SCRIBE_DIR wins, else <repo-root>/private/gemini-scribe, else <cwd>/private/gemini-scribe
SCRIBE_DIR="${KIMAI_SCRIBE_DIR:-}"
if [ -z "$SCRIBE_DIR" ]; then
    ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
    SCRIBE_DIR="$ROOT/private/gemini-scribe"
fi

mkdir -p "$SCRIBE_DIR"
LOG_FILE="$SCRIBE_DIR/${DATE_STR}-session.md"

cat << EOF >> "$LOG_FILE"

### 🕒 $TIME_STR — Branch: $CURRENT_BRANCH
- **Summary:** $SUMMARY
- **Kimai Note:** $TICKET_TAG$SUMMARY
EOF

echo "✅ Session logged to $LOG_FILE"
echo ""
echo "📋 Kimai Timesheet Copy-Paste Entry:"
echo "--------------------------------------------------------"
echo "$TICKET_TAG$SUMMARY"
echo "--------------------------------------------------------"

if [ "$DO_POST" = true ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$SCRIPT_DIR/kimai-sync.sh" ]; then
        SYNC_ARGS=("--post" "--desc" "$TICKET_TAG$SUMMARY")
        if [ -n "$HOURS" ]; then
            SYNC_ARGS+=("--hours" "$HOURS")
        fi
        bash "$SCRIPT_DIR/kimai-sync.sh" "${SYNC_ARGS[@]}"
    fi
fi
