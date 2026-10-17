# Contributing to doc-services / Mitwirken an doc-services

[English](#english) · [Deutsch](#deutsch)

---

<a id="english"></a>
## English

Thank you for your interest in contributing to `doc-services`! This repository provides BACH-independent document extraction, AGPL-free OCR, and content-based privacy screening for local LLM pipelines and autonomous agents.

### 1. Architectural & Engineering Principles

Contributions must preserve the repository's core runtime invariants:

- **INV-LOCAL-01 (Zero-Egress):** All document processing, OCR, and privacy screening routines must run strictly locally. Outbound network sockets, analytics, telemetry, or remote API calls are strictly forbidden.
- **INV-LOCAL-02 (RunAsInvoker):** All operations must execute in unprivileged user mode without requiring root or administrator elevation.
- **INV-LOCAL-03 (Zero-AGPL):** PDF rendering and OCR rasterization must use `pypdfium2` (BSD/Apache) exclusively. Under no circumstances may PyMuPDF (`fitz`, AGPL) or other copyleft libraries be introduced.
- **INV-LOCAL-04 (Fail-Closed Privacy Gate):** Content inspection (`darf_weitergegeben_werden()`) must remain fail-closed: sensitive findings (RED/YELLOW) must block data propagation by default. Diagnostic reports must always mask raw secrets.
- **INV-LOCAL-05 (Merged Cell Deduplication):** DOCX extraction must deduplicate merged table cells via the underlying XML `tc` element identity to prevent token explosion.
- **INV-LOCAL-06 (CI Hardening):** All workflows in `.github/workflows/` must enforce `timeout-minutes` and concurrency cancellation (`cancel-in-progress: true`).
- **INV-LOCAL-07 (Multi-Host Sync Protection):** `.gitignore` must guard against cloud-sync conflict copies and lock leaks across multi-device developer fleets.
- **INV-LOCAL-08 (PEP 621 Standardisation):** Package configuration and URLs in `pyproject.toml` adhere to standard modern packaging specifications.
- **INV-LOCAL-09 (Version Immutability per T-20260920-167562623):** Maintenance and marketing runs (Pfad A / Pfad B) must **never** bump the `version` field. Version increments are reserved exclusively for dedicated, authorized release cycles.
- **INV-SLA-10 (48h Security Response SLA):** Maintainers commit to a binding 48-hour response SLA and 5-day triage commitment for security and privacy reports.

### 2. Development Workflow (Plan D)

- **Source of Truth:** Code is developed, tested, and committed in local Git clones (`C:\_Local_DEV\repos\doc-services`) and pushed to GitHub `origin/main`.
- **Pre-Commit Quality Gates:**
  ```bash
  # 1. Run all tests (must be 100% green)
  python -m pytest -ra -v

  # 2. Lint and format checks
  python -m ruff check .

  # 3. Bytecode syntax compilation
  python -m compileall -q doc_services tests docs

  # 4. Verify whitespace and diff clean
  git diff --check
  ```

### 3. Statutory Notice & Disclaimer (§ 521 BGB)

Contributions are made available as open-source software free of charge under the MIT License. In accordance with German statutory law on gratuitous services (§ 521 BGB - *Gefälligkeitsrecht*), maintainers are liable only for intent and gross negligence.

---

<a id="deutsch"></a>
## Deutsch

Vielen Dank für dein Interesse, zu `doc-services` beizutragen! Dieses Modul stellt eine BACH-unabhängige Dokumentenextraktion, AGPL-freie OCR und inhaltsbasierte Datenschutzfilter für lokale LLM-Pipelines und Agenten bereit.

### 1. Architektonische Leitlinien & Invarianten

Jeder Beitrag muss die folgenden Laufzeit- und Governance-Invarianten zwingend einhalten:

- **INV-LOCAL-01 (Zero-Egress):** Vollständige lokale Ausführung ohne Netzwerkzugriffe, Telemetrie oder externe Cloud-APIs.
- **INV-LOCAL-02 (RunAsInvoker):** Unprivilegierte Ausführung im Benutzerkontext; keine administrativen Rechte erforderlich.
- **INV-LOCAL-03 (AGPL-Freiheit):** PDF-Verarbeitung erfolgt ausschließlich über `pypdfium2`. PyMuPDF (`fitz`) oder sonstige Copyleft-Lizenzen sind strikt unzulässig (Vertragstest `tests/test_no_agpl.py`).
- **INV-LOCAL-04 (Fail-Closed Datenschutz):** Inhaltsprüfung blockiert sensible Daten (ROT/GELB) standardmäßig. Diagnoseberichte maskieren Treffer zum Schutz vor Log-Leaks.
- **INV-LOCAL-05 (Zellendeduplizierung):** Verbundene Word-Tabellenzellen werden über XML-`tc`-Identität dedupliziert, um Tokenverschwendung zu verhindern.
- **INV-LOCAL-06 (CI-Härtung):** Alle Workflows tragen verbindliche Timeouts (`timeout-minutes`) und `concurrency`-Abbrüche.
- **INV-LOCAL-07 (Multi-Host-Schutz):** Gehärtetes `.gitignore` verhindert das Einchecken von Cloud-Sync-Konfliktkopien und Sperrdateien.
- **INV-LOCAL-08 (PEP 621 Standardisierung):** Standardkonforme Metadaten in `pyproject.toml`.
- **INV-LOCAL-09 (Versions-Immutabilität nach T-20260920-167562623):** Pfad-A- und Pfad-B-Läufe verändern **niemals** das `version`-Feld.
- **INV-SLA-10 (48h Sicherheits-SLA):** Verbindliche 48-Stunden-Reaktionszeit für Sicherheits- und Integritätsmeldungen.

### 2. Lokaler Entwicklungsablauf (Plan D)

- **Kanonischer Arbeitsort:** Entwicklung, Tests und Commits erfolgen im lokalen Git-Klon (`C:\_Local_DEV\repos\doc-services`) und werden nach `origin/main` gepusht.
- **Qualitätsprüfungen vor dem Commit:**
  ```bash
  python -m pytest -ra -v
  python -m ruff check .
  python -m compileall -q doc_services tests docs
  git diff --check
  ```

### 3. Gesetzlicher Hinweis & Haftungsbeschränkung (§ 521 BGB)

Die Bereitstellung der Software erfolgt unentgeltlich im Rahmen des Open-Source-Modells (MIT-Lizenz). Nach den gesetzlichen Vorschriften des deutschen Schenkungs- und Gefälligkeitsrechts (§ 521 BGB) ist die Haftung auf Vorsatz und grobe Fahrlässigkeit beschränkt.
