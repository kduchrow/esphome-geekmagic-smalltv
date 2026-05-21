# esphome-geekmagic-smalltv

ESPHome external component providing a reusable display framework for the GeekMagic SmallTV Ultra (ESP8266, 240x240 ST7789V display with fractional framebuffer). The component manages a page stack with rotation, expiry, header queue, and notification icon. Users interact via ESPHome services (set_page, set_header, set_notification) from Home Assistant automations. Development uses Docker Compose with esphome/esphome image. The component has Python (config schema/codegen) and C++ (display driver) files that must stay in sync. Tested only on GeekMagic SmallTV Ultra.

<!-- agent-meta:managed-begin -->
<!-- This block is automatically updated by sync.py on every sync. -->
<!-- Manual changes here will be overwritten. -->

Generiert von agent-meta v0.46.2 — `2026-05-21`
DoD-Preset: **rapid-prototyping** | REQ-Traceability: false | Tests: false | Codebase-Overview: false | Security-Audit: false

> **Einstiegspunkt:** Starte mit dem `orchestrator`-Agenten für alle Entwicklungsaufgaben.

| Agent | Zuständigkeit |
|-------|--------------|
| `agent-meta-manager` | agent-meta verwalten: Upgrade, Sync, Feedback, projektspezifische Agenten anlegen |
| `developer` | Feature-Implementierung und Bugfixes nach REQ-IDs |
| `documenter` | Doku pflegen: CODEBASE_OVERVIEW, ARCHITECTURE, README, Erkenntnisse |
| `feature` | Feature-Lifecycle-Subagent: Branch → REQ → TDD → Dev → Validate → PR. Wird vom Orchestrator gestartet, nicht direkt vom User. |
| `git` | Commits, Branches, Tags, Push/Pull und alle Git-Operationen |
| `ideation` | Neue Ideen explorieren, Vision schärfen, Übergabe an requirements |
| `log-analyzer` | Log-Analyse: Fehler clustern, Severity klassifizieren (RFC 5424), Findings als Issues oder Tasks delegieren |
| `meta-feedback` | Verbesserungsvorschläge für agent-meta als GitHub Issues einreichen |
| `orchestrator` | Einstiegspunkt für alle Entwicklungsaufgaben — koordiniert alle anderen Agenten |
| `release` | Versioning, Changelog, Build-Artifact, GitHub Release erstellen |
| `requirements` | Anforderungen aufnehmen, REQ-IDs vergeben, REQUIREMENTS.md pflegen |
| `validator` | Interner Qualitäts-Checker: DoD-Checkliste, Traceability-Audit. Wird vom Orchestrator nach der Implementierung aufgerufen. Nicht für direkte User-Fragen oder Setup-Hilfe. |

## Regeln

# Branch-Guard — Feature-Branch Pflicht

**Gilt für alle code-ändernden Aufgaben.**

## Pflicht vor dem ersten Edit

```bash
git branch --show-current
```

Auf `main`/`master` → Branch anlegen: `feat/<thema>` | `fix/<thema>` | `refactor/<thema>`

## Branch PFLICHT wenn

- Mehr als eine Datei geändert
- Inhaltliche Änderung an Templates, Rules, Scripts
- GitHub Issue bearbeitet

**Faustregel: >1 Datei anfassen → Branch.**

## Direkt auf main erlaubt (Ausnahmen)

Nur: Version-Bump (`VERSION`, `CHANGELOG.md`, `README.md`) | einzelner Tippfehler (1 Datei, 1 Zeile, User-Bestätigung) | Post-Merge-Pflege nach Review.

**NIE für:** Templates, Rules, Scripts — egal wie klein. Nie für Issue-Arbeit.

## Warum

Direkte Commits auf main können kaum rückgängig gemacht werden und blockieren andere Entwicklung.

---

# Commit-Konventionen (Conventional Commits)

Gilt für alle Agenten die Commits erstellen oder vorbereiten.

## Format

```
<type>(REQ-xxx): <beschreibung>   ← mit req-traceability
<type>: <beschreibung>            ← ohne req-traceability
```

| Type | Bedeutung | REQ-ID |
|------|-----------|--------|
| `feat` | Neues Feature | Wenn `req-traceability` aktiv |
| `fix` | Bugfix | Wenn `req-traceability` aktiv |
| `refactor` | Refactoring ohne Verhaltensänderung | Wenn `req-traceability` aktiv |
| `test` | Tests hinzufügen/ändern | Wenn `req-traceability` aktiv |
| `chore` | Wartung: Dependencies, Config, Versions-Bumps | **Nie** |
| `docs` | Dokumentation | **Nie** |
| `ci` | CI/CD-Änderungen | **Nie** |

