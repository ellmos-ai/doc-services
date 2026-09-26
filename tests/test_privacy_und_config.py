# SPDX-License-Identifier: MIT
"""Tests der Datenschutzpruefung (E06) und der Praeferenzschicht (E02)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from doc_services.config import Registry
from doc_services.privacy import (
    GELB,
    GRUEN,
    ROT,
    Klassifikator,
    darf_weitergegeben_werden,
)

# ---------------------------------------------------------------- Datenschutz

def test_die_luecke_die_caveman_hatte(tmp_path):
    """Kernfall aus E06: Zugangsdaten in einem unverdaechtig benannten Dokument.

    caveman's Dateinamen-Guard liess einen frei gewaehlten Ordnernamen fuer
    Zugangsdaten (z. B. `CREDENTIALS/<anbieter>/webhosting.md`) durch, weil
    weder Ordner noch Dateiname in seiner Liste stehen. Die Inhaltspruefung
    muss hier greifen — und zusaetzlich der Pfadhinweis.
    """
    ordner = tmp_path / "CREDENTIALS" / "beispiel-anbieter"
    ordner.mkdir(parents=True)
    datei = ordner / "webhosting.md"
    datei.write_text(
        "# Beispiel Webhosting\n\nHost: acc123.example-hosting.tld\n"
        "password = S3hrGeheim!2026\n",
        encoding="utf-8",
    )
    erlaubt, befund = darf_weitergegeben_werden(datei)
    assert not erlaubt, "Zugangsdaten duerfen nicht durchgehen"
    assert befund.ampel == ROT
    assert befund.pfad_hinweis is not None, "Pfad 'CREDENTIALS' sollte zusaetzlich auffallen"


def test_treffer_werden_maskiert(tmp_path):
    """Der Bericht darf das Geheimnis nicht selbst ausplaudern."""
    datei = tmp_path / "notiz.md"
    datei.write_text("api_key = sk-abcdefghijklmnopqrstuvwxyz012345\n", encoding="utf-8")
    befund = Klassifikator().datei(datei)
    assert befund.ampel == ROT
    for fund in befund.funde:
        for treffer in fund.treffer:
            assert "abcdefghijklmnop" not in treffer, "Klartext im Bericht"


@pytest.mark.parametrize("text,erwartet", [
    ("Ganz normaler Satz ohne alles.", GRUEN),
    ("IBAN DE89 3704 0044 0532 0130 00 bitte pruefen", ROT),
    ("-----BEGIN OPENSSH PRIVATE KEY-----", ROT),
    ("Diagnose: Verdacht auf Migräne", ROT),
    ("Melde dich unter person@example.org", GELB),
    ("Wohnhaft Musterstraße 12", GELB),
])
def test_ampelstufen(text, erwartet):
    assert Klassifikator().text(text).ampel == erwartet


def test_gelb_blockiert_standardmaessig_und_kann_freigegeben_werden():
    """Streng als Default, Lockerung nur auf ausdrueckliche Entscheidung."""
    text = "Kontakt: person@example.org"
    streng, b1 = darf_weitergegeben_werden(text, ist_text=True)
    locker, b2 = darf_weitergegeben_werden(text, ist_text=True, erlaube_gelb=True)
    assert b1.ampel == GELB and not streng
    assert b2.ampel == GELB and locker


def test_unbedenkliche_datei_geht_durch(tmp_path):
    datei = tmp_path / "readme.md"
    datei.write_text("# Projekt\n\nEine harmlose Beschreibung.\n", encoding="utf-8")
    erlaubt, befund = darf_weitergegeben_werden(datei)
    assert erlaubt and befund.unbedenklich


# ---------------------------------------------------------------- Praeferenzen

@pytest.fixture()
def reg(tmp_path) -> Registry:
    return Registry(config_pfad=tmp_path / "config.json")


def test_katalog_ist_lesbar(reg):
    assert "docx" in reg.formate() and "pdf" in reg.formate()


def test_praeferenz_bestimmt_reihenfolge(reg):
    """Das Beispiel des Nutzers: zwei Optionen, bevorzugt die zweite."""
    reg.setze_praeferenz("xlsx", ["openpyxl-native", "markitdown"])
    a = reg.aufloesen("xlsx")
    alle = [b.id for b in a.kette] + [b.id for b in a.ausgeschlossen]
    assert alle.index("openpyxl-native") < alle.index("markitdown")


def test_unbekannte_backend_id_wird_abgelehnt(reg):
    with pytest.raises(ValueError, match="Unbekannte Backend-IDs"):
        reg.setze_praeferenz("xlsx", ["gibtsnicht"])


def test_ausgeschlossene_tragen_eine_begruendung(reg):
    for fmt in reg.formate():
        for b in reg.aufloesen(fmt).ausgeschlossen:
            assert b.begruendung and b.begruendung != "verfuegbar", (
                f"{fmt}:{b.id} ist ausgeschlossen, sagt aber nicht warum"
            )


def test_abschalten_wirkt(reg):
    reg.config.setdefault("disabled", []).append("markitdown")
    a = reg.aufloesen("pdf")
    assert "markitdown" not in [b.id for b in a.kette]
    assert any("abgeschaltet" in b.begruendung for b in a.ausgeschlossen)


def test_lernen_zaehlt_mit_aber_sortiert_nicht_um(reg):
    """Erfahrung wird gemessen — die Reihenfolge aendert sich nicht von selbst."""
    reg.setze_praeferenz("pdf", ["pypdf-native", "markitdown"])
    vorher = [b.id for b in reg.aufloesen("pdf").kette]
    for _ in range(8):
        reg.merke_ergebnis("pdf", "pypdf-native", erfolg=False)
        reg.merke_ergebnis("pdf", "markitdown", erfolg=True)
    assert [b.id for b in reg.aufloesen("pdf").kette] == vorher, "still umsortiert"


def test_umsortierung_wird_vorgeschlagen(reg):
    """Bei klarer Erfahrungslage kommt ein begruendeter Vorschlag."""
    reg.setze_praeferenz("pdf", ["pypdf-native", "markitdown"])
    verfuegbar = {b.id for b in reg.aufloesen("pdf").kette}
    if not {"pypdf-native", "markitdown"} <= verfuegbar:
        pytest.skip("beide PDF-Backends muessen installiert sein")
    for _ in range(10):
        reg.merke_ergebnis("pdf", "pypdf-native", erfolg=False)
        reg.merke_ergebnis("pdf", "markitdown", erfolg=True)
    v = reg.umsortierung_vorschlagen(mindestlaeufe=5)
    assert any(x["format"] == "pdf" and x["vorschlag"] == "markitdown" for x in v)


def test_config_wird_gespeichert_und_gelesen(tmp_path):
    ziel = tmp_path / "c.json"
    r1 = Registry(config_pfad=ziel)
    r1.setze_praeferenz("docx", ["python-docx-native", "markitdown"])
    r1.speichern()
    gelesen = json.loads(Path(ziel).read_text(encoding="utf-8"))
    assert gelesen["preferences"]["docx"][0] == "python-docx-native"
    assert Registry(config_pfad=ziel).config["preferences"]["docx"][0] == "python-docx-native"


def test_lagebericht_nennt_jedes_format(reg):
    bericht = reg.lagebericht()
    for fmt in reg.formate():
        assert f".{fmt}" in bericht
