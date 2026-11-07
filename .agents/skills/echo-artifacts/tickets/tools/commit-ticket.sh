#!/usr/bin/env bash
# Stagt eine Ticket-Datei und committet sie (inkl. bereits anderweitig gestagter
# Änderungen) mit Commit-Author und -Format gemäß repo-rules.
# Verwendung: commit-ticket.sh <ticket-datei> <commit-message> <author-name> <author-email>

TICKET_FILE="${1:?Erstes Argument fehlt: Pfad zur Ticket-Datei}"
MESSAGE="${2:?Zweites Argument fehlt: Commit-Message, z.B. '(#170) chore(tickets): ... anlegen'}"
AUTHOR_NAME="${3:?Drittes Argument fehlt: Author-Name}"
AUTHOR_EMAIL="${4:?Viertes Argument fehlt: Author-E-Mail}"

REPO_ROOT="$(git -C "$(dirname "$TICKET_FILE")" rev-parse --show-toplevel)"

git -C "$REPO_ROOT" add "$TICKET_FILE"
git -C "$REPO_ROOT" commit -m "$MESSAGE" --author="$AUTHOR_NAME <$AUTHOR_EMAIL>"