## Regeln

- Beschreibung im **Imperativ**: `add feature`, nicht `added feature`
- Maximal **72 Zeichen** in der ersten Zeile
- Beschreibungssprache: `Englisch`
- Body optional: Was **und warum** geändert wurde

## Beispiele

**Mit req-traceability:**
```
feat(REQ-042): add queue persistence across restarts
fix(REQ-017): prevent duplicate video entries on reconnect
test(REQ-042): add persistence tests
chore: bump version to 1.2.0
docs: update installation instructions
```

**Ohne req-traceability:**
```
feat: add queue persistence across restarts
fix: prevent duplicate video entries on reconnect
chore: bump version to 1.2.0
```

---

# Definition of Done (DoD)

Aufgabe abgeschlossen wenn alle **aktiven** Kriterien erfüllt sind.

## Immer Pflicht

- [ ] Code implementiert die Aufgabe vollständig
- [ ] Code-Konventionen eingehalten
- [ ] Commit-Message im Conventional-Commits-Format
- [ ] Keine Regressions

{{#if DOD_REQ_TRACEABILITY}}
## REQ-Traceability

- [ ] REQ-ID existiert in `docs/REQUIREMENTS.md`
- [ ] Commit-Format: `<type>(REQ-xxx): <beschreibung>`
{{/if}}

{{#if DOD_TESTS_REQUIRED}}
## Tests

- [ ] Test vorhanden und grün
{{/if}}

{{#if DOD_CODEBASE_OVERVIEW}}
## Dokumentation

- [ ] `CODEBASE_OVERVIEW.md` aktualisiert
{{/if}}

{{#if DOD_SECURITY_AUDIT}}
## Security

- [ ] Security-Audit vor Release durchgeführt
{{/if}}

**Keine finale Antwort und keine Commit-Empfehlung** ohne Prüfung aller aktiven Kriterien.

---

# GitHub Issue Lifecycle

Wenn deine Arbeit mit einem GitHub Issue verknüpft ist, schließe es nach Abschluss ab.

## Pflicht nach erledigter Arbeit

1. **Kommentiere das Issue** — kurze Zusammenfassung was implementiert wurde und in welchem Commit
2. **Schließe das Issue** — `gh issue close <number>`

```bash
# Kommentar + schließen in einem Schritt
gh issue close <number> --comment "Implemented in <commit>: <one-line summary>"

# Oder separat (wenn ausführlicherer Kommentar gewünscht)
gh issue comment <number> --body "..."
gh issue close <number>
```

## Wann gilt das?

- Nach jedem abgeschlossenen Feature, Bugfix oder Task der einem Issue zugeordnet ist
- Auch wenn kein PR erstellt wird (direkte Commits auf main)
- Der `git`-Agent kennt den vollständigen Workflow (inkl. Formulierungshilfe)

## Commit-Message-Referenz

Issue-Referenzen in Commit-Messages sind optional, aber empfohlen:
```
feat(REQ-042): add queue persistence  (closes #22)
```

## Delegation

Für GitHub-Operationen → `git`-Agent

---

# Sprachregeln

Diese Regel gilt für alle Agenten und den Hauptchat.

## Sprachzuordnung

| Kontext | Sprache |
|---------|---------|
| Kommunikation mit dem Nutzer | **Deutsch** |
| Nutzer-Eingaben verstehen | **Deutsch** |
| Externe Dokumente (README, CHANGELOG, Release Notes, GitHub Issues) | **Englisch** |
| Interne Dokumente (CODEBASE_OVERVIEW, ARCHITECTURE, REQUIREMENTS, Berichte) | **Deutsch** |
| Code-nahe Artefakte (Kommentare, Commit-Messages, Test-Beschreibungen) | **Englisch** |

## Rollenspezifische Präzisierungen

Agenten-Templates können zusätzliche Präzisierungen für ihren spezifischen Output-Typ enthalten
(z.B. welche Datei unter welche Kategorie fällt). Diese Regel definiert den Rahmen — die
rollenspezifische Zuordnung konkretisiert ihn.

---

# Lifecycle-Tasks — Ausstehende Aufgaben prüfen

Beim Start einer neuen Konversation: prüfe ob `.opencode/pending-tasks.md` existiert.

## Pflicht beim Konversations-Start

```bash
# Prüfen ob Lifecycle-Tasks ausstehen
test -f .opencode/pending-tasks.md && cat .opencode/pending-tasks.md
```

Wenn die Datei existiert und offene Tasks enthält (`- [ ]`):

1. Informiere den User:
   > "Es gibt ausstehende Lifecycle-Tasks aus einem Git-Event. Soll ich diese jetzt bearbeiten?"

2. Zeige die offenen Tasks kompakt (Agent + Aufgabe, eine Zeile je Task).

3. Wenn User bestätigt → delegiere Tasks an die genannten Agenten.

4. Nach Erledigung aller Tasks: lösche `.opencode/pending-tasks.md`.

## Wann diese Rule greift

Lifecycle-Tasks entstehen wenn der `lifecycle-check`-Hook aktiv ist und ein konfiguriertes
Git-Event erkannt wird (z.B. Release-Tag, Version-Bump, Merge).

Konfiguration in `.meta-config/project.yaml`:
```yaml
lifecycle-triggers:
  on-release:
    - agent: documenter
      task: "Update CODEBASE_OVERVIEW.md and ARCHITECTURE.md for this release."
  on-merge:
    - agent: validator
      task: "Quick DoD check for merged changes."
```

## Wenn keine Tasks offen sind

Datei existiert nicht oder enthält keine `- [ ]` Zeilen → nichts tun.
Datei nicht committen — sie ist gitignored (`.opencode/pending-tasks.md`).

---

# Session-Abschluss — Erkenntnisse sichern

Gilt für Hauptchat und Orchestrator.

## Session-Ende erkennen

Signale dass eine Session abgeschlossen ist:

- User sagt "tschüss", "bye", "bis später", "fertig", "done", "das war's"
- User fragt nach einem Commit oder Push (Task ist abgeschlossen)
- User wechselt explizit das Thema zu etwas Unverbundenem
- User fragt "was haben wir heute gemacht?"

## Pflicht bei Session-Ende

Wenn ein Signal erkannt wird und in der Session etwas Nennenswertes passiert ist
(Code geändert, Architektur-Entscheid getroffen, Bug analysiert, Feature implementiert):

> "Session abschließen? Ich kann die Erkenntnisse an den documenter-Agenten delegieren."

Bei Bestätigung → `documenter` mit Session-Zusammenfassung delegieren:
- Was wurde implementiert / gefixt / entschieden
- Offene Punkte / Follow-ups
- Wichtige Erkenntnisse (Probleme, Lösungsansätze, Architektur-Änderungen)

## Wann NICHT fragen

- Kurze Fragen ohne Code-Änderungen (nur Erklärungen, Reviews ohne Fixes)
- User hat Erkenntnisse bereits explizit gespeichert
- Session war trivial (1 Datei, 1 Zeile Fix)

---

# Orchestrator — Pflichtnutzung

Einstiegspunkt für alle Entwicklungsaufgaben: `orchestrator`-Agent.

## Immer Orchestrator

Feature | Bugfix | Refactoring | Anforderungen | Tests | Audit | Release | Docker | Ideation | Analyse | Design

> **Der Orchestrator wählt automatisch das kosteneffizienteste Model-Tier** für jede Delegation (nano → fast → balanced → powerful → max). Nie direkt an teurere Agenten delegieren als nötig.

## Ausnahmen — direkt an

| Aufgabe | Agent |
|---------|-------|
| Git-Operationen (Commit, Push, Branch, Tag, PR) | `git` |
| Erkenntnisse speichern (Session-Ende) | `documenter` |
| agent-meta Upgrade / Sync / Extension / Meta-Fragen | `agent-meta-manager` |
| Projekt-Feedback als GitHub Issue einreichen | `feedback` |

## Was NIE direkt an andere Agenten geht

| Falsch | Richtig |
|--------|---------|
| "Wie funktioniert der Sync?" → `git` | → `agent-meta-manager` |
| "Ist mein Code gut?" → `validator` | → `orchestrator` (der entscheidet ob/wann `validator`) |
| "Erstelle ein Feature" → `feature` (direkt) | → `orchestrator` (der startet `feature`) |
| "Was bedeutet diese Rule?" → `validator` | → `agent-meta-manager` |
| "Analysiere die Codebase" → im Hauptchat | → `orchestrator` → `ideation` |
| "Entwirf ein Konzept" → im Hauptchat | → `orchestrator` → `ideation` |

## Hauptchat ohne Orchestrator

Branch-Guard manuell: `git branch --show-current` — auf `main` → Branch anlegen.
<!-- agent-meta:managed-end -->

## Agents

Agent files are in `.opencode/agents/`. Invoke them by name in opencode.

## Project Setup

- **Build:** `docker compose run --rm esphome compile my_examples/displayarbeitszimmer.dev.yaml`
- **Test:** `docker compose run --rm esphome config my_examples/displayarbeitszimmer.dev.yaml`
- **Platform:** ESPHome External Component (ESP8266 + ST7789V)
- **Runtime:** ESPHome 2026.x (ESP8266, C++/Python)
