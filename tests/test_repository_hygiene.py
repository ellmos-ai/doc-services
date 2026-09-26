# SPDX-License-Identifier: MIT
"""Vertragstests für Repository-Hygiene, CI-Härtung, PEP 621 und Governance."""

from __future__ import annotations

import compileall
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parent.parent


def test_gitignore_contains_multihost_and_lock_patterns():
    """Prüft, ob .gitignore vor Multi-Host-Konflikten, Locks und Caches schützt."""
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    pflicht_muster = [
        "LOCK",
        "LOCK.*",
        "LOCK*.txt",
        "uv.lock",
        "* (kopie)*",
        "* (copy)*",
        "*-WORKSTATION*",
        "*-ASUS*",
        "*-LAPTOP*",
        "*-Mac Studio*",
        ".coverage",
        "coverage/",
    ]
    for muster in pflicht_muster:
        assert muster in gitignore, f"Muster '{muster}' fehlt in .gitignore"


def test_ci_workflows_exist_and_are_hardened():
    """CI-Workflows müssen existieren und Timeout- sowie Concurrency-Schutz tragen."""
    workflows_dir = ROOT / ".github" / "workflows"
    assert workflows_dir.is_dir(), ".github/workflows Verzeichnis fehlt"

    erwartete_workflows = ["ci.yml", "stale.yml", "welcome.yml"]
    for wf in erwartete_workflows:
        pfad = workflows_dir / wf
        assert pfad.is_file(), f"Workflow-Datei {wf} fehlt"
        inhalt = pfad.read_text(encoding="utf-8")
        assert "timeout-minutes:" in inhalt, f"Workflow {wf} fehlt 'timeout-minutes'"
        assert "concurrency:" in inhalt, f"Workflow {wf} fehlt 'concurrency'"
        assert "cancel-in-progress: true" in inhalt, f"Workflow {wf} bricht veraltete Läufe nicht ab"


def test_pyproject_pep621_urls_and_pytest_options():
    """pyproject.toml muss PEP 621 Projekt-URLs und verbindliche Pytest-Flags führen."""
    pyproject_pfad = ROOT / "pyproject.toml"
    assert pyproject_pfad.is_file(), "pyproject.toml fehlt"

    with pyproject_pfad.open("rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    urls = project.get("urls", {})
    erwartete_urls = [
        "Repository",
        "Issues",
        "Documentation",
        "German Documentation",
        "Security Policy",
        "LLM Context Index",
        "Marketing Log",
    ]
    for key in erwartete_urls:
        assert key in urls, f"PEP 621 URL '{key}' fehlt in pyproject.toml [project.urls]"

    # Pytest-Flags
    pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    addopts = pytest_opts.get("addopts", "")
    assert "-ra" in addopts and "-v" in addopts, f"pytest addopts unvollständig: {addopts}"


def test_version_parity_across_manifests():
    """Version 0.1.1 muss über alle Manifeste, Module und Kontextdateien harmonisiert sein."""
    # pyproject.toml
    with (ROOT / "pyproject.toml").open("rb") as f:
        pyproject_ver = tomllib.load(f)["project"]["version"]

    # doc_services/__init__.py
    # ellmos-module.json
    import json

    from doc_services import __version__ as init_ver
    with (ROOT / "ellmos-module.json").open(encoding="utf-8") as f:
        m1_ver = json.load(f)["version"]

    # ellmos-module.v2.json
    with (ROOT / "ellmos-module.v2.json").open(encoding="utf-8") as f:
        m2_ver = json.load(f)["version"]

    # llms.txt
    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert f"Version: {pyproject_ver}" in llms_text, "Version in llms.txt weicht ab"

    # CHANGELOG.md
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{pyproject_ver}]" in changelog, f"Changelog führt Version {pyproject_ver} nicht"

    assert pyproject_ver == init_ver == m1_ver == m2_ver == "0.1.1", (
        f"Versionsinkonsistenz: pyproject={pyproject_ver}, __init__={init_ver}, "
        f"module_v1={m1_ver}, module_v2={m2_ver}"
    )


def test_security_policy_and_sla():
    """SECURITY.md muss vorhanden sein und Kernversprechen sowie die 48h-SLA enthalten."""
    sec_pfad = ROOT / "SECURITY.md"
    assert sec_pfad.is_file(), "SECURITY.md fehlt"
    inhalt = sec_pfad.read_text(encoding="utf-8")
    assert "48 hours" in inhalt or "48 Stunden" in inhalt, "48h SLA fehlt in SECURITY.md"
    assert "Local-First" in inhalt or "Zero Network Egress" in inhalt, "Local-First fehlt in SECURITY.md"
    assert "pypdfium2" in inhalt, "pypdfium2 fehlt in SECURITY.md"


def test_public_gate_intact():
    """PUBLIC.txt muss vorhanden sein und einen bekannten GATE-Zustand tragen
    (Nachfolger von PRIVATE.txt). "conditional" heisst: eine Nutzerentscheidung
    steht noch aus (siehe Inhalt), nicht dass die Datei fehlerhaft waere."""
    gate_pfad = ROOT / "PUBLIC.txt"
    assert gate_pfad.is_file(), "PUBLIC.txt fehlt"
    inhalt = gate_pfad.read_text(encoding="utf-8")
    assert "GATE: lifted" in inhalt or "GATE: conditional" in inhalt, (
        "PUBLIC.txt hat keinen bekannten GATE-Zustand"
    )
    assert not (ROOT / "PRIVATE.txt").is_file(), "PRIVATE.txt haette durch PUBLIC.txt ersetzt werden muessen"


def test_marketing_log_intact():
    """MARKETING-LOG.txt muss vorhanden sein und Governance-Invarianten aufführen."""
    log_pfad = ROOT / "MARKETING-LOG.txt"
    assert log_pfad.is_file(), "MARKETING-LOG.txt fehlt"
    inhalt = log_pfad.read_text(encoding="utf-8")
    assert "INV-LOCAL-01" in inhalt and "INV-LOCAL-10" in inhalt, "Invarianten fehlen in MARKETING-LOG.txt"


def test_syntax_compilation():
    """doc_services, tests und docs müssen ohne Syntaxfehler kompilieren."""
    erfolg = compileall.compile_dir(str(ROOT / "doc_services"), quiet=1)
    erfolg = erfolg and compileall.compile_dir(str(ROOT / "tests"), quiet=1)
    erfolg = erfolg and compileall.compile_dir(str(ROOT / "docs"), quiet=1)
    assert erfolg, "Syntaxfehler bei compileall gefunden"
