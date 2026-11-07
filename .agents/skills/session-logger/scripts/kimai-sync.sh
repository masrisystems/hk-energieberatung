#!/usr/bin/env bash
set -e

# Kimai Sync & REST API Automation (Global / Multi-Project)

CONFIG_FILE="${HOME}/.agents/config/kimai.env"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="${USERPROFILE}/.agents/config/kimai.env"
fi

# Check local repo overrides
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if [ -f "$GIT_ROOT/.kimai.env" ]; then
    CONFIG_FILE="$GIT_ROOT/.kimai.env"
elif [ -f "$GIT_ROOT/kimai.env" ]; then
    CONFIG_FILE="$GIT_ROOT/kimai.env"
fi

if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
fi

KIMAI_URL="${KIMAI_URL%/}"
KIMAI_USER="${KIMAI_USER:-}"
KIMAI_TOKEN="${KIMAI_TOKEN:-}"

DEFAULT_PROJECT="${KIMAI_DEFAULT_PROJECT:-}"
DEFAULT_ACTIVITY="${KIMAI_DEFAULT_ACTIVITY:-}"
DEFAULT_TAGS="${KIMAI_DEFAULT_TAGS:-development}"
BEGIN_TIME="${KIMAI_DEFAULT_BEGIN:-08:30}"
END_TIME="${KIMAI_DEFAULT_END:-17:00}"
TARGET_DATE=$(date +%Y-%m-%d)

DO_TEST=false
DO_POST=false
DO_CSV=false
CUSTOM_DESC=""
DURATION_HOURS=""
REPO_NAME=$(basename "$GIT_ROOT")

usage() {
    echo "Kimai Sync & Import Helper (Multi-Project)"
    echo "Usage: bash kimai-sync.sh [options]"
    echo ""
    echo "Options:"
    echo "  --test                 Test Kimai REST API connection and list projects/activities"
    echo "  --post                 Book timesheet directly via Kimai REST API"
    echo "  --csv                  Generate CSV import file"
    echo "  --date YYYY-MM-DD      Date (default: today $TARGET_DATE)"
    echo "  --begin HH:MM          Begin time (default: $BEGIN_TIME)"
    echo "  --end HH:MM            End time (default: $END_TIME)"
    echo "  --hours <N>            Duration in hours (e.g. --hours 2 or --hours 1.5)"
    echo "  --desc \"Text\"          Description of work"
    echo "  --project <ID>         Project ID override"
    echo "  --activity <ID>        Activity ID override"
    echo "  --tags \"tag1,tag2\"     Tags override"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --test) DO_TEST=true; shift ;;
        --post) DO_POST=true; shift ;;
        --csv)  DO_CSV=true; shift ;;
        --date) TARGET_DATE="$2"; shift 2 ;;
        --begin) BEGIN_TIME="$2"; shift 2 ;;
        --end) END_TIME="$2"; shift 2 ;;
        --hours|--duration) DURATION_HOURS="$2"; shift 2 ;;
        --desc) CUSTOM_DESC="$2"; shift 2 ;;
        --project) TARGET_PROJECT="$2"; shift 2 ;;
        --activity) TARGET_ACTIVITY="$2"; shift 2 ;;
        --tags) TARGET_TAGS="$2"; shift 2 ;;
        --help|-h) usage ;;
        *)
            if [ -z "$CUSTOM_DESC" ]; then
                CUSTOM_DESC="$1"
            fi
            shift
            ;;
    esac
done

TARGET_PROJECT="${TARGET_PROJECT:-$DEFAULT_PROJECT}"
TARGET_ACTIVITY="${TARGET_ACTIVITY:-$DEFAULT_ACTIVITY}"
TARGET_TAGS="${TARGET_TAGS:-$DEFAULT_TAGS}"
if [[ ! "$TARGET_TAGS" =~ $REPO_NAME ]]; then
    TARGET_TAGS="$TARGET_TAGS,$REPO_NAME"
fi

