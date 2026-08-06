"""SEC EDGAR: estados contables (XBRL) y material oficial del ultimo earnings.

Fuente primaria y oficial. Sin API key. Dos cosas salen de aca:

1. Estados contables normalizados desde la API XBRL companyfacts.
2. El material del ultimo earnings: el 8-K con su Exhibit 99.1/99.2, que es el
   press release que la empresa presenta ante la SEC y donde vive el guidance.
   Es la fuente oficial, no un resumen de terceros.
"""
from __future__ import annotations

import re
import logging
from datetime import datetime

from .http import get, get_json

log = logging.getLogger(__name__)

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SUBS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{doc}"

# Cada linea del estado contable puede venir con distintos tags XBRL segun la
# empresa. Se prueban en orden y gana el primero que exista.
CONCEPTS: dict[str, list[str]] = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ],
    "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    "shares_diluted": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "rnd": ["ResearchAndDevelopmentExpense"],
    "sgna": ["SellingGeneralAndAdministrativeExpense"],
    "dep_amort": [
        "DepreciationDepletionAndAmortization",
        "DepreciationAmortizationAndAccretionNet",
    ],
    "total_assets": ["Assets"],
    "total_liabilities": ["Liabilities"],
    "equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ],
    "short_term_investments": ["ShortTermInvestments", "MarketableSecuritiesCurrent"],
    "current_assets": ["AssetsCurrent"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "inventory": ["InventoryNet"],
    "receivables": ["AccountsReceivableNetCurrent"],
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "short_term_debt": ["LongTermDebtCurrent", "DebtCurrent"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "dividends_paid": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"],
    "sbc": ["ShareBasedCompensation"],
}


def resolve_cik(ticker: str) -> tuple[int, str]:
    """Devuelve (cik, nombre) para un ticker US."""
    data = get_json(TICKERS_URL, sec=True)
    tk = ticker.upper()
    for row in data.values():
        if row["ticker"].upper() == tk:
            return int(row["cik_str"]), row["title"]
    raise ValueError(f"ticker {ticker} no encontrado en EDGAR")


def _pick_series(facts: dict, tags: list[str]) -> list[dict]:
    """Extrae la serie del primer tag disponible, deduplicada por periodo."""
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for tag in tags:
        node = gaap.get(tag)
        if not node:
            continue
        units = node.get("units", {})
        key = next((k for k in ("USD", "USD/shares", "shares") if k in units), None)
        if not key:
            continue

        rows: dict[tuple, dict] = {}
        for f in units[key]:
            if "start" in f and "end" in f:  # flujo (P&L, cash flow)
                period = (f["start"], f["end"])
            else:  # stock (balance)
                period = (None, f["end"])
            # Se queda con la version mas reciente de cada periodo (restatements)
            prev = rows.get(period)
            if prev is None or f.get("filed", "") >= prev.get("filed", ""):
                rows[period] = f

        out = []
        for (start, end), f in rows.items():
            out.append(
                {
                    "start": start,
                    "end": end,
                    "val": f["val"],
                    "fy": f.get("fy"),
                    "fp": f.get("fp"),
                    "form": f.get("form"),
                    "frame": f.get("frame"),
                    "tag": tag,
                }
            )
        out.sort(key=lambda r: r["end"])
        return out
    return []


def _is_annual(row: dict) -> bool:
    if row["start"] is None:
        return row.get("form") == "10-K"
    days = (datetime.fromisoformat(row["end"]) - datetime.fromisoformat(row["start"])).days
    return 340 <= days <= 400


def _is_quarterly(row: dict) -> bool:
    if row["start"] is None:
        return True
    days = (datetime.fromisoformat(row["end"]) - datetime.fromisoformat(row["start"])).days
    return 80 <= days <= 100


def financials(cik: int, *, years: int = 6, quarters: int = 12) -> dict:
    """Estados contables anuales y trimestrales normalizados."""
    facts = get_json(FACTS_URL.format(cik=cik), sec=True)

    annual: dict[str, list[dict]] = {}
    quarterly: dict[str, list[dict]] = {}
    for name, tags in CONCEPTS.items():
        series = _pick_series(facts, tags)
        if not series:
            continue
        annual[name] = [r for r in series if _is_annual(r)][-years:]
        quarterly[name] = [r for r in series if _is_quarterly(r)][-quarters:]

    return {
        "entity": facts.get("entityName"),
        "annual": annual,
        "quarterly": quarterly,
        "source": FACTS_URL.format(cik=cik),
    }


def latest_earnings_material(cik: int) -> dict:
    """Ultimo 8-K de resultados con sus exhibits 99.x (press release + guidance).

    Devuelve el texto plano del exhibit para que el analisis lea el guidance
    de la fuente oficial y no de un resumen de terceros.
    """
    subs = get_json(SUBS_URL.format(cik=cik), sec=True)
    recent = subs["filings"]["recent"]

    idx = None
    for i, form in enumerate(recent["form"]):
        # Item 2.02 = Results of Operations and Financial Condition
        if form == "8-K" and "2.02" in (recent.get("items") or [""] * len(recent["form"]))[i]:
            idx = i
            break
    if idx is None:
        return {"found": False}

    acc = recent["accessionNumber"][idx]
    acc_nodash = acc.replace("-", "")
    filing_date = recent["filingDate"][idx]

    # El index JSON del filing lista todos los documentos adjuntos
    index_url = (
        f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/index.json"
    )
    index = get_json(index_url, sec=True)
    items = index.get("directory", {}).get("item", [])

    exhibits = []
    for it in items:
        name = it.get("name", "")
        if re.search(r"ex-?99", name, re.I) and name.lower().endswith((".htm", ".html", ".txt")):
            url = ARCHIVE.format(cik=cik, acc_nodash=acc_nodash, doc=name)
            try:
                html = get(url, sec=True).text
            except Exception as exc:  # noqa: BLE001
                log.warning("no se pudo bajar exhibit %s: %s", name, exc)
                continue
            exhibits.append({"name": name, "url": url, "text": _strip_html(html)})

    return {
        "found": bool(exhibits),
        "accession": acc,
        "filing_date": filing_date,
        "filing_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/",
        "exhibits": exhibits,
    }


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?i)<br\s*/?>|</p>|</tr>|</div>", "\n", text)
    text = re.sub(r"(?i)</t[dh]>", "\t", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&#8217;", "'")
        .replace("&#8212;", "-")
        .replace("&rsquo;", "'")
        .replace("&mdash;", "-")
    )
    text = re.sub(r"[ \t]{2,}", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def latest_10k_narrative(cik: int) -> dict:
    """Item 1 (Negocio), Item 1A (Factores de riesgo) e Item 7 (MD&A) del 10-K.

    Estas tres secciones son texto redactado por la propia empresa dentro de
    un filing oficial: no son un resumen de un tercero. Es la fuente mas rica
    que existe, gratis, para nutrir la descripcion del negocio y los riesgos
    sin depender de articulos de terceros.
    """
    subs = get_json(SUBS_URL.format(cik=cik), sec=True)
    recent = subs["filings"]["recent"]

    idx = next((i for i, f in enumerate(recent["form"]) if f == "10-K"), None)
    if idx is None:
        return {"found": False}

    acc = recent["accessionNumber"][idx]
    acc_nodash = acc.replace("-", "")
    filing_date = recent["filingDate"][idx]

    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/index.json"
    index = get_json(index_url, sec=True)
    items = index.get("directory", {}).get("item", [])

    # El documento primario del 10-K es el .htm mas grande que no sea un exhibit
    candidates = [
        it for it in items
        if it.get("name", "").lower().endswith(".htm")
        and "ex" not in it.get("name", "").lower()[:4]
    ]
    if not candidates:
        return {"found": False}
    main_doc = max(candidates, key=lambda it: int(it.get("size", 0)))

    url = ARCHIVE.format(cik=cik, acc_nodash=acc_nodash, doc=main_doc["name"])
    text = _strip_html(get(url, sec=True).text)

    return {
        "found": True,
        "filing_date": filing_date,
        "url": url,
        "business": _extract_item(text, "1", "1A"),
        "risk_factors": _extract_item(text, "1A", "1B"),
        "mdna": _extract_item(text, "7", "7A"),
    }


def _extract_item(text: str, item: str, next_item: str) -> str | None:
    """Recorta el texto entre 'Item {item}.' y 'Item {next_item}.'.

    Los 10-K suelen repetir el indice al principio, asi que se busca la
    SEGUNDA ocurrencia de cada marcador (la que abre la seccion real).
    """
    pat_start = re.compile(rf"Item\s+{item}\.?\s", re.I)
    pat_end = re.compile(rf"Item\s+{next_item}\.?\s", re.I)

    starts = [m.start() for m in pat_start.finditer(text)]
    ends = [m.start() for m in pat_end.finditer(text)]
    if len(starts) < 2 or len(ends) < 2:
        return None

    start = starts[1]
    end = next((e for e in ends if e > start), None)
    if end is None:
        return None

    chunk = text[start:end].strip()
    # Recorte defensivo: estas secciones pueden ser enormes (MD&A > 20k palabras)
    return chunk[:20000]


def investor_relations_hint(cik: int) -> dict:
    """Datos de contacto/website del emisor para ubicar el IR site y el call."""
    subs = get_json(SUBS_URL.format(cik=cik), sec=True)
    return {
        "name": subs.get("name"),
        "sic_description": subs.get("sicDescription"),
        "website": subs.get("website"),
        "investor_website": subs.get("investorWebsite"),
        "exchanges": subs.get("exchanges"),
        "fiscal_year_end": subs.get("fiscalYearEnd"),
    }
