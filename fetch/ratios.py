"""Ratios calculados a partir de los estados de EDGAR + datos de mercado.

Cuatro bloques: profitability, growth, valuation y solvencia. Ademas los
ratios forward, que aplican los estimates de consenso sobre el precio actual
(lo que pediste como "ratios teniendo en cuenta esos estimativos").
"""
from __future__ import annotations


def _last(series: list[dict] | None, n: int = 1):
    if not series:
        return None
    vals = [r["val"] for r in series[-n:]]
    return vals[0] if n == 1 else vals


def _ttm(quarterly: list[dict] | None) -> float | None:
    """Suma los ultimos 4 trimestres (para lineas de flujo)."""
    if not quarterly or len(quarterly) < 4:
        return None
    return sum(r["val"] for r in quarterly[-4:])


def _div(a, b):
    if a is None or b in (None, 0):
        return None
    return a / b


def _cagr(series: list[dict] | None, years: int) -> float | None:
    if not series or len(series) < years + 1:
        return None
    first, last = series[-(years + 1)]["val"], series[-1]["val"]
    if first is None or last is None or first <= 0:
        return None
    return (last / first) ** (1 / years) - 1


def _yoy(series: list[dict] | None) -> float | None:
    if not series or len(series) < 2:
        return None
    prev, cur = series[-2]["val"], series[-1]["val"]
    return _div(cur - prev, abs(prev)) if prev else None


def build(financials: dict, market: dict) -> dict:
    """financials = salida de sec_edgar.financials; market = perfil de Yahoo."""
    a = financials.get("annual", {})
    q = financials.get("quarterly", {})

    rev_ttm = _ttm(q.get("revenue")) or _last(a.get("revenue"))
    ni_ttm = _ttm(q.get("net_income")) or _last(a.get("net_income"))
    op_ttm = _ttm(q.get("operating_income")) or _last(a.get("operating_income"))
    gp_ttm = _ttm(q.get("gross_profit")) or _last(a.get("gross_profit"))
    da_ttm = _ttm(q.get("dep_amort")) or _last(a.get("dep_amort")) or 0
    cfo_ttm = _ttm(q.get("cfo")) or _last(a.get("cfo"))
    capex_ttm = _ttm(q.get("capex")) or _last(a.get("capex")) or 0
    sbc_ttm = _ttm(q.get("sbc")) or 0

    ebitda_ttm = (op_ttm + da_ttm) if op_ttm is not None else None
    fcf_ttm = (cfo_ttm - capex_ttm) if cfo_ttm is not None else None

    equity = _last(q.get("equity")) or _last(a.get("equity"))
    assets = _last(q.get("total_assets")) or _last(a.get("total_assets"))
    cash = (_last(q.get("cash")) or _last(a.get("cash")) or 0) + (
        _last(q.get("short_term_investments")) or 0
    )
    debt = (_last(q.get("long_term_debt")) or 0) + (_last(q.get("short_term_debt")) or 0)
    if not debt:
        debt = market.get("totalDebt") or 0
    ca = _last(q.get("current_assets"))
    cl = _last(q.get("current_liabilities"))

    mcap = market.get("marketCap")
    price = market.get("currentPrice")
    ev = market.get("enterpriseValue") or (
        (mcap + debt - cash) if mcap is not None else None
    )

    profitability = {
        "gross_margin": _div(gp_ttm, rev_ttm),
        "operating_margin": _div(op_ttm, rev_ttm),
        "ebitda_margin": _div(ebitda_ttm, rev_ttm),
        "net_margin": _div(ni_ttm, rev_ttm),
        "fcf_margin": _div(fcf_ttm, rev_ttm),
        "roe": _div(ni_ttm, equity),
        "roa": _div(ni_ttm, assets),
        "roic": _div(op_ttm * 0.79 if op_ttm is not None else None, (equity or 0) + debt - cash)
        if equity
        else None,
        "sbc_pct_revenue": _div(sbc_ttm, rev_ttm),
        "cash_conversion": _div(fcf_ttm, ni_ttm),
    }

    growth = {
        "revenue_yoy": _yoy(a.get("revenue")),
        "revenue_cagr_3y": _cagr(a.get("revenue"), 3),
        "revenue_cagr_5y": _cagr(a.get("revenue"), 5),
        "ebitda_cagr_3y": None,
        "net_income_yoy": _yoy(a.get("net_income")),
        "net_income_cagr_3y": _cagr(a.get("net_income"), 3),
        "eps_yoy": _yoy(a.get("eps_diluted")),
        "eps_cagr_3y": _cagr(a.get("eps_diluted"), 3),
        "revenue_qoq_yoy": _div(
            (q.get("revenue") or [{}])[-1].get("val", 0)
            - (q.get("revenue") or [{}, {}, {}, {}, {}])[-5].get("val", 0),
            abs((q.get("revenue") or [{}, {}, {}, {}, {}])[-5].get("val", 1) or 1),
        )
        if len(q.get("revenue") or []) >= 5
        else None,
    }

    rule_of_40 = None
    if growth["revenue_yoy"] is not None and profitability["fcf_margin"] is not None:
        rule_of_40 = growth["revenue_yoy"] + profitability["fcf_margin"]

    valuation = {
        "market_cap": mcap,
        "enterprise_value": ev,
        "price": price,
        "pe_ttm": _div(mcap, ni_ttm),
        "pe_forward": market.get("forwardPE"),
        "ev_ebitda": _div(ev, ebitda_ttm),
        "ev_sales": _div(ev, rev_ttm),
        "ev_fcf": _div(ev, fcf_ttm),
        "price_to_book": _div(mcap, equity),
        "fcf_yield": _div(fcf_ttm, mcap),
        "earnings_yield": _div(ni_ttm, mcap),
        "peg": market.get("pegRatio"),
        "dividend_yield": market.get("dividendYield"),
    }

    solvency = {
        "total_debt": debt,
        "cash_and_equivalents": cash,
        "net_debt": debt - cash,
        "net_debt_ebitda": _div(debt - cash, ebitda_ttm),
        "debt_to_equity": _div(debt, equity),
        "current_ratio": _div(ca, cl),
        "interest_coverage": None,
        "equity": equity,
    }

    return {
        "ttm": {
            "revenue": rev_ttm,
            "gross_profit": gp_ttm,
            "operating_income": op_ttm,
            "ebitda": ebitda_ttm,
            "net_income": ni_ttm,
            "cfo": cfo_ttm,
            "capex": capex_ttm,
            "fcf": fcf_ttm,
        },
        "profitability": profitability,
        "growth": growth,
        "valuation": valuation,
        "solvency": solvency,
        "rule_of_40": rule_of_40,
    }


