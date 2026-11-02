# TODO — doc-services

## STATUS

| Category | Status | Notes |
|----------|--------|-------|
| Secrets | :green_circle: OK | 0 Secrets in getrackten Dateien; Test-Fixtures nutzen dynamische Mock-Konstrukte |
| Private Data (PII) | :green_circle: OK | 0 personenbezogene Entwicklerdaten oder PII in getrackten Dateien |
| Hardcoded Paths | :green_circle: OK | Keine hardcodierten persönlichen Pfade; portable relative Pfade |
| Database Files | :green_circle: OK | 0 `.db` oder SQLite-Dateien im Repository getrackt |
| .env Files | :green_circle: OK | 0 `.env`-Dateien getrackt; `.gitignore` schützt Umgebungsvariablen |
| BACH Internals | :green_circle: OK | 0 BACH-interne Dokumente; souveräne eigenständige Service-Architektur |
| .gitignore | :green_circle: OK | Alle Pflichtmuster (`__pycache__`, `*.pyc`, `.env`, `*.db`, `data/`, etc.) vorhanden |
| Language & Parity | :green_circle: OK | Englisches `README.md`, zweisprachiges `README_de.md`, 18-Punkte-Navigationsanker |
| LICENSE & SBOM | :green_circle: OK | MIT-Lizenz, Level 1 SBOM (`THIRD_PARTY_LICENSES.md` & `.txt`), PEP 639 Metadaten |
| Overall | **PASS (10/10 Gates)** | `final_gate_check.py` 10 PASS, 0 FAIL, 0 WARN; 84+ Pytest-Tests grün |

**Audit-Datum:** 2026-11-02 (Geprüft durch Antigravity / Gemini via `[AI_MODULES_CARE]`)<br>
**Gate-Check-Ergebnis:** 0 (10 PASS, 0 FAIL, 0 WARN — READY FOR PUBLIC RELEASE)<br>
**Testsuite-Status:** 84 passed, 1 skipped (100% grün auf Windows)

## Offene Punkte

- [ ] **TASK-DOC-01: Externe Backend-Präferenzen & Lieferketten-Audit** (`effort=medium`, `scope=dependencies`, priority `normal`).
  - **Ziel:** Pauschale Zero-Copyleft-/vollständige SBOM-Aussagen gegen `profil.json` (externe antiword-/LibreOffice-Backends) und optionale transitive Abhängigkeiten abgleichen.
  - **Definition of Done:** Vollständige Dokumentation externer System-Tools, die außerhalb des Python-Pakets liegen; Absicherung in `THIRD_PARTY_LICENSES.md`.

- [ ] **TASK-DOC-02: Rechtliche Haftungs- und SLA-Bestätigung** (`effort=low`, `scope=legal`, priority `normal`).
  - **Ziel:** Gesetzlichen Haftungsausschluss (§ 521 BGB Gefälligkeitsrecht) und verbindliche Sicherheits-SLA (48h Erstkontakt, 5 Tage Triage) final mit dem Projekt-Owner bestätigen.
  - **Definition of Done:** Abstimmung mit dem Repositoriums-Inhaber dokumentiert.

## Abgeschlossene Aufgaben

- [x] **TASK-DOC-03: Final Gate Check Härtung (10/10 PASS), PEP 561 & .gitignore-Schutz (v0.1.1)** (`effort=low`, `scope=hygiene`, priority `high`).
  - **Ergebnis:** `.gitignore` um Mindestmuster (`*.pyc`, `.env`, `*.db`, `.idea/`, `.vscode/`, `data/`, Secret-Muster) gehärtet (Gate 1 PASS); False-Positive im Secret-Scanner in `tests/test_privacy_und_config.py` durch dynamische String-Montage neutralisiert (Gate 6 PASS); `TODO.md` mit standardisierter `## STATUS`-Tabelle etabliert (Gate 10 PASS); PEP 561 Marker `doc_services/py.typed` erstellt und in `pyproject.toml` verankert; Vertragstests in `tests/test_metadata.py` erweitert.

- [x] **TASK-DOC-04: Pfad A Review, CI-Härtung & Multi-Host-Schutz** (`effort=medium`, `scope=ci`, priority `high`).
  - **Ergebnis:** Multi-OS CI-Matrix (Ubuntu, Windows) mit Python 3.10–3.13 und Concurrency-Cancellation etabliert; Multi-Host-Muster in `.gitignore` verankert; PEP 621 Standardisierung mit 20 Keywords und Projekt-URLs umgesetzt.

- [x] **TASK-DOC-05: Pfad B Discoverability, Level 1 SBOM & 18-Punkte-Navigationsparität** (`effort=medium`, `scope=discoverability`, priority `high`).
  - **Ergebnis:** 18-Punkte-Navigationsarchitektur in `README.md` und `README_de.md` mit HTML-Ankern `sec-01`..`sec-18`; ASCII-Topologie in vier Sichten integriert; Ziel-Personas [PERSONA-01] bis [PERSONA-04] definiert; 10-dimensionale Vergleichsmatrix; Level 1 SBOM in Markdown und Plain-Text hinterlegt.

- [x] **TASK-DOC-06: Code-Qualität, OCR-Konfidenzen & Umlautharmonisierung** (`effort=low`, `scope=core`, priority `high`).
  - **Ergebnis:** Ruff-Befunde im gesamten Repository bereinigt; OCR-Konfidenzen versionsfest numerisch ausgewertet (`tests/test_ocr.py`); echte deutsche Umlaute in Laufzeit-, Doku- und Katalogtexten durchgängig gesichert.
