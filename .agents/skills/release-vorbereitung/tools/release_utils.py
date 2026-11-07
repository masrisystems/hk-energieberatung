#!/usr/bin/env python3
"""Deterministische Hilfsfunktionen für den Skill release-vorbereitung.

Deckt die Teile der Mechanik ab, die keine fachliche Einschätzung erfordern:
Versionsnormalisierung, Milestone-Namensabgleich, Dedup der Release-Menge,
Branchname. Der Rest der Mechanik (Artefaktprüfung, Changelog-Formulierung)
bleibt Agentenaufgabe gemäß SKILL.md.
"""
import re
import sys

_SEMVER_RE = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')


def normalize_version(raw):
    """Entfernt ein führendes 'v' und prüft auf vollständige Semantic Version.

    Wirft ValueError bei unvollständigem oder nicht-numerischem Wert.
    """
    value = raw[1:] if raw[:1] in ('v', 'V') else raw
    if not _SEMVER_RE.match(value):
        raise ValueError(f"'{raw}' ist keine vollständige Semantic Version (MAJOR.MINOR.PATCH)")
    return value


def version_parts(normalized_version):
    """Zerlegt eine normalisierte Version in (major, minor, patch) als int."""
    major, minor, patch = normalized_version.split('.')
    return int(major), int(minor), int(patch)


def milestone_matches(milestone_name, normalized_version):
    """True, wenn normalized_version als eigenständiger Bestandteil in milestone_name vorkommt.

    'eigenständig' heißt: das Zeichen vor und nach dem Treffer ist kein Ziffern- oder
    Punktzeichen (oder Stringanfang/-ende) — verhindert, dass z.B. '2.4.1' auf einen
    Milestone-Namen mit '2.4.12' passt.
    """
    pattern = re.escape(normalized_version)
    for match in re.finditer(pattern, milestone_name):
        start, end = match.start(), match.end()
        before = milestone_name[start - 1] if start > 0 else None
        after = milestone_name[end] if end < len(milestone_name) else None
        boundary_digits = set('0123456789.')
        if before not in boundary_digits and after not in boundary_digits:
            return True
    return False


def dedupe_tickets(ticket_lists, key='iid'):
    """Bildet die Vereinigungsmenge mehrerer Ticketlisten, dedupliziert über `key`."""
    seen = set()
    result = []
    for tickets in ticket_lists:
        for ticket in tickets:
            ticket_key = ticket[key]
            if ticket_key not in seen:
                seen.add(ticket_key)
                result.append(ticket)
    return result


def branch_name(normalized_version):
    return f"release/{normalized_version}"


def main():
    if len(sys.argv) < 3:
        print("Usage: release_utils.py <normalize_version|branch_name> <value>")
        print("       release_utils.py milestone_matches <milestone_name> <version>")
        sys.exit(1)

    command = sys.argv[1]
    if command == 'normalize_version':
        print(normalize_version(sys.argv[2]))
    elif command == 'branch_name':
        print(branch_name(normalize_version(sys.argv[2])))
    elif command == 'milestone_matches':
        if len(sys.argv) < 4:
            print("Usage: release_utils.py milestone_matches <milestone_name> <version>")
            sys.exit(1)
        print(milestone_matches(sys.argv[2], normalize_version(sys.argv[3])))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
