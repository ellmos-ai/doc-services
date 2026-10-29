# SPDX-License-Identifier: MIT
"""Contract and metadata tests for doc-services repository.

Verifies PEP 621 compliance, .gitignore hygiene, CI matrix configuration,
bilingual documentation parity, 18-point navigation anchors, dual Mermaid diagrams,
ASCII four-view topology, Level 1 SBOM, statutory disclaimers, and version immutability.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read_text(relative_path: str) -> str:
    path = REPO_ROOT / relative_path
    assert path.is_file(), f"Expected file {relative_path} does not exist"
    return path.read_text(encoding="utf-8")


def test_gitignore_hygiene_and_multihost_guards():
    """Verify .gitignore contains essential security, lock, cache, and multi-host sync patterns."""
    content = _read_text(".gitignore")
    lines = {
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.startswith("#")
    }
    required_patterns = [
        "__pycache__/",
        "*.py[cod]",
        ".pytest_cache/",
        ".ruff_cache/",
        ".coverage",
        "LOCK",
        "LOCK.*",
        "LOCK*.txt",
        "LOCK.permissions.json",
        "uv.lock",
        "* (kopie)*",
        "* (copy)*",
        "*-WORKSTATION*",
        "*-ASUS*",
        "*-LAPTOP*",
        "*-Mac Studio*",
    ]
    for pattern in required_patterns:
        assert pattern in lines, f"Missing required .gitignore pattern: {pattern}"


def test_pyproject_pep621_metadata_and_20_keywords():
    """Verify pyproject.toml complies with PEP 621, has 20 saturated keywords and license-files."""
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    assert project.get("name") == "doc-services"
    import doc_services
    assert project.get("version") == doc_services.__version__
    assert project.get("version") == "0.1.1"  # Frozen per T-20260920-167562623
    assert project.get("license") == "MIT"

    # License files
    license_files = project.get("license-files", [])
    for expected_file in ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]:
        assert expected_file in license_files, f"Missing {expected_file} in license-files"

    # Saturated 20 keywords
    keywords = set(project.get("keywords", []))
    assert len(keywords) == 20, f"Expected exactly 20 keywords, found {len(keywords)}: {keywords}"

    # Standard URLs
    urls = project.get("urls", {})
    required_urls = [
        "Homepage",
        "Repository",
        "Issues",
        "Documentation",
        "German Documentation",
        "Changelog",
        "Contributing",
        "Notice",
        "Third-Party Licenses",
        "Third-Party Licenses (Text)",
        "Plain-Text License",
        "Security Policy",
        "LLM Context Index",
        "Marketing Log",
        "Parent Organization",
        "Umbrella Ecosystem",
    ]
    for key in required_urls:
        assert key in urls, f"Missing required URL '{key}' in pyproject.toml [project.urls]"


def test_version_parity_and_frozen_invariant():
    """Verify version 0.1.1 is strictly synchronized and frozen across all manifests."""
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        pyproject_ver = tomllib.load(f)["project"]["version"]

    import json

    import doc_services
    init_ver = doc_services.__version__

    with open(REPO_ROOT / "ellmos-module.json", encoding="utf-8") as f:
        m1_ver = json.load(f)["version"]

    with open(REPO_ROOT / "ellmos-module.v2.json", encoding="utf-8") as f:
        m2_ver = json.load(f)["version"]

    llms_txt = _read_text("llms.txt")
    assert f"Version: {pyproject_ver}" in llms_txt

    assert pyproject_ver == init_ver == m1_ver == m2_ver == "0.1.1", (
        f"Version parity violation: {pyproject_ver} != {init_ver} != {m1_ver} != {m2_ver}"
    )


def test_security_policy_and_sla():
    """Verify SECURITY.md defines 48h SLA, 5-day triage, contacts, and Zero Egress."""
    content = _read_text("SECURITY.md")
    assert "48 hours" in content or "48 Stunden" in content
    assert "5 business days" in content or "5 Werktagen" in content
    assert "security@ellmos.ai" in content
    assert "security@open-bricks.org" in content
    assert "Zero Network Egress" in content or "Zero-Egress" in content
    assert "RunAsInvoker" in content


def test_readme_bilingual_parity():
    """Verify cross-linking and banner presence in English and German READMEs."""
    en_content = _read_text("README.md")
    de_content = _read_text("README_de.md")

    assert "README_de.md" in en_content or "Deutsche Fassung" in en_content
    assert "README.md" in de_content or "English version" in de_content

    assert '<img src="assets/banner.png"' in en_content
    assert '<img src="assets/banner.png"' in de_content


def test_readme_navigation_anchor_parity():
    """Verify 18-point quick navigation and dual HTML anchors in both READMEs."""
    en_content = _read_text("README.md")
    de_content = _read_text("README_de.md")

    en_links = re.findall(r"^\d+\.\s+\[.+?\]\((#.+?)\)", en_content, re.MULTILINE)
    de_links = re.findall(r"^\d+\.\s+\[.+?\]\((#.+?)\)", de_content, re.MULTILINE)

    assert len(en_links) == 18, f"Expected 18 navigation links in README.md, got {len(en_links)}"
    assert len(de_links) == 18, f"Expected 18 navigation links in README_de.md, got {len(de_links)}"

    # Check reciprocal dual HTML anchors for sec-01 through sec-18
    for i in range(1, 19):
        anchor = f'<a id="sec-{i:02d}"></a>'
        assert anchor in en_content, f"Missing {anchor} in README.md"
        assert anchor in de_content, f"Missing {anchor} in README_de.md"


def test_dual_mermaid_diagrams_syntax():
    """Verify Mermaid diagrams exist, have clean syntax, and no trailing semicolons."""
    en_content = _read_text("README.md")
    de_content = _read_text("README_de.md")

    for content, lang in [(en_content, "EN"), (de_content, "DE")]:
        assert "```mermaid\nflowchart TD" in content, f"Missing flowchart TD in {lang}"
        assert "```mermaid\nsequenceDiagram" in content, f"Missing sequenceDiagram in {lang}"
        assert "autonumber" in content, f"Missing autonumber in {lang}"

        mermaid_blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
        for block in mermaid_blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            for line in lines:
                assert not line.endswith(";"), f"Mermaid line ends with semicolon in {lang}: {line}"


def test_ascii_topology_projection_present():
    """Verify README.md and README_de.md both project the four-view ASCII topology."""
    en_text = _read_text("README.md")
    de_text = _read_text("README_de.md")

    en_markers = [
        "DOC-SERVICES ARCHITECTURAL TOPOLOGY PROJECTION",
        "[VIEW 1: CLI, REGISTRY & HOST SITUATION SUBSYSTEM]",
        "[VIEW 2: BACKEND ENGINE SELECTION, EXTRACTION & OCR SUBSYSTEM]",
        "[VIEW 3: PRIVACY GATE, FAIL-CLOSED CLASSIFIER & CONTENT SCREENING SUBSYSTEM]",
        "[VIEW 4: LEARNING PREFERENCES, METRIC TRACKING & EVALUATION SUBSYSTEM]",
        "INV-LOCAL-01",
        "INV-LOCAL-05",
        "INV-SLA-10",
    ]
    for marker in en_markers:
        assert marker in en_text, f"Missing marker '{marker}' in README.md"

    de_markers = [
        "DOC-SERVICES ARCHITECTURAL TOPOLOGY PROJECTION",
        "[SICHT 1: CLI, REGISTRIERUNG & HOST-LAGE-SUBSYSTEM]",
        "[SICHT 2: BACKEND-ENGINE-AUSWAHL, EXTRAKTION & OCR-SUBSYSTEM]",
        "[SICHT 3: DATENSCHUTZ-TOR, FAIL-CLOSED KLASSIFIKATOR & INHALTSPRÜFUNG]",
        "[SICHT 4: LERNENDE PRÄFERENZEN, METRIK-VERFOLGUNG & EVALUATIONSSYSTEM]",
        "INV-LOCAL-01",
        "INV-LOCAL-05",
        "INV-SLA-10",
    ]
    for marker in de_markers:
        assert marker in de_text, f"Missing marker '{marker}' in README_de.md"


def test_target_personas_present():
    """Verify target personas [PERSONA-01] to [PERSONA-04] in both READMEs."""
    en_content = _read_text("README.md")
    de_content = _read_text("README_de.md")

    personas = ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]
    for p in personas:
        assert p in en_content, f"Missing persona {p} in README.md"
        assert p in de_content, f"Missing persona {p} in README_de.md"


def test_comparative_matrix_sections():
    """Verify 10-dimension comparative matrix vs. alternatives in both READMEs."""
    en_content = _read_text("README.md")
    de_content = _read_text("README_de.md")

    for content, lang in [(en_content, "EN"), (de_content, "DE")]:
        assert "PyMuPDF" in content, f"Missing PyMuPDF comparison in {lang}"
        assert "python-docx" in content, f"Missing python-docx comparison in {lang}"
        assert "Cloud" in content, f"Missing Cloud comparison in {lang}"


def test_governance_invariants_table():
    """Verify all 10 runtime invariants (INV-LOCAL-01 to INV-SLA-10) are documented."""
    en_content = _read_text("README.md")
    de_content = _read_text("README_de.md")
    llms_content = _read_text("llms.txt")
    licenses_md = _read_text("THIRD_PARTY_LICENSES.md")
    licenses_txt = _read_text("THIRD_PARTY_LICENSES.txt")
    marketing_content = _read_text("MARKETING-LOG.txt")

    invariants = [
        "INV-LOCAL-01", "INV-LOCAL-02", "INV-LOCAL-03", "INV-LOCAL-04", "INV-LOCAL-05",
        "INV-LOCAL-06", "INV-LOCAL-07", "INV-LOCAL-08", "INV-LOCAL-09", "INV-SLA-10",
    ]
    for inv in invariants:
        assert inv in en_content, f"Missing {inv} in README.md"
        assert inv in de_content, f"Missing {inv} in README_de.md"
        assert inv in llms_content, f"Missing {inv} in llms.txt"
        assert inv in licenses_md, f"Missing {inv} in THIRD_PARTY_LICENSES.md"
        assert inv in licenses_txt, f"Missing {inv} in THIRD_PARTY_LICENSES.txt"
        assert inv in marketing_content, f"Missing {inv} in MARKETING-LOG.txt"


def test_statutory_disclaimer_521_bgb():
    """Verify Section 18 statutory notice and liability limitation (§ 521 BGB)."""
    en_content = _read_text("README.md")
    de_content = _read_text("README_de.md")
    contrib_content = _read_text("CONTRIBUTING.md")

    check_targets = [
        (en_content, "README.md"),
        (de_content, "README_de.md"),
        (contrib_content, "CONTRIBUTING.md"),
    ]
    for content, name in check_targets:
        assert "§ 521 BGB" in content, f"Missing § 521 BGB in {name}"
        assert "Gefälligkeitsrecht" in content or "gratuitous" in content, f"Missing Gefälligkeitsrecht in {name}"


def test_notice_file_exists():
    """Verify NOTICE file exists and contains correct entity attributions."""
    content = _read_text("NOTICE")
    assert "doc-services" in content
    assert "Lukas Geiger" in content
    assert "ellmos-ai" in content
    assert "open-bricks" in content


def test_contributing_guidelines_bilingual():
    """Verify CONTRIBUTING.md contains Plan D workflow, quality gates, and invariant discipline."""
    content = _read_text("CONTRIBUTING.md")
    assert "Contributing to doc-services" in content
    assert "Mitwirken an doc-services" in content
    assert "Plan D" in content
    assert "INV-LOCAL-01" in content
    assert "T-20260920-167562623" in content
    assert "pytest" in content


def test_third_party_licenses_level1_sbom():
    """Verify THIRD_PARTY_LICENSES.md and THIRD_PARTY_LICENSES.txt provide Level 1 SBOM."""
    md_content = _read_text("THIRD_PARTY_LICENSES.md")
    txt_content = _read_text("THIRD_PARTY_LICENSES.txt")

    for content, name in [(md_content, "THIRD_PARTY_LICENSES.md"), (txt_content, "THIRD_PARTY_LICENSES.txt")]:
        assert "Level 1" in content, f"Missing Level 1 SBOM in {name}"
        assert "Zero-Copyleft" in content or "Zero-AGPL" in content, f"Missing copyleft guarantee in {name}"
        assert "RunAsInvoker" in content, f"Missing RunAsInvoker in {name}"
        assert "pypdfium2" in content, f"Missing pypdfium2 in {name}"


def test_marketing_log_pfad_b_contract():
    """Verify MARKETING-LOG.txt contains Section 6 Pfad B audit and recommendations."""
    content = _read_text("MARKETING-LOG.txt")
    assert "6. MARKETING & DISCOVERABILITY PARITY UPGRADE (PFAD B)" in content
    assert "Frozen per T-20260920-167562623" in content
    assert "[REC-20261018-01]" in content
    assert "[REC-20261018-02]" in content
    assert "[REC-20261018-03]" in content


def test_llms_txt_version_and_recency():
    """Verify llms.txt reflects v0.1.1, 2026-10-30 stamp, and green test baseline."""
    content = _read_text("llms.txt")
    assert "Version: 0.1.1" in content
    assert "Last-checked: 2026-10-30" in content
    assert "INV-LOCAL-01" in content
    assert "Four-View Architectural Topology" in content
