"""stockanalysis.com: multiplos, consenso de analistas, estimates y peers.

El sitio es Next.js: los datos vienen serializados en el payload de la pagina,
asi que se extraen del JSON embebido en vez de parsear la tabla renderizada.
Cubre en un solo lugar lo que de otra forma necesitaria tres scrapers.
"""
from __future__ import annotations

import re
import json
import logging

from .http import get

log = logging.getLogger(__name__)

BASE = "https://stockanalysis.com/stocks/{t}"


def _next_data(html: str) -> dict:
    """Extrae el payload de datos que Next.js embebe en la pagina."""
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S
    )
    if m:
        return json.loads(m.group(1)).get("props", {}).get("pageProps", {})

    # App Router: los datos vienen en chunks self.__next_f.push
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.S)
    if chunks:
        blob = "".join(chunks).encode().decode("unicode_escape", errors="ignore")
        for key in ("\"data\":{", "\"financialData\":{"):
            i = blob.find(key)
            if i == -1:
                continue
            start = blob.index("{", i + len(key) - 1)
            depth, j = 0, start
            while j < len(blob):
                if blob[j] == "{":
                    depth += 1
                elif blob[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            try:
                return json.loads(blob[start : j + 1])
            except json.JSONDecodeError:
                continue
    return {}


def _page(ticker: str, path: str = "") -> dict:
    url = BASE.format(t=ticker.lower()) + path
    html = get(url, min_gap=1.0).text
    data = _next_data(html)
    return {"url": url, "data": data, "html": html}


def overview(ticker: str) -> dict:
    """Quote, multiplos y estadisticas de la ficha principal."""
    p = _page(ticker)
    return {"source": p["url"], "payload": p["data"]}


def financials(ticker: str, statement: str = "", period: str = "quarterly") -> dict:
    """statement: '' (income), 'balance-sheet', 'cash-flow-statement', 'ratios'."""
    path = f"/financials/{statement}/" if statement else "/financials/"
    if period == "quarterly":
        path += "?p=quarterly"
    p = _page(ticker, path)
    return {"source": p["url"], "payload": p["data"]}


def forecast(ticker: str) -> dict:
    """Consenso de analistas: rating, price target y estimates forward."""
    p = _page(ticker, "/forecast/")
    return {"source": p["url"], "payload": p["data"]}


def statistics(ticker: str) -> dict:
    """Ratios de valuacion, rentabilidad, solvencia y datos de mercado."""
    p = _page(ticker, "/statistics/")
    return {"source": p["url"], "payload": p["data"]}


def peers(ticker: str) -> dict:
    """Comparables sugeridos por el sitio (misma industria)."""
    p = _page(ticker, "/comparison/")
    return {"source": p["url"], "payload": p["data"]}


def collect(ticker: str) -> dict:
    """Junta todo lo de stockanalysis tolerando fallos parciales."""
    out: dict[str, dict] = {}
    jobs = {
        "overview": lambda: overview(ticker),
        "statistics": lambda: statistics(ticker),
        "forecast": lambda: forecast(ticker),
        "income_q": lambda: financials(ticker, "", "quarterly"),
        "ratios": lambda: financials(ticker, "ratios", "quarterly"),
        "peers": lambda: peers(ticker),
    }
    for name, fn in jobs.items():
        try:
            out[name] = fn()
        except Exception as exc:  # noqa: BLE001
            log.warning("stockanalysis %s fallo: %s", name, exc)
            out[name] = {"error": str(exc)}
    return out
