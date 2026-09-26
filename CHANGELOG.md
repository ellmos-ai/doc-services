# Changelog — doc-services

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] — 2026-09-14

### Added
- **CI Workflow Hardening**:
  - `.github/workflows/ci.yml`: Multi-OS (`ubuntu-latest`, `windows-latest`) and multi-Python matrix (`3.10`, `3.11`, `3.12`, `3.13`), `timeout-minutes: 15`, concurrency cancellation, syntax compilation, Ruff linting, and verbose pytest runs.
  - `.github/workflows/stale.yml`: Daily cron lifecycle automation (`30 1 * * *`), `timeout-minutes: 10`, concurrency cancellation, least-privilege permissions (`issues: write`, `pull-requests: write`).
  - `.github/workflows/welcome.yml`: Contributor interaction workflow, `timeout-minutes: 5`, concurrency cancellation.
- **Multi-Host Cloud-Sync & Lock Hardening in `.gitignore`**:
  - Protected against cloud-sync conflict files (`* (kopie)*`, `* (copy)*`, `*conflicted copy*`, `*-WORKSTATION*`, `*-ASUS*`, `*-LAPTOP*`, `*-Mac Studio*`).
  - Hardened lock rules (`LOCK`, `LOCK.*`, `LOCK*.txt`, `LOCK.permissions.json`, `*.lock`, `uv.lock`).
  - Added temporary cache and test output filters (`.coverage*`, `coverage/`, `htmlcov/`, `wheelhouse/`, `.wheel-smoke/`, `.tox/`, `.hypothesis/`, `.turbo/`).
- **PEP 621 Standardisation**:
  - Added `[project.urls]` in `pyproject.toml` pointing to Repository, Issues, Documentation, German Documentation, Security Policy, LLM Context Index, and Marketing Log.
  - Added `test` optional dependencies extra and standardized `addopts = "-ra -v"` for verbose, clear test diagnostics.
- **Security Policy (`SECURITY.md`)**:
  - Documented Local-First guarantees, zero network egress, AGPL-free enforcement, fail-closed privacy screening, unprivileged execution (`RunAsInvoker`), and explicit 48-hour vulnerability reporting SLA.
- **Marketing & Discoverability Log (`MARKETING-LOG.txt`)**:
  - Documented value proposition, 4 target personas, 10-dimension comparison matrix against alternatives, and governance invariants (INV-LOCAL-01 to INV-SLA-10).
- **LLM Context Index (`llms.txt`)**:
  - Added structured overview of architecture, core functions, invariants, and test commands for autonomous coding assistants.
- **Repository Hygiene Contract Tests (`tests/test_repository_hygiene.py`)**:
  - Automated tests validating `.gitignore` protection patterns, CI workflow timeouts and concurrency, PEP 621 URLs, Pytest configuration, version parity, and security policy requirements.

### Changed
- Harmonized version `0.1.1` across `pyproject.toml`, `doc_services/__init__.py`, `ellmos-module.json`, `ellmos-module.v2.json`, and `llms.txt`.
- Refined German text descriptions in `pyproject.toml` with genuine umlauts.
- Updated `README.md` and `README_de.md` with badges for Python, MIT, green test suite, local-first, zero egress, and security policy references.

### Fixed
- Fixed Ruff SIM300 Yoda comparison finding in `tests/test_produces_filter.py`.

---

## [0.1.0] — 2026-09-05

### Added
- Initial standalone extraction from `BACH/system/hub/_services/document/` and `system/tools/ocr/engine.py`.
- Merged table cell deduplication in DOCX via XML `tc` element identity (ticket `T-20260817-825816579`).
- AGPL-free PDF rendering using `pypdfium2` with contract test guard `tests/test_no_agpl.py`.
- Content-based privacy classifier `darf_weitergegeben_werden()` with fail-closed traffic-light evaluation.
- Dynamic backend preference and learning layer separating catalog (`profil.json`) from host configuration (`config.json`).
