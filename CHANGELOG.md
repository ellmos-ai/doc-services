# Changelog — doc-services

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Marketing, Design & Discoverability Parity Upgrade (Pfad B — Stand 2026-10-18)**:
  - **Visual Architecture Topology**:
    - Integrated dual Mermaid diagrams (5-layer architecture flowchart TD and end-to-end extraction/privacy lifecycle sequenceDiagram with autonumber).
    - Added ASCII Four-View Architectural Topology projection in `README.md` and `README_de.md` (`[VIEW 1..VIEW 4]` / `[SICHT 1..SICHT 4]`) projecting all 10 invariants `INV-LOCAL-01..INV-SLA-10`.
  - **18-Point Bilingual Navigation Parity**:
    - Harmonized 18-point quick navigation across English and German READMEs with reciprocal dual HTML anchors (`<a id="sec-01"></a>..<a id="sec-18"></a>` aliases).
  - **Target Personas & High-Intent Queries**:
    - Formulated 4 target developer/compliance personas (`[PERSONA-01]` to `[PERSONA-04]`) and high-intent developer search queries in English and German.
  - **10-Dimension Comparative Matrix**:
    - Comprehensive comparative matrix evaluating `doc-services` against PyMuPDF-based tools, naive `python-docx`, and cloud document extraction APIs.
  - **Level 1 SBOM Transparency**:
    - Added comprehensive Level 1 SBOM in `THIRD_PARTY_LICENSES.md` and plain-text companion `THIRD_PARTY_LICENSES.txt` auditing all 10 runtime invariants `INV-LOCAL-01..INV-SLA-10` [all 10 VERIFIED], Zero-Copyleft isolation guarantee, and `RunAsInvoker` certification.
  - **Attribution & Governance**:
    - Added root `NOTICE` file specifying copyright attribution under MIT for Lukas Geiger, `ellmos-ai`, and `open-bricks`.
    - Added bilingual `CONTRIBUTING.md` guidelines detailing the Plan D local development workflow, quality gates, invariant discipline, and statutory notice.
  - **Statutory Notice & Liability Limitation (§ 521 BGB)**:
    - Incorporated statutory notice for gratuitous open-source provision (*Gefälligkeitsrecht* § 521 BGB) and binding 48-hour security response SLA in Section 18 of `README.md` and `README_de.md`.
  - **PEP 621 Standardisation**:
    - Saturated `keywords` to 20 relevant topics in `pyproject.toml`.
    - Expanded `[project.urls]` with Notice, Contributing, Changelog, Level 1 SBOM, and umbrella links.
    - Updated `license-files` to include `NOTICE`, `THIRD_PARTY_LICENSES.md`, and `THIRD_PARTY_LICENSES.txt`.
  - **Automated Metadata & Contract Tests**:
    - Added `tests/test_metadata.py` verifying all Pfad B documentation contracts, navigation anchors, Mermaid diagrams, ASCII topology, Level 1 SBOM, and frozen version invariance (`0.1.1` frozen per T-20260920-167562623).

### Fixed
- Privacy file screening now enforces its size limit in bytes without reading the
  entire file. Oversized files receive an explicit incomplete-screening YELLOW
  verdict instead of a potentially unsafe GREEN verdict for a truncated prefix.
  Nonpositive limits are rejected; regression tests cover hidden sensitive tails,
  exact boundaries, and multibyte UTF-8 text.

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
