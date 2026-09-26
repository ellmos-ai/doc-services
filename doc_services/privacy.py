# SPDX-License-Identifier: MIT
"""Inhaltsbasierte Datenschutzpruefung vor der Weitergabe an Dritte.

Herkunft: portiert aus BACH `system/hub/_services/document/privacy_classifier.py`
und `redaction_service.py` (MIT, eigenes Copyright), BACH-unabhaengig gemacht.

WARUM INHALT UND NICHT DATEINAME (Entscheidung E06 vom 2026-08-18):
Beim Test des caveman-Skills am 2026-08-17 zeigte sich, dass dessen Schutz rein
ueber Dateinamen und Pfadbestandteile arbeitet. Er blockiert `.env`,
`credentials.md`, `id_ed25519` und alles unter `.ssh/.aws/.gnupg/.kube/.docker`
- aber NICHT einen frei gewaehlten Ordnernamen fuer Zugangsdaten (z. B.
`<projektordner>\\CREDENTIALS\\<dienst>\\notes.md`), weil der Ordnername
nicht in seiner Liste steht und der Dateiname unverdaechtig klingt.
10 von 11 Faellen korrekt, und die eine Luecke betraf genau diese Art von
frei benanntem Zugangsdaten-Ordner.

Ein Dateinamen-Guard kann das prinzipiell nicht leisten. Deshalb prueft dieses
Modul den INHALT - und nutzt Pfadmuster nur zusaetzlich, nie allein.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ROT = "ROT"
GELB = "GELB"
GRUEN = "GRUEN"

# Definitiv sensibel — Fund bedeutet: nicht ungeprueft weitergeben.
MUSTER_ROT: dict[str, str] = {
    "IBAN (DE)": r"\bDE\d{2}\s?(?:\d{4}\s?){4}\d{2}\b",
    "IBAN (allgemein)": r"\b[A-Z]{2}\d{2}\s?[\dA-Z]{4}(?:\s?[\dA-Z]{4}){2,7}\b",
    "Steuernummer": r"\b\d{2,3}/\d{3}/\d{5}\b",
    "Steuer-ID": r"\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b",
    "Sozialversicherungsnr": r"\b\d{2}\s?\d{6}\s?[A-Z]\s?\d{3}\b",
    "Kreditkarte": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "Personalausweis": r"\b[A-Z]{1,2}\d{7}[0-9A-Z]\b",
    "Gesundheitsdaten": r"\b(?:Diagnose|Befund|Krankheit|Medikament|Therapie|Rezept|Patient(?:in)?)\b",
    "Privater Schluessel": r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----",
    "API-Token": r"\b(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,})\b",
    "Zugangsdaten-Zuweisung": r"(?i)\b(?:password|passwort|api[_-]?key|secret|token)\s*[:=]\s*\S{6,}",
}

# Moeglicherweise sensibel — Fund bedeutet: ansehen, dann entscheiden.
MUSTER_GELB: dict[str, str] = {
    "Geburtsdatum": r"\b(?:geb\.|geboren|Geburtsdatum)[:\s]*\d{1,2}\.\d{1,2}\.\d{2,4}\b",
    "Telefonnummer": r"\b(?:Tel|Fon|Telefon|Mobil)[.:\s]*[+\d][\d\s/()-]{8,}\b",
    "E-Mail-Adresse": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
    "Kontonummer": r"\b(?:Konto(?:nr)?|BLZ)[.:\s]*\d{6,}\b",
    # Deutsche Strassennamen sind meist Komposita ("Musterstraße"). Ein \b vor
    # dem Grundwort scheitert deshalb - das Grundwort muss als SUFFIX greifen.
    "Anschrift": r"(?i)\b[a-zäöüß-]*(?:stra(?:ß|ss)e|str\.|weg|platz|gasse|allee|ring)\s+\d{1,4}\s?[a-z]?\b",
}

# Zusaetzlicher Pfad-Hinweis — ergaenzt die Inhaltspruefung, ersetzt sie nicht.
PFAD_TEILE = {".ssh", ".aws", ".gnupg", ".kube", ".docker", "credentials", "secrets"}
PFAD_NAMEN = re.compile(
    r"(?i)^(\.env(\..+)?|\.netrc|credentials?(\..+)?|secrets?(\..+)?|passwords?(\..+)?"
    r"|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?|authorized_keys|known_hosts"
    r"|.*\.(pem|key|p12|pfx|jks|keystore|asc|gpg))$"
)


@dataclass
class Fund:
    muster: str
    stufe: str
    treffer: list[str] = field(default_factory=list)
    anzahl: int = 0


@dataclass
class Befund:
    ampel: str
    funde: list[Fund] = field(default_factory=list)
    pfad_hinweis: str | None = None

    @property
    def unbedenklich(self) -> bool:
        return self.ampel == GRUEN and self.pfad_hinweis is None

    def bericht(self) -> str:
        if self.unbedenklich:
            return "GRUEN - keine sensiblen Muster gefunden."
        zeilen = [f"{self.ampel} - {len(self.funde)} Musterart(en) gefunden:"]
        if self.pfad_hinweis:
            zeilen.append(f"  ! Pfad/Name: {self.pfad_hinweis}")
        for f in sorted(self.funde, key=lambda x: (x.stufe != ROT, x.muster)):
            zeilen.append(f"  [{f.stufe}] {f.muster}: {f.anzahl} Treffer")
        return "\n".join(zeilen)


class Klassifikator:
    """Prueft Text und Dateien auf sensible Inhalte."""

    def __init__(self, maskieren: bool = True, max_treffer: int = 3):
        self._rot = {n: re.compile(p) for n, p in MUSTER_ROT.items()}
        self._gelb = {n: re.compile(p) for n, p in MUSTER_GELB.items()}
        self.maskieren = maskieren
        self.max_treffer = max_treffer

    def _maskiere(self, wert: str) -> str:
        """Treffer nie im Klartext weiterreichen - sonst leckt der Bericht selbst."""
        if not self.maskieren:
            return wert
        w = wert.strip()
        return w[:2] + "…" + w[-2:] if len(w) > 8 else "…"

    def text(self, inhalt: str) -> Befund:
        funde: list[Fund] = []
        for stufe, menge in ((ROT, self._rot), (GELB, self._gelb)):
            for name, regex in menge.items():
                treffer = regex.findall(inhalt)
                if treffer:
                    flach = [t if isinstance(t, str) else " ".join(t) for t in treffer]
                    funde.append(Fund(
                        muster=name, stufe=stufe,
                        treffer=[self._maskiere(t) for t in flach[: self.max_treffer]],
                        anzahl=len(flach),
                    ))
        if any(f.stufe == ROT for f in funde):
            ampel = ROT
        elif funde:
            ampel = GELB
        else:
            ampel = GRUEN
        return Befund(ampel=ampel, funde=funde)

    def pfad(self, pfad: Path | str) -> str | None:
        """Zusaetzlicher Hinweis aus Name und Pfad - niemals als alleinige Pruefung."""
        p = Path(pfad)
        if PFAD_NAMEN.match(p.name):
            return f"Dateiname '{p.name}' deutet auf Zugangsdaten hin"
        teile = {t.lower() for t in p.parts}
        if (treffer := teile & PFAD_TEILE):
            return f"Pfad enthaelt '{sorted(treffer)[0]}'"
        return None

    def datei(self, pfad: Path | str, max_bytes: int = 2 * 1024 * 1024) -> Befund:
        p = Path(pfad)
        hinweis = self.pfad(p)
        try:
            inhalt = p.read_text(encoding="utf-8", errors="replace")[:max_bytes]
        except OSError as exc:
            b = Befund(ampel=GELB, pfad_hinweis=hinweis)
            b.funde.append(Fund(muster=f"nicht lesbar: {exc}", stufe=GELB, anzahl=0))
            return b
        b = self.text(inhalt)
        b.pfad_hinweis = hinweis
        if hinweis and b.ampel == GRUEN:
            b.ampel = GELB
        return b


def darf_weitergegeben_werden(
    pfad_oder_text: Path | str,
    ist_text: bool = False,
    erlaube_gelb: bool = False,
) -> tuple[bool, Befund]:
    """Fail-closed Torwaechter vor der Weitergabe an Dritte (LLM-API, Upload, Repo).

    Standard ist streng: ROT und GELB blockieren. `erlaube_gelb=True` laesst
    GELB durch - bewusst nur auf ausdrueckliche Entscheidung, nicht als Default.

    Returns:
        (erlaubt, befund) - der Befund traegt die Begruendung.
    """
    k = Klassifikator()
    befund = k.text(str(pfad_oder_text)) if ist_text else k.datei(pfad_oder_text)
    if befund.ampel == ROT:
        return False, befund
    if befund.ampel == GELB:
        return (erlaube_gelb, befund)
    return (befund.pfad_hinweis is None, befund)
