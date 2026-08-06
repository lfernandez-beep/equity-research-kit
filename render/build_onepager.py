"""Arma el diccionario del one-pager a partir del JSON del scraper.

Los numeros salen del JSON; la narrativa (tesis, fortalezas, riesgos) se
escribe aparte y se pasa en 'narrative'. La separacion es a proposito: los
datos son reproducibles, el juicio de inversion es de quien firma el informe.
"""
from __future__ import annotations

from . import charts


def _loc(s: str) -> str:
    """Convencion local: coma decimal, punto separador de miles."""
    return s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def pct(x, digits: int = 1, dash: str = "n/d") -> str:
    return _loc(f"{x * 100:.{digits}f}") + "%" if isinstance(x, (int, float)) else dash


def mult(x, digits: int = 1, dash: str = "n/d") -> str:
    return _loc(f"{x:.{digits}f}") + "x" if isinstance(x, (int, float)) else dash


def usd(x, dash: str = "n/d") -> str:
    """Siempre en millones, para que las magnitudes sean comparables de un vistazo."""
    if not isinstance(x, (int, float)):
        return dash
    if abs(x) >= 1e6:
        return "USD " + _loc(f"{x / 1e6:,.0f}") + "M"
    return "USD " + _loc(f"{x:,.0f}")


def money(x, dash: str = "n/d") -> str:
    return _loc(f"{x:,.2f}") if isinstance(x, (int, float)) else dash


def num(x, digits: int = 2, dash: str = "n/d") -> str:
    return _loc(f"{x:.{digits}f}") if isinstance(x, (int, float)) else dash


def build(data: dict, narrative: dict) -> dict:
    """data = JSON del scraper. narrative = tesis y juicio escritos a mano."""
    prof = data.get("profile", {})
    r = data.get("computed_ratios", {}) or {}
    val = r.get("valuation", {})
    profit = r.get("profitability", {})
    growth = r.get("growth", {})
    solv = r.get("solvency", {})
    stats_ = (data.get("statistics") or {}).get("vs", {}).get("SPY", {})

    price = val.get("price")
    target = narrative["target"]["base"]
    upside = (target / price - 1) if price else None

    header = {
        "eyebrow": narrative.get("eyebrow", "Equity research · Nota de inicio"),
        "tagline": narrative["tagline"],
        "source_line": narrative.get(
            "source_line",
            f"Fuentes: SEC EDGAR, Yahoo Finance, stockanalysis.com — {data['meta']['generated_at'][:10]}",
        ),
        "kpis": [
            {"label": "Precio", "value": money(price), "tone": ""},
            {"label": "Precio objetivo", "value": money(target), "tone": ""},
            {
                "label": "Upside",
                "value": pct(upside, 1),
                "tone": "up" if (upside or 0) > 0 else "down",
            },
            {"label": "Market cap", "value": usd(val.get("market_cap")), "tone": ""},
        ],
    }

    call = {
        "rating": narrative["rating"],
        "rating_sub": narrative.get("rating_sub", "recomendación · horizonte 12m"),
        "pill": narrative.get("pill"),
        "pill_class": narrative.get("pill_class", ""),
    }

    snapshot = [
        {"k": "Ticker / mercado", "v": f"{data['meta']['ticker']} · {prof.get('exchange', 'n/d')}"},
        {"k": "Sector / industria", "v": f"{prof.get('sector', 'n/d')} · {prof.get('industry', 'n/d')}"},
        {"k": "Ingresos (LTM)", "v": usd((r.get('ttm') or {}).get('revenue'))},
        {"k": "EBITDA (LTM)", "v": usd((r.get('ttm') or {}).get('ebitda'))},
        {"k": "Margen EBITDA", "v": pct(profit.get("ebitda_margin"))},
        {"k": "Margen neto", "v": pct(profit.get("net_margin"))},
        {"k": "ROE", "v": pct(profit.get("roe"))},
        {"k": "Crecimiento de ingresos (a/a)", "v": pct(growth.get("revenue_yoy"))},
        {"k": "P/E (LTM / fwd)", "v": f"{mult(val.get('pe_ttm'))} / {mult(val.get('pe_forward'))}"},
        {"k": "EV / EBITDA", "v": mult(val.get("ev_ebitda"))},
        {"k": "FCF yield", "v": pct(val.get("fcf_yield"))},
        {"k": "Deuda neta / EBITDA", "v": mult(solv.get("net_debt_ebitda"))},
        {"k": "Beta (propia, 5a semanal vs. SPY)",
         "v": f"{num(stats_.get('beta_raw'))} · R² {num(stats_.get('r_squared'))}"},
    ]

    return {
        "company": {
            "name": prof.get("longName") or data["meta"].get("legal_name") or data["meta"]["ticker"],
            "ticker": data["meta"]["ticker"],
        },
        "header": header,
        "call": call,
        "thesis": narrative["thesis"],
        "bull": narrative["bull"],
        "bear": narrative["bear"],
        "snapshot": snapshot,
        "guidance": narrative.get("guidance"),
        "peers": narrative.get("peers"),
        "valuation_chart": {
            "title": "Rango de valuación y precio objetivo",
            "svg": charts.target_range(
                low=narrative["target"]["bear"],
                base=narrative["target"]["base"],
                high=narrative["target"]["bull"],
                current=price,
            ),
            "caption": narrative["target"].get("caption", ""),
            "ref": narrative["target"].get("ref", ""),
        },
        "disclaimer": narrative["disclaimer"],
        "signoff": narrative["signoff"],
    }
