# SPDX-License-Identifier: MIT
"""Haelt die Lizenzentscheidung E08 dauerhaft fest.

Das Modul soll ohne AGPL-Bindung auslieferbar bleiben. Die BACH-Vorlage
importierte fuer PDF-Rendering PyMuPDF (`fitz`, AGPL). Dieser Test verhindert,
dass die Abhaengigkeit unbemerkt zurueckkehrt — durch Copy-Paste aus BACH,
durch eine bequeme Bibliothek oder durch einen Fallback, den jemand gut meint.

Ein Test statt einer Notiz, weil eine Notiz niemanden aufhaelt.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

PAKET = Path(__file__).resolve().parent.parent / "doc_services"

# Namen, die eine Copyleft-Bindung in ein ausgeliefertes MIT-Modul tragen wuerden.
VERBOTEN = {
    "fitz": "PyMuPDF (AGPL-3.0)",
    "pymupdf": "PyMuPDF (AGPL-3.0)",
    "PyMuPDF": "PyMuPDF (AGPL-3.0)",
    "textract": "textract (zieht GPL-Abhaengigkeiten nach)",
}


def _module_dateien() -> list[Path]:
    return sorted(PAKET.rglob("*.py"))


def test_paket_hat_dateien():
    assert _module_dateien(), "Kein Quelltext gefunden — Testpfad pruefen"


@pytest.mark.parametrize("datei", _module_dateien(), ids=lambda p: p.name)
def test_kein_copyleft_import(datei: Path):
    """Kein Modul importiert eine copyleft-gebundene Bibliothek."""
    baum = ast.parse(datei.read_text(encoding="utf-8"), filename=str(datei))
    getroffen: list[str] = []
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Import):
            for alias in knoten.names:
                wurzel = alias.name.split(".")[0]
                if wurzel in VERBOTEN:
                    getroffen.append(f"{wurzel} ({VERBOTEN[wurzel]})")
        elif isinstance(knoten, ast.ImportFrom) and knoten.module:
            wurzel = knoten.module.split(".")[0]
            if wurzel in VERBOTEN:
                getroffen.append(f"{wurzel} ({VERBOTEN[wurzel]})")
    assert not getroffen, (
        f"{datei.name} importiert copyleft-gebundene Bibliotheken: {getroffen}. "
        "Entscheidung E08 vom 2026-08-18: PDF-Rendering laeuft ueber pypdfium2 "
        "(BSD-3-Clause / Apache-2.0)."
    )


def test_ocr_nutzt_pypdfium2():
    """Positivprobe: der vorgesehene permissive Renderer wird tatsaechlich genutzt."""
    quelle = (PAKET / "ocr.py").read_text(encoding="utf-8")
    assert "pypdfium2" in quelle, "ocr.py soll pypdfium2 zum Rendern verwenden"


def test_katalog_fuehrt_kein_agpl_backend():
    """profil.json darf kein AGPL-Backend als benutzbare Option anbieten."""
    katalog = json.loads((PAKET.parent / "profil.json").read_text(encoding="utf-8"))
    treffer: list[str] = []
    for fmt, block in katalog.get("formats", {}).items():
        for b in block.get("backends", []):
            lizenz = (b.get("license") or "").upper()
            if "AGPL" in lizenz:
                treffer.append(f"{fmt}:{b['id']} -> {b.get('license')}")
    assert not treffer, f"AGPL-Backends im Katalog: {treffer}"


def test_gpl_backends_sind_eingeordnet():
    """GPL-Backends duerfen gelistet sein, muessen aber eingeordnet werden.

    Die Unterscheidung ist die entscheidende aus der Lizenzpolitik:

      GELINKT (Python-Import)  -> die GPL bindet unser Modul. Muss ausdruecklich
                                  gewarnt sein. Beispiel: extract-msg (GPL-3.0).
      PROZESS-SEPARAT (Binary) -> kein Linking, keine Bindung. Muss als solches
                                  benannt sein. Beispiel: antiword.

    Beides ist zulaessig; unmarkiert ist keines von beidem.
    """
    katalog = json.loads((PAKET.parent / "profil.json").read_text(encoding="utf-8"))
    for fmt, block in katalog.get("formats", {}).items():
        for b in block.get("backends", []):
            lizenz = (b.get("license") or "").upper()
            if "GPL" not in lizenz or "AGPL" in lizenz or "MPL" in lizenz:
                continue
            text = ((b.get("schwaeche") or "") + " " + (b.get("license") or "")).upper()
            prozess_separat = bool(b.get("requires_binary")) and "PROZESS-SEPARAT" in text
            gewarnt = "WARNUNG" in text or "NICHT" in text
            assert prozess_separat or gewarnt, (
                f"{fmt}:{b['id']} ist GPL, aber weder als prozess-separat eingeordnet "
                "noch mit einer Warnung versehen"
            )
