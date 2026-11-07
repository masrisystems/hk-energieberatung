---
name: skill-entwicklung
description: Führt durch die Erstellung oder Überarbeitung einer SKILL.md-Datei nach dem Framework-Standard. Verwenden, wenn ein neuer Skill angelegt oder eine bestehende SKILL.md inhaltlich überarbeitet werden soll.
---

# skill-entwicklung

## Ablauf

1. **Agentengrenze prüfen:** „Mechanik vor Agentenanweisung" aus
   `.agent/professions/konstrukteur.md` anwenden. Nur der danach verbleibende agentische
   Anteil wird als Skill ausgefüllt.

2. **Template laden:** `.agent/templates/skill.md`

3. **YAML-Frontmatter ausfüllen:**
   - `name`: kebab-case, max. 64 Zeichen
   - `description`: dritte Person, "was der Skill tut + wann er zu verwenden ist", max. 1024 Zeichen

4. **Body schreiben** nach den Schicht-1-Prinzipien aus `.agent/professions/konstrukteur.md`

5. **Constraints prüfen:**
   - Body gesamt: max. 500 Zeilen
   - Referenzen: max. eine Ebene tief ab SKILL.md
   - Referenzierte Dateien mit mehr als 100 Zeilen: Inhaltsverzeichnis am Anfang
