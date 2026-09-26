<img src="assets/banner.png" width="100%" alt="doc-services banner">

# doc-services

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](pyproject.toml)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen.svg)](.github/workflows/ci.yml)
[![Egress: Zero](https://img.shields.io/badge/Egress-Zero%20(Local--First)-success.svg)](SECURITY.md)
[![Ausfhrung: RunAsInvoker](https://img.shields.io/badge/Ausf%C3%BChrung-RunAsInvoker-blue.svg)](SECURITY.md)

**Dokumentenextraktion, OCR und Datenschutzprüfung — BACH-unabhängig, permissiv lizenziert, mit lernender Backend-Präferenz.**

[English](README.md) · Deutsch · [Sicherheitsrichtlinie](SECURITY.md) · [LLM-Kontextindex](llms.txt) · [Changelog](CHANGELOG.md) · [Marketing-Log](MARKETING-LOG.txt)

---

## Wozu

Ein Agent, der Dokumente lesen soll, steht vor drei Fragen: *Womit* lese ich dieses Format,
*was tue ich*, wenn das Werkzeug fehlt, und *darf* der Inhalt überhaupt weitergegeben werden.
Dieses Modul beantwortet alle drei an einer Stelle.

Herausgelöst aus `BACH/system/hub/_services/document/` (MIT, eigenes Copyright) und dabei von
BACH entkoppelt: keine Importe aus `hub`/`tools`, keine SQLite-Kopplung, keine Klientenlogik.

## Die drei Bausteine

| Modul | Aufgabe |
|---|---|
| `extract` | Datei → Text/Markdown über eine Präferenzkette mit ehrlichem Fallback |
| `ocr` | Tesseract für Bilder und PDFs, Rendering über **pypdfium2** |
| `privacy` | Inhaltsbasierte Ampelprüfung vor Weitergabe an Dritte |
| `config` | Katalog (`profil.json`) + eigene Lage (`config.json`), lernend |

## Zwei Dinge, die dieses Modul bewusst anders macht

**1. Verbundene Tabellenzellen werden nicht mehr vervielfacht.**
`python-docx` liefert eine über mehrere Spalten verbundene Zelle *einmal pro Rasterspalte*.
Wer nicht dedupliziert, schreibt sie entsprechend oft in den Text. An einer realen 25-KB-Datei
gemessen: **785 gezählte gegen 44 eindeutige Zellen** — Faktor 17,8, rund **12.750 Tokens**
Verschwendung in einer einzigen Datei. Hier wird über die Identität des `tc`-XML-Elements
dedupliziert. (`id(zelle)` genügt nicht — python-docx erzeugt bei jedem Zugriff neue Wrapper.)

**2. Keine AGPL-Bindung.**
PDF-Rendering läuft ausschließlich über `pypdfium2` (BSD-3-Clause / Apache-2.0). PyMuPDF
(`fitz`, AGPL) wird nirgends importiert. `tests/test_no_agpl.py` hält das fest — ein Test statt
einer Notiz, weil eine Notiz niemanden aufhält.

## Lernende Präferenz statt fester Verdrahtung

Zwei Dateien mit verschiedenen Rollen:

- **`profil.json`** — Katalog: was es für ein Format *theoretisch gibt*, samt Stärken, Schwächen
  und Lizenz. Kennt auch Backends, die hier nicht installiert sind.
- **`config.json`** — unsere Lage: was davon *installiert* ist, was wir *bevorzugen*, was
  abgeschaltet ist, plus die gezählten Erfahrungswerte.

```python
from doc_services import registry, extrahieren

reg = registry()
print(reg.lagebericht())          # was kennen wir, was haben wir, was nutzen wir

reg.setze_praeferenz("xlsx", ["openpyxl-native", "markitdown"])   # bevorzugt 1, Fallback 2
reg.speichern()

e = extrahieren("bericht.docx")
print(e.backend, e.produces, e.zeichen)
for hinweis in e.hinweise:
    print("Hinweis:", hinweis)
```

### Ausgabeform verlangen: `produces`

Wer den Text **weiterverarbeitet** statt ihn anzuzeigen — Schwärzung, Suche, Regeln auf
Wortgrenzen — braucht Fließtext, keine Markdown-Auszeichnung:

```python
e = extrahieren("paper.pdf", produces="text")   # Kette bleibt, nur auf text-Backends eingeengt
```

Bei LaTeX-PDFs ist das keine Geschmacksfrage. An einem echten Paper gemessen (2026-09-13):
markitdown liefert **8.698 statt 14.856 Wörtern**, und 37 % der Tokens kommen in der
`.tex`-Quelle gar nicht vor — ganze Sätze verkleben zu einem Token, weil die Wortabstände
verloren gehen. Mit `produces="text"` stimmt das Ergebnis Byte für Byte mit `pypdf` überein.

`produces` engt die Präferenzkette **ein**, es ersetzt sie nicht: Fallbacks derselben
Ausgabeform bleiben erhalten. Das ist der Unterschied zu `nur_backend`, das auf genau ein
Backend festnagelt und jeden Fallback verliert.

**Lernen heißt hier nicht, dass sich die Reihenfolge heimlich ändert.** Erfolge und Fehlschläge
werden gezählt und sichtbar gemacht; eine Umsortierung *schlägt* `umsortierung_vorschlagen()`
vor, entschieden wird sie vom Menschen. Stilles Selbstumbauen wäre in einer Kette, die Dokumente
an ein LLM gibt, das falsche Verhalten.

## Datenschutz: Inhalt statt Dateiname

```python
from doc_services import darf_weitergegeben_werden

erlaubt, befund = darf_weitergegeben_werden("unterlagen/notiz.md")
if not erlaubt:
    print(befund.bericht())
```

Ein Guard, der nur Dateinamen prüft, übersieht Zugangsdaten in unverdächtig benannten Dateien —
belegt an `CREDENTIALS/<anbieter>/webhosting.md`, das ein reiner Namensfilter durchlässt. Deshalb
prüft dieses Modul den **Inhalt** (IBAN, Steuer-ID, Sozialversicherungsnummer, Gesundheitsdaten,
private Schlüssel, API-Token) und nutzt Pfadmuster nur *zusätzlich*.

Standard ist **fail-closed**: ROT und GELB blockieren. Gefundene Treffer werden im Bericht
maskiert — ein Prüfbericht, der das Geheimnis ausplaudert, wäre sinnlos.

## Installation

```bash
pip install -e ".[all]"      # alles
pip install -e ".[markitdown,office,pdf]"   # ohne OCR
```

Harte Abhängigkeiten gibt es bewusst keine: Das Modul erkennt zur Laufzeit, was vorhanden ist,
und meldet Fehlendes **mit Begründung** statt mit einem nackten „geht nicht".

Für OCR zusätzlich Tesseract mit deutschem Sprachpaket installieren.

## Tests

```bash
pytest -ra -v
```

Umfassende Unit- und Vertragstest-Suiten sichern Copyleft-Freiheit, Tabellenzellen-Deduplizierung, Datenschutzfilter, Backend-Präferenzen und Repository-Hygiene ab.


## Herkunft und Entscheidungen

Entstanden aus den Entscheidungen E01–E08 vom 2026-08-18
(`_control-center/_DECISIONS/DECISION-BRIEFING_caveman-markitdown_2026-08-17.md`).
Der Zellen-Fix ist Ticket `T-20260817-825816579`, der Lizenzwechsel Entscheidung E08.

**Lizenz:** MIT
