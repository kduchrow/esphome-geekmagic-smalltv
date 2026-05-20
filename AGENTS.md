# esphome-geekmagic-smalltv

ESPHome external component providing a reusable display framework for the GeekMagic SmallTV Ultra (ESP8266, 240x240 ST7789V display with fractional framebuffer). The component manages a page stack with rotation, expiry, header queue, and notification icon. Users interact via ESPHome services (set_page, set_header, set_notification) from Home Assistant automations. Development uses Docker Compose with esphome/esphome image. The component has Python (config schema/codegen) and C++ (display driver) files that must stay in sync. Tested only on GeekMagic SmallTV Ultra.

<!-- agent-meta:managed-begin -->
<!-- This block is automatically updated by sync.py on every sync. -->
<!-- Manual changes here will be overwritten. -->

Generiert von agent-meta v0.45.0 — `2026-05-20`
DoD-Preset: **rapid-prototyping** | REQ-Traceability: false | Tests: false | Codebase-Overview: false | Security-Audit: false

> **Einstiegspunkt:** Starte mit dem `orchestrator`-Agenten für alle Entwicklungsaufgaben.

| Agent | Zuständigkeit |
|-------|--------------|
| `agent-meta-manager` | agent-meta verwalten: Upgrade, Sync, Feedback, projektspezifische Agenten anlegen |
| `developer` | Feature-Implementierung und Bugfixes nach REQ-IDs |
| `documenter` | Doku pflegen: CODEBASE_OVERVIEW, ARCHITECTURE, README, Erkenntnisse |
| `feature` | Neues Feature end-to-end durchführen: Branch → REQ → TDD → Dev → Validate → PR |
| `git` | Commits, Branches, Tags, Push/Pull und alle Git-Operationen |
| `ideation` | Neue Ideen explorieren, Vision schärfen, Übergabe an requirements |
| `log-analyzer` | Log-Analyse: Fehler clustern, Severity klassifizieren (RFC 5424), Findings als Issues oder Tasks delegieren |
| `meta-feedback` | Verbesserungsvorschläge für agent-meta als GitHub Issues einreichen |
| `orchestrator` | Einstiegspunkt für alle Entwicklungsaufgaben — koordiniert alle anderen Agenten |
| `release` | Versioning, Changelog, Build-Artifact, GitHub Release erstellen |
| `requirements` | Anforderungen aufnehmen, REQ-IDs vergeben, REQUIREMENTS.md pflegen |
| `reviewer` | Code-Review: Qualität, Stil, Logik, Best Practices — vor dem Merge |
| `validator` | Code gegen REQs prüfen, DoD-Checkliste, Traceability-Audit |

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

# Multi-Repo Workspace Conventions

> Activated when `WORKSPACE_REPOS` is configured in `project.yaml`.

## Rules

1. **Agent files live ONLY in the meta-repo root.**
   - Never create `.claude/`, `.opencode/`, `.continue/`, `.gemini/` directories in sibling repos.
   - All agent configuration is managed centrally in the meta-repo.

2. **Use absolute or relative paths from the meta-repo root.**
   - Sibling repos: `../sharkord-vid-with-friends/src/index.ts`
   - Always verify the working directory before running commands.

3. **Build and test commands must run in the correct repo directory.**
   - Example: `cd ../sharkord-vid-with-friends && bun test`

4. **Workspace-level documentation belongs in the meta-repo.**
   - Cross-plugin conventions → `docs/CONVENTIONS.md`
   - Cross-plugin patterns → `docs/PATTERNS.md`
   - Lessons learned → `docs/LEARNINGS.md`
   - Plugin-specific docs → stay in the respective plugin repo

5. **Standardized learning capture.**
   - When a developer discovers a pattern or solves a bug, use `.agent-meta/templates/learning-capture.md`
   - Propose adding it to the meta-repo's `docs/LEARNINGS.md`

## VS Code Workspace (Optional)

If using VS Code, create a `.code-workspace` file in the meta-repo root:

```json
{
  "folders": [
    { "name": "sharkord-meta", "path": "." },
    { "name": "vid-with-friends", "path": "../sharkord-vid-with-friends" },
    { "name": "stream-with-friends", "path": "../sharkord-stream-with-friends" },
    { "name": "hero-introducer", "path": "../sharkord-hero-introducer" }
  ]
}
```

## Cross-Repo Operations

When delegating to agents for cross-repo work:

```
Delegiere an: developer
Aufgabe: Editiere ../sharkord-vid-with-friends/src/index.ts
         Arbeitsverzeichnis: ../sharkord-vid-with-friends/
```

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

Feature | Bugfix | Refactoring | Anforderungen | Tests | Audit | Release | Docker | Ideation

## Routing-Signale — wann welcher Agent

### Explorative / Research-Fragen → `ideation`

Direkt an `ideation` delegieren (nicht inline beantworten) wenn:

- Frage beginnt mit "Wie könnte ich...", "Was wäre wenn...", "Welche Möglichkeiten gibt es..."
- Expliziter Recherche-Wunsch: "Recherchiere...", "Suche Beispiele...", "Vergleiche Ansätze..."
- WebSearch/WebFetch nötig (externe Quellen, Best Practices, andere Projekte)
- Frage hat keinen konkreten Implementierungs-Scope (kein Ticket, kein Code-Pfad)

**Grenze:** Wenn eine Frage direkt in einem laufenden Task beantwortet werden kann (≤2 Sätze, kein Research nötig) → inline. Sonst → `ideation`.

### Log-Analyse → `log-analyzer`

Bei: Fehler-Logs, Stack Traces, Produktions-Incidents, Monitoring-Daten analysieren.

### Performance → `performance`

Bei: "ist langsam", "zu viel Memory", "Bottleneck finden", "profilen".

### Code-Review → `reviewer`

Bei: PR-Review, "schau dir den Code an", "ist das gut implementiert?", vor dem Merge.

## Ausnahmen — direkt an

| Aufgabe | Agent |
|---------|-------|
| Git-Commit / Push / Tag / Frage | `git` |
| Erkenntnisse speichern | `documenter` |
| agent-meta Upgrade / Sync | `agent-meta-manager` |
| Projekt-Feedback einreichen (Bugs, Features) | `feedback` |
| agent-meta-Feedback einreichen | `meta-feedback` |
| Neues Feature (≥3 Dateien, Lifecycle) | `feature` → delegiert an `developer` |

> **`feature` vs. `developer`:**
> - `feature` koordiniert den gesamten Lifecycle (Branch, REQ, Dev, Test, PR) — implementiert **nichts** selbst
> - `developer` implementiert und fixt direkt
> - Bei parallelen unabhängigen Teilaufgaben: mehrere `developer` via Map-Reduce statt einem `feature`
> - **ENTWICKLUNGSARBEITEN IMMER DURCH `developer`** — auch 1 Datei, wenn inhaltlich (kein Tippfehler)
> - Faustregel: Tippfehler (1 Datei, 1 Zeile) → selbst | Alles andere → `developer` | Lifecycle nötig → `feature`

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
