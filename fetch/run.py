"""Orquestador: junta todas las fuentes en un unico JSON por ticker.

    python -m fetch.run AAPL --peers MSFT,GOOGL --out data/

Cada bloque falla de forma aislada: si una fuente se cae, el JSON igual sale
con el resto y con el error registrado en 'diagnostics'. El campo 'sources'
guarda URL + timestamp de cada dato para poder citarlo en el informe.
"""
from __future__ import annotations

import os
import sys
import json
import logging
import argparse
import traceback
from datetime import datetime, timezone
from pathlib import Path

from . import sec_edgar, stockanalysis, yahoo, damodaran, stats, ratios

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("run")


def _step(diagnostics: dict, name: str, fn):
    try:
        result = fn()
        diagnostics[name] = "ok"
        return result
    except Exception as exc:  # noqa: BLE001
        log.error("%s fallo: %s", name, exc)
        diagnostics[name] = f"error: {exc}"
        log.debug(traceback.format_exc())
        return None


def collect(ticker: str, peers: list[str] | None = None) -> dict:
    ticker = ticker.upper()
    diag: dict[str, str] = {}
    now = datetime.now(timezone.utc).isoformat()

    log.info("== %s ==", ticker)

    cik_name = _step(diag, "sec.cik", lambda: sec_edgar.resolve_cik(ticker))
    cik, legal_name = cik_name if cik_name else (None, None)

    fin = _step(diag, "sec.financials", lambda: sec_edgar.financials(cik)) if cik else None
    earnings = (
        _step(diag, "sec.earnings_8k", lambda: sec_edgar.latest_earnings_material(cik))
        if cik
        else None
    )
    narrative_10k = (
        _step(diag, "sec.10k_narrative", lambda: sec_edgar.latest_10k_narrative(cik))
        if cik
        else None
    )
    ir = (
        _step(diag, "sec.ir_hint", lambda: sec_edgar.investor_relations_hint(cik))
        if cik
        else None
    )

    prof = _step(diag, "yahoo.profile", lambda: yahoo.profile(ticker)) or {}
    prices = _step(diag, "yahoo.prices", lambda: yahoo.price_history(ticker)) or []
    bench = _step(diag, "yahoo.benchmarks", lambda: yahoo.benchmarks()) or {}
    analysts = _step(diag, "yahoo.analysts", lambda: yahoo.analyst_data(ticker)) or {}
    holders = _step(diag, "yahoo.ownership", lambda: yahoo.ownership(ticker)) or {}
    cal = _step(diag, "yahoo.calendar", lambda: yahoo.calendar(ticker)) or {}

    sa = _step(diag, "stockanalysis", lambda: stockanalysis.collect(ticker)) or {}

    market_stats = (
        _step(diag, "stats", lambda: stats.compute(prices, bench)) if prices else None
    )

    industry = prof.get("industry") or (ir or {}).get("sic_description")
    dmd = _step(diag, "damodaran", lambda: damodaran.industry_benchmarks(industry))

    peer_list = peers or []
    peer_data = (
        _step(diag, "yahoo.peers", lambda: yahoo.peer_quotes(peer_list))
        if peer_list
        else []
    )

    computed = (
        _step(diag, "ratios", lambda: ratios.build(fin, prof)) if fin else None
    )

    return {
        "meta": {
            "ticker": ticker,
            "legal_name": legal_name,
            "cik": cik,
            "generated_at": now,
            "kit_version": "1.0",
        },
        "profile": prof,
        "ir": ir,
        "financials_sec": fin,
        "earnings_material": earnings,
        "narrative_10k": narrative_10k,
        "market": {
            "price_history_weekly_5y": prices,
            "benchmarks": bench,
            "calendar": cal,
        },
        "statistics": market_stats,
        "consensus": analysts,
        "ownership": holders,
        "stockanalysis": sa,
        "industry_benchmarks": dmd,
        "peers": {"tickers": peer_list, "quotes": peer_data},
        "computed_ratios": computed,
        "sources": {
            "sec_edgar": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
            if cik
            else None,
            "sec_filings": (earnings or {}).get("filing_url"),
            "yahoo": f"https://finance.yahoo.com/quote/{ticker}",
            "stockanalysis": f"https://stockanalysis.com/stocks/{ticker.lower()}/",
            "damodaran": damodaran.BASE,
            "retrieved_at": now,
        },
        "diagnostics": diag,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Recolecta datos de un ticker US")
    ap.add_argument("ticker")
    ap.add_argument("--peers", default="", help="comparables separados por coma")
    ap.add_argument("--out", default="data", help="directorio de salida")
    args = ap.parse_args()

    peers = [p.strip().upper() for p in args.peers.split(",") if p.strip()]
    payload = collect(args.ticker, peers)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outdir = Path(args.out) / payload["meta"]["ticker"]
    outdir.mkdir(parents=True, exist_ok=True)

    path = outdir / f"{stamp}.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    (outdir / "latest.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )

    failed = [k for k, v in payload["diagnostics"].items() if v != "ok"]
    log.info("escrito %s (%.1f KB)", path, path.stat().st_size / 1024)
    if failed:
        log.warning("bloques con error: %s", ", ".join(failed))

    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write(f"json_path={path}\n")
            fh.write(f"failed_blocks={len(failed)}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
