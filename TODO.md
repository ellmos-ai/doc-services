# TODO — doc-services

Diese Datei ist die TASKWRITER-Erfassung zum Bundle vom 2026-09-05 sowie das
Aufgaben- und Statusregister für Wartungs- und Hygienezwecke.

## Abgeschlossene TASKPLAN-Aufgaben

- [x] #366 Ruff-Befunde in Paket, Abnahmeskript und Tests bereinigen. (Abgeschlossen: 0 Ruff-Fehler im gesamten Repo).
- [x] #367 OCR-Konfidenzen versionsfest als Zahlen auswerten. (Abgeschlossen in `_erkenne_bild`, abgesichert durch `tests/test_ocr.py`).
- [x] #368 Deutsche Laufzeit- und Katalogtexte mit echten Umlauten pflegen. (Abgeschlossen: `pyproject.toml` und Manifeste aktualisiert).

## Pfad A Review & CI-Härtung — 2026-09-14

- Stand: lokaler Klon, Branch `master`, Version `0.1.1`.
- Schutzkontrollen: `PRIVATE.txt` geprüft und intakt (`GATE: closed`, `SCOPE: private-repository`).
- CI-Workflows gehärtet:
  - `.github/workflows/ci.yml` mit Multi-OS (Ubuntu, Windows) und Multi-Python (3.10-3.13), `timeout-minutes: 15`, Concurrency-Cancellation.
  - `.github/workflows/stale.yml` mit täglichem Cron (`30 1 * * *`), `timeout-minutes: 10`, least-privilege permissions.
  - `.github/workflows/welcome.yml` mit `timeout-minutes: 5`, Concurrency-Cancellation.
- Multi-Host Cloud-Sync-, Lock- und Cache-Härtung in `.gitignore`.
- PEP 621 Standardisierung in `pyproject.toml` mit Projekt-URLs und `addopts = "-ra -v"`.
- `SECURITY.md`, `MARKETING-LOG.txt` und `llms.txt` neu angelegt.
- Vertragstestsuite `tests/test_repository_hygiene.py` implementiert (53/53 Tests grün).
- Version 0.1.1 harmonisiert über alle Manifeste (`pyproject.toml`, `doc_services/__init__.py`, `ellmos-module.json`, `ellmos-module.v2.json`, `llms.txt`, `CHANGELOG.md`).

## TASKWRITER-Review — 2026-09-05

- Bundle: `c36424ec-e8f1-4c97-9b21-9d43d0546410` · selector review
  `sha256-v1:2d607903b932d7a23950cd04786d051916c7ba34caf5817ae153c95f680ac659`
- Projekt/Stand: lokaler Klon, Branch `master`,
  `4de22eb`, `master...origin/master`, Arbeitsbaum vor dem TASKWRITER-Schreiben
  sauber; Remote ist das private `ellmos-ai/doc-services`-Repository.
- Schutzkontrollen: `PRIVATE.txt` gelesen — Repository bleibt privat; kein
  Publish, kein Package-Release, kein öffentlicher Mirror. Kein Projekt-
  spezifisches `AGENTS.md` oder `CLAUDE.md` vorhanden.
- Gelesene Kontrollen: `README.md`, `README_de.md`, `pyproject.toml`,
  `profil.json`, beide `ellmos-module*.json`, `LICENSE`, `PRIVATE.txt`,
  alle fünf Paketmodule, drei Testdateien und das Abnahmeskript.
- Verifikation: `python -m pytest -q` besteht; `python -m compileall -q
  doc_services tests` besteht; Wheel-Build mit `python -m build --wheel
  --no-isolation` besteht und enthält `profil.json`.
