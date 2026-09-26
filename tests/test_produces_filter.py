# SPDX-License-Identifier: MIT
"""Tests fuer `extrahieren(..., produces=...)` — die Ausgabeform als Wunsch des Aufrufers.

Hintergrund (T-20260818-903104603, Einheit 5b): Wer den Text weiterverarbeitet
statt ihn anzuzeigen, braucht Fliesstext. Bei LaTeX-PDFs ist das nicht Kosmetik —
markitdown verliert dort Wortabstaende. An einem echten Paper gemessen
(2026-09-13): 8.698 statt 14.856 Woerter, und 37 % der Tokens kommen in der
.tex-Quelle nicht vor, weil ganze Saetze zu einem Token verkleben.

Der Filter engt die Praeferenzkette ein, er ersetzt sie NICHT: Fallbacks derselben
Ausgabeform bleiben erhalten. Das ist der Unterschied zu `nur_backend`, das auf
genau ein Backend festnagelt und jeden Fallback verliert.
"""

from __future__ import annotations

import pytest

from doc_services import AUSGABEFORMEN
from doc_services.config import Auswahl, BackendLage
from doc_services.extract import ExtraktionsFehler, extrahieren


def _lage(backend_id: str, produces: str, fmt: str = "pdf") -> BackendLage:
    return BackendLage(
        id=backend_id, format=fmt, produces=produces, license="MIT",
        verfuegbar=True, begruendung="", rang=0, abgeschaltet=False,
    )


class _FesteRegistry:
    """Registry-Ersatz mit einer bekannten Kette — kein Zugriff auf die echte Config."""

    def __init__(self, kette):
        self.kette = kette
        self.gemerkt = []

    def aufloesen(self, fmt):
        return Auswahl(format=fmt, kette=list(self.kette), ausgeschlossen=[])

    def merke_ergebnis(self, fmt, backend_id, erfolg):
        self.gemerkt.append((fmt, backend_id, erfolg))


@pytest.fixture
def pdf(tmp_path):
    ziel = tmp_path / "probe.pdf"
    ziel.write_bytes(b"%PDF-1.4\n%%EOF\n")   # Inhalt egal: die Backends sind gestellt
    return ziel


@pytest.fixture
def backends(monkeypatch):
    """Zwei markdown- und zwei text-Backends, die ihren Namen zurueckgeben."""
    from doc_services import extract

    gerufen = []

    def mach(name):
        def fn(pfad):
            gerufen.append(name)
            return f"Inhalt von {name}"
        return fn

    tabelle = {n: mach(n) for n in ("markitdown", "md-zwei", "pypdf-native", "text-zwei")}
    monkeypatch.setattr(extract, "BACKENDS", tabelle)
    return gerufen


KETTE = [
    _lage("markitdown", "markdown"),
    _lage("md-zwei", "markdown"),
    _lage("pypdf-native", "text"),
    _lage("text-zwei", "text"),
]


def test_ohne_angabe_aendert_sich_nichts(pdf, backends):
    """Der Default bleibt die konfigurierte Kette — kein bestehender Aufrufer merkt etwas."""
    erg = extrahieren(pdf, reg=_FesteRegistry(KETTE), lernen=False)
    assert erg.backend == "markitdown"
    assert erg.produces == "markdown"
    assert backends == ["markitdown"]


def test_text_waehlt_das_erste_text_backend(pdf, backends):
    erg = extrahieren(pdf, reg=_FesteRegistry(KETTE), lernen=False, produces="text")
    assert erg.backend == "pypdf-native"
    assert erg.produces == "text"
    assert "markitdown" not in backends, "ein markdown-Backend wurde trotz produces='text' benutzt"


def test_markdown_waehlt_das_erste_markdown_backend(pdf, backends):
    erg = extrahieren(pdf, reg=_FesteRegistry(KETTE), lernen=False, produces="markdown")
    assert erg.backend == "markitdown"


def test_fallback_innerhalb_der_ausgabeform_bleibt_erhalten(pdf, monkeypatch):
    """Der Unterschied zu nur_backend: faellt das erste Text-Backend aus, greift das zweite."""
    from doc_services import extract

    gerufen = []

    def kaputt(pfad):
        gerufen.append("pypdf-native")
        raise RuntimeError("Backend kaputt")

    def gut(pfad):
        gerufen.append("text-zwei")
        return "Fliesstext"

    monkeypatch.setattr(extract, "BACKENDS", {
        "markitdown": lambda p: "sollte nicht laufen",
        "md-zwei": lambda p: "sollte nicht laufen",
        "pypdf-native": kaputt,
        "text-zwei": gut,
    })

    erg = extrahieren(pdf, reg=_FesteRegistry(KETTE), lernen=False, produces="text")
    assert erg.backend == "text-zwei"
    assert gerufen == ["pypdf-native", "text-zwei"]
    assert ("pypdf-native", "RuntimeError: Backend kaputt") in [
        (b, f) for b, f in erg.versuche if b == "pypdf-native"
    ]


def test_nur_backend_verliert_den_fallback(pdf, monkeypatch):
    """Gegenprobe, damit der Unterschied der beiden Schalter nicht nur behauptet ist."""
    from doc_services import extract

    monkeypatch.setattr(extract, "BACKENDS", {
        "pypdf-native": lambda p: (_ for _ in ()).throw(RuntimeError("kaputt")),
        "text-zwei": lambda p: "Fliesstext",
    })
    with pytest.raises(ExtraktionsFehler):
        extrahieren(pdf, reg=_FesteRegistry(KETTE), lernen=False, nur_backend="pypdf-native")


def test_unbekannte_ausgabeform_scheitert_laut(pdf):
    """Ein Tippfehler darf nicht als 'keine Angabe' durchgehen."""
    with pytest.raises(ExtraktionsFehler) as excinfo:
        extrahieren(pdf, reg=_FesteRegistry(KETTE), lernen=False, produces="txt")
    assert "txt" in str(excinfo.value)
    assert "text" in str(excinfo.value), "die Meldung muss die erlaubten Formen nennen"


def test_keine_passende_ausgabeform_nennt_die_bedingung(pdf, backends):
    nur_markdown = [_lage("markitdown", "markdown")]
    with pytest.raises(ExtraktionsFehler) as excinfo:
        extrahieren(pdf, reg=_FesteRegistry(nur_markdown), lernen=False, produces="text")
    assert "produces='text'" in str(excinfo.value)


def test_ausgabeformen_deckt_die_katalogwerte(pdf):
    assert {"text", "markdown"} == AUSGABEFORMEN
