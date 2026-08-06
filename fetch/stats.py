"""Estadistica de mercado calculada por nosotros, no tomada de terceros.

Beta por regresion OLS contra el benchmark, R2, error estandar, volatilidad
anualizada, correlacion, max drawdown y beta ajustada de Blume. Tambien arma
el CAPM (ke) y el WACC, que es lo que alimenta la seccion de valuacion.
"""
from __future__ import annotations

import math

import numpy as np


def _returns(series: list[dict]) -> tuple[list[str], np.ndarray]:
    dates = [p["date"] for p in series]
    closes = np.array([p["close"] for p in series], dtype=float)
    rets = np.diff(closes) / closes[:-1]
    return dates[1:], rets


def _align(a: list[dict], b: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    da, ra = _returns(a)
    db, rb = _returns(b)
    mb = dict(zip(db, rb))
    pairs = [(x, mb[d]) for d, x in zip(da, ra) if d in mb]
    if not pairs:
        return np.array([]), np.array([])
    arr = np.array(pairs)
    return arr[:, 0], arr[:, 1]


def regression(stock: list[dict], bench: list[dict], periods_per_year: int = 52) -> dict:
    """Regresion OLS de los retornos del activo contra el benchmark."""
    y, x = _align(stock, bench)
    n = len(y)
    if n < 30:
        return {"error": f"muestra insuficiente ({n} observaciones)"}

    beta, alpha = np.polyfit(x, y, 1)
    resid = y - (alpha + beta * x)
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")
    se_beta = math.sqrt(ss_res / (n - 2) / np.sum((x - x.mean()) ** 2))

    return {
        "n_obs": n,
        "beta_raw": round(float(beta), 4),
        # Blume: los betas tienden a revertir a 1 en el tiempo
        "beta_adjusted": round(0.67 * float(beta) + 0.33, 4),
        "alpha_periodic": round(float(alpha), 6),
        "alpha_annualized": round(float(alpha) * periods_per_year, 4),
        "r_squared": round(float(r2), 4),
        "beta_std_error": round(float(se_beta), 4),
        "beta_ci95": [
            round(float(beta - 1.96 * se_beta), 4),
            round(float(beta + 1.96 * se_beta), 4),
        ],
        "correlation": round(float(np.corrcoef(y, x)[0, 1]), 4),
        # Puntos para el scatter de dispersion (igual que el reporte del CFA)
        "scatter": [[round(float(xi), 5), round(float(yi), 5)] for xi, yi in zip(x, y)],
    }


def risk_profile(stock: list[dict], periods_per_year: int = 52) -> dict:
    _, r = _returns(stock)
    if len(r) < 10:
        return {"error": "serie insuficiente"}

    closes = np.array([p["close"] for p in stock], dtype=float)
    peak = np.maximum.accumulate(closes)
    dd = (closes - peak) / peak

    total = closes[-1] / closes[0] - 1
    years = len(r) / periods_per_year

    return {
        "volatility_annualized": round(float(r.std(ddof=1) * math.sqrt(periods_per_year)), 4),
        "downside_deviation": round(
            float(r[r < 0].std(ddof=1) * math.sqrt(periods_per_year)), 4
        )
        if (r < 0).sum() > 1
        else None,
        "max_drawdown": round(float(dd.min()), 4),
        "total_return": round(float(total), 4),
        "cagr": round(float((1 + total) ** (1 / years) - 1), 4) if years > 0 else None,
        "skew": round(float(((r - r.mean()) ** 3).mean() / r.std() ** 3), 4),
        "kurtosis": round(float(((r - r.mean()) ** 4).mean() / r.std() ** 4 - 3), 4),
    }


def capm(beta: float, risk_free: float, erp: float) -> float:
    """Costo de capital propio. erp = equity risk premium (Damodaran)."""
    return risk_free + beta * erp


def wacc(
    *,
    ke: float,
    market_cap: float,
    total_debt: float,
    cost_of_debt: float,
    tax_rate: float = 0.21,
) -> dict:
    v = (market_cap or 0) + (total_debt or 0)
    if v <= 0:
        return {"error": "estructura de capital no disponible"}
    we, wd = market_cap / v, total_debt / v
    kd_after_tax = cost_of_debt * (1 - tax_rate)
    return {
        "weight_equity": round(we, 4),
        "weight_debt": round(wd, 4),
        "cost_of_equity": round(ke, 4),
        "cost_of_debt_pretax": round(cost_of_debt, 4),
        "cost_of_debt_after_tax": round(kd_after_tax, 4),
        "tax_rate": tax_rate,
        "wacc": round(we * ke + wd * kd_after_tax, 4),
    }


def compute(prices: dict, benchmarks: dict, interval: str = "1wk") -> dict:
    ppy = 52 if interval == "1wk" else 252
    out = {"interval": interval, "periods_per_year": ppy, "vs": {}}
    out["risk"] = risk_profile(prices, ppy)
    for name, series in benchmarks.items():
        if series:
            out["vs"][name] = regression(prices, series, ppy)
    return out
