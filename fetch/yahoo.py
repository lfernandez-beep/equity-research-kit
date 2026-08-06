"""Yahoo Finance (yfinance): precios historicos, perfil, consenso y holders.

Sirve para dos cosas que no cubre EDGAR: datos de mercado (precio, market cap,
multiplos) y la serie de precios que alimenta el calculo propio de beta.
Es un endpoint no oficial, asi que todo va envuelto en try/except.
"""
from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)

BENCHMARKS = ["SPY", "QQQ"]


def _safe(fn, default=None):
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001
        log.warning("yahoo: %s", exc)
        return default


def profile(ticker: str) -> dict:
    tk = yf.Ticker(ticker)
    info = _safe(lambda: tk.info, {}) or {}
    keep = [
        "shortName", "longName", "sector", "industry", "country", "website",
        "longBusinessSummary", "fullTimeEmployees", "currency", "exchange",
        "marketCap", "enterpriseValue", "sharesOutstanding", "floatShares",
        "currentPrice", "previousClose", "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
        "trailingPE", "forwardPE", "priceToBook", "enterpriseToEbitda",
        "enterpriseToRevenue", "pegRatio", "beta", "dividendYield",
        "payoutRatio", "profitMargins", "operatingMargins", "grossMargins",
        "returnOnEquity", "returnOnAssets", "revenueGrowth", "earningsGrowth",
        "totalCash", "totalDebt", "freeCashflow", "operatingCashflow",
        "targetMeanPrice", "targetHighPrice", "targetLowPrice",
        "recommendationKey", "numberOfAnalystOpinions",
    ]
    return {k: info.get(k) for k in keep if info.get(k) is not None}


def price_history(ticker: str, period: str = "5y", interval: str = "1wk") -> list[dict]:
    df = _safe(lambda: yf.Ticker(ticker).history(period=period, interval=interval))
    if df is None or df.empty:
        return []
    df = df.reset_index()
    date_col = "Date" if "Date" in df.columns else df.columns[0]
    return [
        {"date": str(pd.Timestamp(r[date_col]).date()), "close": float(r["Close"])}
        for _, r in df.iterrows()
        if pd.notna(r["Close"])
    ]


def analyst_data(ticker: str) -> dict:
    tk = yf.Ticker(ticker)

    def _df(attr):
        df = _safe(lambda: getattr(tk, attr))
        if df is None or not hasattr(df, "empty") or df.empty:
            return None
        return df.reset_index().astype(object).where(pd.notna(df.reset_index()), None).to_dict("records")

    return {
        "recommendations_summary": _df("recommendations_summary") or _df("recommendations"),
        "earnings_estimate": _df("earnings_estimate"),
        "revenue_estimate": _df("revenue_estimate"),
        "growth_estimates": _df("growth_estimates"),
        "eps_trend": _df("eps_trend"),
        "price_targets": _safe(lambda: tk.analyst_price_targets),
    }


def ownership(ticker: str) -> dict:
    tk = yf.Ticker(ticker)

    def _df(attr, n=15):
        df = _safe(lambda: getattr(tk, attr))
        if df is None or not hasattr(df, "empty") or df.empty:
            return None
        df = df.head(n).reset_index()
        return df.astype(object).where(pd.notna(df), None).to_dict("records")

    return {
        "institutional": _df("institutional_holders"),
        "major": _df("major_holders"),
    }


def calendar(ticker: str) -> dict:
    cal = _safe(lambda: yf.Ticker(ticker).calendar, {}) or {}
    return {k: str(v) for k, v in cal.items()} if isinstance(cal, dict) else {}


def benchmarks(period: str = "5y", interval: str = "1wk") -> dict[str, list[dict]]:
    return {b: price_history(b, period, interval) for b in BENCHMARKS}


def peer_quotes(tickers: list[str]) -> list[dict]:
    """Multiplos rapidos de cada comparable para la tabla de peers."""
    out = []
    for t in tickers:
        info = _safe(lambda t=t: yf.Ticker(t).info, {}) or {}
        if not info:
            continue
        out.append(
            {
                "ticker": t,
                "name": info.get("shortName"),
                "market_cap": info.get("marketCap"),
                "pe_fwd": info.get("forwardPE"),
                "pe_ttm": info.get("trailingPE"),
                "ev_ebitda": info.get("enterpriseToEbitda"),
                "ev_sales": info.get("enterpriseToRevenue"),
                "gross_margin": info.get("grossMargins"),
                "op_margin": info.get("operatingMargins"),
                "net_margin": info.get("profitMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "roe": info.get("returnOnEquity"),
                "beta": info.get("beta"),
            }
        )
    return out
