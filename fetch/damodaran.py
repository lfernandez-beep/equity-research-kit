"""Datasets de Aswath Damodaran (NYU Stern): benchmarks de industria.

Gratuitos y actualizados cada enero. Sirven de cross-check del beta propio y
de referencia para margenes, multiplos y equity risk premium por industria.
"""
from __future__ import annotations

import io
import logging

import pandas as pd

from .http import get

log = logging.getLogger(__name__)

BASE = "https://pages.stern.nyu.edu/~adamodar/pc/datasets/"
FILES = {
    "betas": "betas.xls",            # beta, D/E, unlevered beta por industria
    "margins": "margin.xls",         # margen bruto, operativo y neto
    "multiples": "pedata.xls",       # PE, PEG por industria
    "ev_multiples": "vebitda.xls",   # EV/EBITDA, EV/Sales
    "wacc": "wacc.xls",              # costo de capital por industria
}


def _load(fname: str) -> pd.DataFrame | None:
    try:
        raw = get(BASE + fname, min_gap=1.0).content
        # Los archivos traen encabezado de titulo antes de la tabla real
        for skip in (7, 6, 8, 9, 0):
            try:
                df = pd.read_excel(io.BytesIO(raw), skiprows=skip)
                if "Industry Name" in df.columns or "Industry name" in df.columns:
                    return df
            except Exception:  # noqa: BLE001, S110
                continue
    except Exception as exc:  # noqa: BLE001
        log.warning("damodaran %s: %s", fname, exc)
    return None


def industry_benchmarks(industry_hint: str | None = None) -> dict:
    """Devuelve las filas de cada dataset que matcheen la industria."""
    out: dict[str, object] = {"source": BASE, "matched_industry": None}

    for key, fname in FILES.items():
        df = _load(fname)
        if df is None:
            out[key] = None
            continue
        col = "Industry Name" if "Industry Name" in df.columns else df.columns[0]
        df[col] = df[col].astype(str).str.strip()

        if industry_hint:
            words = [w.lower() for w in industry_hint.split() if len(w) > 3]
            mask = df[col].str.lower().apply(lambda s: any(w in s for w in words))
            hit = df[mask]
            if not hit.empty:
                out["matched_industry"] = hit.iloc[0][col]
                out[key] = hit.head(3).astype(object).where(pd.notna(hit.head(3)), None).to_dict("records")
                continue
        # Sin match: se guarda el promedio del mercado como referencia
        total = df[df[col].str.lower().str.startswith("total market")]
        out[key] = (
            total.astype(object).where(pd.notna(total), None).to_dict("records")
            if not total.empty
            else None
        )

    return out