if [ -n "$DURATION_HOURS" ]; then
    CALC_END=$(python3 -c "import datetime; b = datetime.datetime.strptime('$BEGIN_TIME', '%H:%M'); e = b + datetime.timedelta(hours=float('$DURATION_HOURS')); print(e.strftime('%H:%M'))" 2>/dev/null || echo "")
    if [ -n "$CALC_END" ]; then
        END_TIME="$CALC_END"
    fi
fi

if [ "$DO_TEST" = true ]; then
    if [ -z "$KIMAI_URL" ] || [ -z "$KIMAI_USER" ] || [ -z "$KIMAI_TOKEN" ]; then
        echo "Kimai configuration incomplete in $CONFIG_FILE"
        exit 1
    fi
    echo "Testing connection to $KIMAI_URL as user '$KIMAI_USER'..."
    PING=$(curl -s -H "X-AUTH-USER: $KIMAI_USER" -H "X-AUTH-TOKEN: $KIMAI_TOKEN" "$KIMAI_URL/api/ping" || echo "")
    echo "Result: $PING"
    echo ""
    echo "Available Projects:"
    curl -s -H "X-AUTH-USER: $KIMAI_USER" -H "X-AUTH-TOKEN: $KIMAI_TOKEN" "$KIMAI_URL/api/projects" \
        | jq -r '.[] | "  - ID \(.id): \(.name)"' 2>/dev/null || echo "Could not parse projects"
    echo ""
    echo "Available Activities:"
    curl -s -H "X-AUTH-USER: $KIMAI_USER" -H "X-AUTH-TOKEN: $KIMAI_TOKEN" "$KIMAI_URL/api/activities" \
        | jq -r '.[] | "  - ID \(.id): \(.name)"' 2>/dev/null || echo "Could not parse activities"
    exit 0
fi

if [ -z "$CUSTOM_DESC" ]; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    CUSTOM_DESC="Development on $BRANCH in $REPO_NAME"
fi

if [ "$DO_POST" = true ]; then
    ISO_BEGIN="${TARGET_DATE}T${BEGIN_TIME}:00"
    ISO_END="${TARGET_DATE}T${END_TIME}:00"
    PAYLOAD=$(jq -n \
        --arg begin "$ISO_BEGIN" \
        --arg end "$ISO_END" \
        --argjson project "$TARGET_PROJECT" \
        --argjson activity "$TARGET_ACTIVITY" \
        --arg desc "$CUSTOM_DESC" \
        --arg tags "$TARGET_TAGS" \
        '{begin: $begin, end: $end, project: $project, activity: $activity, description: $desc, tags: $tags}')

    echo "Booking time to Kimai ($KIMAI_URL)..."
    RES=$(curl -s -w "%{http_code}" -X POST \
        -H "X-AUTH-USER: $KIMAI_USER" \
        -H "X-AUTH-TOKEN: $KIMAI_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" \
        "$KIMAI_URL/api/timesheets")
    echo "Status: $RES"
    exit 0
fi

if [ "$DO_CSV" = true ]; then
    CSV_FILE="$GIT_ROOT/private/gemini-scribe/kimai-import-${TARGET_DATE}.csv"
    mkdir -p "$(dirname "$CSV_FILE")"
    echo '"date","begin","end","project","activity","description","tags"' > "$CSV_FILE"
    echo "\"$TARGET_DATE\",\"$BEGIN_TIME\",\"$END_TIME\",\"$TARGET_PROJECT\",\"$TARGET_ACTIVITY\",\"$CUSTOM_DESC\",\"$TARGET_TAGS\"" >> "$CSV_FILE"
    echo "CSV created: $CSV_FILE"
    exit 0
fi

echo "================================================================================"
echo "Kimai Note (Copy & Paste):"
echo "--------------------------------------------------------------------------------"
echo "$CUSTOM_DESC"
echo "--------------------------------------------------------------------------------"
echo "Book via API: bash kimai-sync.sh --post --hours 2"
echo "================================================================================"
