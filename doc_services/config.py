# SPDX-License-Identifier: MIT
"""Praeferenz- und Lernschicht fuer doc-services.

Zwei getrennte Dateien mit klar verschiedenen Rollen — das ist Absicht:

  profil.json   KATALOG: was es fuer ein Format theoretisch GIBT.
                Wird gepflegt/erweitert, wenn neue Werkzeuge bekannt werden.
                Kennt auch Backends, die hier gar nicht installiert sind.

  config.json   UNSERE LAGE: was davon installiert ist, was wir BEVORZUGEN,
                was abgeschaltet ist, plus die gelernten Erfahrungswerte.

Der Resolver bringt beides zusammen: Praeferenzreihenfolge, gefiltert auf das,
was tatsaechlich verfuegbar ist, mit Fallback-Kette. Beispiel des Nutzers:
"fuer xlsx zwei Optionen, bevorzugt 2, Fallback 1" -> preferences["xlsx"] = [2, 1].

Lernen heisst hier NICHT, dass sich die Reihenfolge heimlich aendert. Erfolge und
Fehlschlaege werden gezaehlt und sichtbar gemacht; eine Umsortierung schlaegt der
Skill vor, entschieden wird sie vom Nutzer. Stilles Selbstumbauen waere in einer
Kette, die Dokumente an ein LLM gibt, das falsche Verhalten.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------
# Ablageorte
# ----------------------------------------------------------------------------

def _paket_dir() -> Path:
    return Path(__file__).resolve().parent


def _default_profil_pfad() -> Path:
    """Katalog liegt beim Paket — er gehoert zum Lieferumfang."""
    return _paket_dir().parent / "profil.json"


def _default_config_pfad() -> Path:
    """Nutzerlage liegt ausserhalb des Repos (nicht versionierbar, hostabhaengig)."""
    override = os.environ.get("DOC_SERVICES_CONFIG")
    if override:
        return Path(override)
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / "doc-services" / "config.json"


# ----------------------------------------------------------------------------
# Verfuegbarkeitspruefung
# ----------------------------------------------------------------------------

def _python_paket_da(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _programm_da(name: str) -> bool:
    return shutil.which(name) is not None


def pruefe_verfuegbar(backend: dict[str, Any]) -> tuple[bool, str]:
    """Ist dieses Backend hier tatsaechlich benutzbar?

    Returns:
        (verfuegbar, begruendung) — die Begruendung wird angezeigt, damit
        "geht nicht" nie ohne Grund dasteht.
    """
    fehlend: list[str] = []
    for modul in backend.get("requires_python", []):
        if not _python_paket_da(modul):
            fehlend.append(f"Python-Paket '{modul}'")
    for prog in backend.get("requires_binary", []):
        if not _programm_da(prog):
            fehlend.append(f"Programm '{prog}'")
    if fehlend:
        return False, "fehlt: " + ", ".join(fehlend)
    return True, "verfuegbar"


# ----------------------------------------------------------------------------
# Datenmodell
# ----------------------------------------------------------------------------

@dataclass
class BackendLage:
    """Ein Backend fuer ein Format, mit allem was zur Auswahl noetig ist."""
    id: str
    format: str
    produces: str                 # "markdown" | "text"
    license: str
    verfuegbar: bool
    begruendung: str
    rang: int | None              # Position in der Praeferenz, None = nicht gelistet
    abgeschaltet: bool
    erfolge: int = 0
    fehlschlaege: int = 0

    @property
    def quote(self) -> float | None:
        n = self.erfolge + self.fehlschlaege
        return None if n == 0 else self.erfolge / n


@dataclass
class Auswahl:
    """Ergebnis einer Backend-Aufloesung fuer ein Format."""
    format: str
    kette: list[BackendLage] = field(default_factory=list)   # in Benutzungsreihenfolge
    ausgeschlossen: list[BackendLage] = field(default_factory=list)

    @property
    def bevorzugt(self) -> BackendLage | None:
        return self.kette[0] if self.kette else None

    @property
    def fallbacks(self) -> list[BackendLage]:
        return self.kette[1:]


# ----------------------------------------------------------------------------
# Registry
# ----------------------------------------------------------------------------

class Registry:
    """Bringt Katalog (profil.json) und Nutzerlage (config.json) zusammen."""

    def __init__(self, profil_pfad: Path | None = None, config_pfad: Path | None = None):
        self.profil_pfad = Path(profil_pfad) if profil_pfad else _default_profil_pfad()
        self.config_pfad = Path(config_pfad) if config_pfad else _default_config_pfad()
        self.profil = self._lade_profil()
        self.config = self._lade_config()

    # -- Laden / Speichern ---------------------------------------------------

    def _lade_profil(self) -> dict[str, Any]:
        if not self.profil_pfad.exists():
            raise FileNotFoundError(
                f"Katalog fehlt: {self.profil_pfad}. profil.json gehoert zum Lieferumfang "
                "des Moduls und darf nicht entfernt werden."
            )
        return json.loads(self.profil_pfad.read_text(encoding="utf-8"))

    def _lade_config(self) -> dict[str, Any]:
        if self.config_pfad.exists():
            return json.loads(self.config_pfad.read_text(encoding="utf-8"))
        return {
            "schema": 1,
            "preferences": {},
            "disabled": [],
            "stats": {},
            "hinweis": (
                "Automatisch angelegt. preferences[<format>] = Liste von Backend-IDs "
                "in Wunschreihenfolge; das erste verfuegbare gewinnt."
            ),
        }

    def speichern(self) -> Path:
        self.config_pfad.parent.mkdir(parents=True, exist_ok=True)
        self.config_pfad.write_text(
            json.dumps(self.config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return self.config_pfad

    # -- Abfragen ------------------------------------------------------------

    def formate(self) -> list[str]:
        return sorted(self.profil.get("formats", {}).keys())

    def _backends_fuer(self, fmt: str) -> list[dict[str, Any]]:
        return self.profil.get("formats", {}).get(fmt, {}).get("backends", [])

    def aufloesen(self, fmt: str) -> Auswahl:
        """Liefert die Benutzungsreihenfolge fuer ein Format.

        Reihenfolge: erst die in config.preferences genannten (in dieser Folge),
        dann alle uebrigen aus dem Katalog in Katalogreihenfolge. Nicht verfuegbare
        und abgeschaltete landen in `ausgeschlossen` — mit Begruendung.
        """
        fmt = fmt.lower().lstrip(".")
        praef: list[str] = self.config.get("preferences", {}).get(fmt, [])
        aus: list[str] = self.config.get("disabled", [])
        stats: dict[str, Any] = self.config.get("stats", {})

        backends = {b["id"]: b for b in self._backends_fuer(fmt)}
        reihenfolge = [bid for bid in praef if bid in backends]
        reihenfolge += [bid for bid in backends if bid not in reihenfolge]

        ergebnis = Auswahl(format=fmt)
        for bid in reihenfolge:
            b = backends[bid]
            verf, grund = pruefe_verfuegbar(b)
            abgesch = bid in aus
            s = stats.get(f"{fmt}:{bid}", {})
            lage = BackendLage(
                id=bid,
                format=fmt,
                produces=b.get("produces", "text"),
                license=b.get("license", "?"),
                verfuegbar=verf,
                begruendung="abgeschaltet (config.json)" if abgesch else grund,
                rang=praef.index(bid) if bid in praef else None,
                abgeschaltet=abgesch,
                erfolge=int(s.get("erfolge", 0)),
                fehlschlaege=int(s.get("fehlschlaege", 0)),
            )
            (ergebnis.kette if (verf and not abgesch) else ergebnis.ausgeschlossen).append(lage)
        return ergebnis

    # -- Pflege --------------------------------------------------------------

    def setze_praeferenz(self, fmt: str, reihenfolge: list[str]) -> None:
        """Legt die Wunschreihenfolge fest. Unbekannte IDs werden abgelehnt."""
        fmt = fmt.lower().lstrip(".")
        bekannt = {b["id"] for b in self._backends_fuer(fmt)}
        unbekannt = [b for b in reihenfolge if b not in bekannt]
        if unbekannt:
            raise ValueError(
                f"Unbekannte Backend-IDs fuer '{fmt}': {unbekannt}. "
                f"Bekannt sind: {sorted(bekannt)}"
            )
        self.config.setdefault("preferences", {})[fmt] = list(reihenfolge)

    def merke_ergebnis(self, fmt: str, backend_id: str, erfolg: bool) -> None:
        """Zaehlt einen Lauf mit. Aendert die Reihenfolge NICHT von selbst."""
        fmt = fmt.lower().lstrip(".")
        key = f"{fmt}:{backend_id}"
        s = self.config.setdefault("stats", {}).setdefault(key, {"erfolge": 0, "fehlschlaege": 0})
        s["erfolge" if erfolg else "fehlschlaege"] += 1

    def umsortierung_vorschlagen(self, mindestlaeufe: int = 5) -> list[dict[str, Any]]:
        """Wo widerspricht die Erfahrung der eingestellten Reihenfolge?

        Liefert Vorschlaege, fuehrt sie aber NICHT aus — die Entscheidung bleibt
        beim Nutzer (siehe Modul-Docstring).
        """
        vorschlaege = []
        for fmt in self.formate():
            a = self.aufloesen(fmt)
            messbar = [b for b in a.kette if (b.erfolge + b.fehlschlaege) >= mindestlaeufe]
            if len(messbar) < 2:
                continue
            best = max(messbar, key=lambda b: (b.quote or 0))
            if best is not messbar[0] and (best.quote or 0) > (messbar[0].quote or 0) + 0.10:
                vorschlaege.append({
                    "format": fmt,
                    "aktuell": messbar[0].id,
                    "aktuelle_quote": round(messbar[0].quote or 0, 3),
                    "vorschlag": best.id,
                    "vorschlag_quote": round(best.quote or 0, 3),
                    "begruendung": (
                        f"{best.id} liegt bei {round((best.quote or 0)*100)} % Erfolg, "
                        f"{messbar[0].id} nur bei {round((messbar[0].quote or 0)*100)} % "
                        f"(je >= {mindestlaeufe} Laeufe)."
                    ),
                })
        return vorschlaege

    # -- Bericht -------------------------------------------------------------

    def lagebericht(self) -> str:
        """Was kennen wir, was haben wir, was nutzen wir — als lesbarer Text."""
        zeilen = [
            "doc-services — Backend-Lage",
            f"  Katalog : {self.profil_pfad}",
            f"  Config  : {self.config_pfad}"
            + ("" if self.config_pfad.exists() else "   (noch nicht angelegt, Defaults aktiv)"),
            "",
        ]
        for fmt in self.formate():
            a = self.aufloesen(fmt)
            b = a.bevorzugt
            kopf = f"  .{fmt:<6} -> " + (f"{b.id} ({b.produces})" if b else "KEIN Backend verfuegbar")
            zeilen.append(kopf)
            for f_ in a.fallbacks:
                zeilen.append(f"           Fallback: {f_.id} ({f_.produces})")
            for x in a.ausgeschlossen:
                zeilen.append(f"           -- {x.id}: {x.begruendung}")
        return "\n".join(zeilen)


def registry(**kw: Any) -> Registry:
    return Registry(**kw)