def forward(base: dict, estimates: dict) -> dict:
    """Ratios forward aplicando el consenso sobre el precio de hoy.

    estimates espera {'revenue': {'2026': x, '2027': y}, 'eps': {...},
    'ebitda': {...}} en la misma moneda que los estados.
    """
    price = base["valuation"].get("price")
    mcap = base["valuation"].get("market_cap")
    ev = base["valuation"].get("enterprise_value")
    ebitda_margin = base["profitability"].get("ebitda_margin")

    out: dict[str, dict] = {}
    years = sorted(
        set(list(estimates.get("revenue", {})) + list(estimates.get("eps", {})))
    )

    for y in years:
        rev = estimates.get("revenue", {}).get(y)
        eps = estimates.get("eps", {}).get(y)
        ebitda = estimates.get("ebitda", {}).get(y)
        # Si no hay estimate de EBITDA, se proyecta con el margen actual
        if ebitda is None and rev is not None and ebitda_margin:
            ebitda = rev * ebitda_margin

        out[y] = {
            "revenue_est": rev,
            "eps_est": eps,
            "ebitda_est": ebitda,
            "pe": _div(price, eps),
            "ev_sales": _div(ev, rev),
            "ev_ebitda": _div(ev, ebitda),
            "implied_growth_revenue": _div(
                rev - base["ttm"]["revenue"], base["ttm"]["revenue"]
            )
            if rev and base["ttm"]["revenue"]
            else None,
        }

    # PEG forward usando el crecimiento implicito de EPS del consenso
    eps_vals = [(y, v) for y, v in sorted(estimates.get("eps", {}).items()) if v]
    if len(eps_vals) >= 2:
        n = len(eps_vals) - 1
        first, last = eps_vals[0][1], eps_vals[-1][1]
        if first > 0:
            g = (last / first) ** (1 / n) - 1
            pe_next = out[eps_vals[0][0]]["pe"]
            out["_peg_forward"] = _div(pe_next, g * 100) if g > 0 else None
            out["_eps_cagr_est"] = g

    return out
