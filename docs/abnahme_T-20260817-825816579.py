# SPDX-License-Identifier: MIT
"""Abnahme zu Ticket T-20260817-825816579 an einer lokal angegebenen Datei.

Kriterium aus dem Ticket: Die extrahierten Zeichen fallen von ~46.990 auf die
Größenordnung 2.300-6.000, und die eindeutigen Zellen entsprechen der Anzahl
ausgegebener Segmente je Zeile.
"""
import argparse
from pathlib import Path

from doc_services.extract import _b_python_docx, _zellen_einer_zeile, extrahieren


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prüft die Tabellenzellen-Korrektur an einer lokalen DOCX-Datei."
    )
    parser.add_argument("datei", type=Path, help="Pfad zur lokalen DOCX-Referenzdatei")
    datei = parser.parse_args().datei

    if not datei.exists():
        print(f"Referenzdatei fehlt: {datei}")
        return 1

    from docx import Document

    print("=" * 76)
    print("Abnahme T-20260817-825816579 - verbundene Tabellenzellen")
    print("=" * 76)

    doc = Document(str(datei))
    naiv = eindeutig = 0
    for tabelle in doc.tables:
        for zeile in tabelle.rows:
            naiv += len([c.text.strip() for c in zeile.cells if c.text.strip()])
            eindeutig += len(_zellen_einer_zeile(zeile))

    print(f"  Zellen, naiv gezählt    : {naiv}")
    print(f"  Zellen, dedupliziert    : {eindeutig}")
    if eindeutig:
        print(f"  Faktor vorher           : {naiv / eindeutig:.1f} x")

    neu = _b_python_docx(datei)
    print(f"\n  Zeichen NEU (mit Fix)   : {len(neu):,}")
    print("  Zeichen ALT (Ticket)    : 46.990")
    print(f"  Ersparnis               : {46990 - len(neu):,} Zeichen "
          f"(~{(46990 - len(neu)) / 3.5:,.0f} Tokens grob)")

    e = extrahieren(datei, lernen=False)
    print(f"\n  Kette gewählt           : {e.backend} ({e.produces})")
    print(f"  Versuche                : {e.versuche}")
    print(f"  Zeichen ueber Kette     : {e.zeichen:,}")

    kriterium = 2300 <= len(neu) <= 6000
    print("\n" + "-" * 76)
    print(f"  KRITERIUM 2.300-6.000 Zeichen: {'ERFÜLLT' if kriterium else 'VERFEHLT'}")
    print("=" * 76)
    return 0 if kriterium else 2


if __name__ == "__main__":
    raise SystemExit(main())
