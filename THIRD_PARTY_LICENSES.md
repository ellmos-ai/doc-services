# Third-Party Licenses & Level 1 SBOM — doc-services

**Document Version:** 1.0.0  
**Audited:** 2026-10-18  
**Repository:** `ellmos-ai/doc-services`  
**License:** MIT  
**Zero-Copyleft Guarantee:** 100% Permissive (No AGPL, No GPL, No LGPL)  
**Security Execution:** `RunAsInvoker` (Unprivileged User Mode)  
**Network Egress:** 100% Offline / Zero-Egress  

---

## 1. Executive Summary & Level 1 SBOM Compliance

`doc-services` is designed from the ground up for zero-copyleft supply chain safety and complete offline autonomy. It provides document extraction, OCR rendering, and fail-closed privacy classification for local-first LLM applications.

- **Zero-Copyleft Guarantee:** PyMuPDF (`fitz`, AGPL) and other copyleft libraries are strictly excluded. Automated contract tests (`tests/test_no_agpl.py`) guard against transitive copyleft infiltration.
- **Level 1 SBOM Transparency:** Every direct, optional, and development dependency is audited and mapped to permissive open-source licenses (MIT, BSD-3-Clause, Apache-2.0, PSFL-2.0, HPND).
- **Zero-Egress Isolation:** All operations execute locally on the host machine. No outbound sockets, telemetry, or cloud-based OCR APIs are invoked.
- **Non-Elevated Execution:** Operates under standard user rights without requiring administrative elevation (`RunAsInvoker`).

---

## 2. Invariant Cross-Reference Matrix (INV-LOCAL-01 to INV-SLA-10)

| Invariant ID | Name | Core Requirement | Verification Method | Status |
|---|---|---|---|---|
| **INV-LOCAL-01** | Zero-Egress Guarantee | No outbound network sockets, telemetry, or remote API calls. | Static inspection & network isolation tests. | **VERIFIED** |
| **INV-LOCAL-02** | Non-Elevation (`RunAsInvoker`) | Strictly runs in unprivileged user mode; no root/admin required. | Security contract tests & execution audit. | **VERIFIED** |
| **INV-LOCAL-03** | AGPL-Free Isolation | Strictly zero AGPL components (no PyMuPDF); pypdfium2 exclusively. | Automated contract test (`tests/test_no_agpl.py`). | **VERIFIED** |
| **INV-LOCAL-04** | Fail-Closed Privacy Gate | Sensitive content (PII, secrets) triggers RED/YELLOW blocking. | Comprehensive privacy test suite (`test_privacy_und_config.py`). | **VERIFIED** |
| **INV-LOCAL-05** | Merged Cell Deduplication | Table cells spanning multiple columns deduplicated via XML `tc`. | Unit test suite (`tests/test_extract.py`). | **VERIFIED** |
| **INV-LOCAL-06** | CI Workflow Hardening | Timeout limits and concurrency cancellation enforced on all workflows. | Workflow schema checks in `test_repository_hygiene.py`. | **VERIFIED** |
| **INV-LOCAL-07** | Multi-Host Sync Protection | `.gitignore` guards against multi-host conflict files and lock leaks. | Repository hygiene tests in `test_repository_hygiene.py`. | **VERIFIED** |
| **INV-LOCAL-08** | PEP 621 Standardisation | `pyproject.toml` fully compliant with modern standard metadata. | Metadata verification tests in `test_metadata.py`. | **VERIFIED** |
| **INV-LOCAL-09** | Version Parity & Immutability | Version `0.1.1` immutable and synchronized per T-20260920-167562623. | Cross-manifest parity tests in `test_repository_hygiene.py`. | **VERIFIED** |
| **INV-SLA-10** | Security Response SLA | 48h acknowledgment SLA and 5-day initial triage commitment. | Documented in `SECURITY.md` and contract tests. | **VERIFIED** |

---

## 3. Dependency Inventory & License Details

### 3.1 Core Runtime (Zero Mandatory Dependencies)

`doc-services` has **no hard mandatory dependencies**. It dynamically discovers available installed engines at runtime and gracefully reports missing tooling.

| Component | License | Purpose |
|---|---|---|
| Python Standard Library | PSFL-2.0 | Core runtime execution, JSON parsing, regex pattern evaluation, dataclasses. |

### 3.2 Optional Extraction & OCR Dependencies

Users may selectively install engines depending on target document formats:

| Package | Version Range | License | Role / Purpose | Copyleft Risk |
|---|---|---|---|---|
| `markitdown` | >=0.1.7 | MIT | Multi-format markdown conversion engine | None (Permissive) |
| `python-docx` | >=1.1 | MIT | Word (.docx) document extraction | None (Permissive) |
| `openpyxl` | >=3.1 | MIT | Excel (.xlsx) spreadsheet processing | None (Permissive) |
| `pypdf` | >=4.0 | BSD-3-Clause | PDF text extraction without copyleft risk | None (Permissive) |
| `pypdfium2` | >=4.0 | BSD-3-Clause / Apache-2.0 | PDF page rendering & rasterization for OCR | None (Permissive) |
| `pytesseract` | >=0.3.10 | Apache-2.0 | Python wrapper for Tesseract OCR binary | None (Permissive) |
| `pillow` | >=10.0 | HPND / Historical | Image processing & raster representation | None (Permissive) |

### 3.3 Development & Test Tooling

| Package | Version Range | License | Role / Purpose |
|---|---|---|---|
| `pytest` | >=8.0 | MIT | Test framework for unit, contract, and regression testing |
| `ruff` | >=0.6 | MIT / Apache-2.0 | Ultra-fast Python linter and code formatter |
| `tomli` | >=2.0 | MIT | TOML parser for Python < 3.11 |

---

## 4. Zero-Copyleft Isolation Guarantee & RunAsInvoker Certification

1. **No Contamination:** No components under AGPL, GPL, LGPL (with static link requirement), or SSPL are linked or distributed.
2. **Commercial & Enterprise Readiness:** Safe for embedding in commercial, proprietary, and open-source applications without triggering reciprocal source disclosure obligations.
3. **Plain-Text Companion:** A machine-readable, plain-text companion file `THIRD_PARTY_LICENSES.txt` is maintained in the root directory for automated dependency scanners and container audits.

---

## 5. Attribution & Maintenance

Maintained by Lukas Geiger and the `ellmos-ai` / `open-bricks` community.  
See `NOTICE` and `LICENSE` for copyright attributions.
