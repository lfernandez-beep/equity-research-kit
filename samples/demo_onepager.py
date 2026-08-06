"""Demo de render con datos FICTICIOS, solo para validar el diseno.

La empresa no existe. Sirve para ver el layout sin depender del scraper.
Uso: python -m samples.demo_onepager
"""
from __future__ import annotations

from pathlib import Path

from render import charts, render
from render.build_onepager import build

DATA = {
    "meta": {"ticker": "NBSY", "legal_name": "Northbeam Systems, Inc.",
             "generated_at": "2026-08-06T12:00:00+00:00"},
    "profile": {
        "longName": "Northbeam Systems, Inc.",
        "exchange": "NasdaqGS", "sector": "Technology",
        "industry": "Information Technology Services",
        "currentPrice": 184.20, "marketCap": 10_450_000_000,
        "forwardPE": 18.4,
    },
    "computed_ratios": {
        "ttm": {"revenue": 4_820_000_000, "ebitda": 742_000_000},
        "profitability": {"ebitda_margin": 0.154, "net_margin": 0.098, "roe": 0.171,
                          "gross_margin": 0.312, "fcf_margin": 0.121},
        "growth": {"revenue_yoy": 0.084},
        "valuation": {"price": 184.20, "market_cap": 10_450_000_000,
                      "pe_ttm": 22.1, "pe_forward": 18.4, "ev_ebitda": 13.2,
                      "fcf_yield": 0.056},
        "solvency": {"net_debt_ebitda": 0.4},
    },
    "statistics": {"vs": {"SPY": {"beta_raw": 1.24, "r_squared": 0.48}}},
}

NARRATIVE = {
    "eyebrow": "Equity research · Nota de inicio de cobertura",
    "tagline": "De proveedor de servicios de IT a socio de ingeniería de plataformas de IA",
    "rating": "COMPRAR",
    "rating_sub": "recomendación · horizonte 12m",
    "pill": "Riesgo medio",
    "pill_class": "warn",
    "target": {
        "bear": 142.00, "base": 226.00, "bull": 278.00,
        "caption": "Objetivo base por DCF (70%) y múltiplos (30%); escenarios por tasa de conversión del backlog de IA.",
        "ref": "Ref.: modelo propio sobre estados 10-Q y guidance del 2T26.",
    },
    "thesis": {
        "headline": "El mercado descuenta un negocio de servicios cíclico; los datos ya muestran una mezcla distinta",
        "blocks": [
            {
                "text": "La acción cotiza a 13,2x EV/EBITDA, un descuento de 28% contra la mediana de comparables, "
                        "sobre la premisa de que el negocio sigue siendo staffing de IT sensible al ciclo. La mezcla "
                        "de ingresos cuenta otra historia: los mandatos de ingeniería de plataformas de IA pasaron de "
                        "9% a 31% de la facturación en seis trimestres, con márgenes brutos entre 8 y 11 puntos por "
                        "encima del negocio tradicional.",
                "figure": {
                    "title": "Mezcla de ingresos: el negocio de mayor margen ya es un tercio del total",
                    "svg": charts.bars_grouped(
                        ["2T25", "3T25", "4T25", "1T26", "2T26"],
                        {"Servicios tradicionales": [91, 87, 80, 74, 69],
                         "Ingeniería de IA": [9, 13, 20, 26, 31]},
                    ),
                    "caption": "Participación en la facturación trimestral, en porcentaje.",
                    "ref": "Ref.: 10-Q 2T26, desagregación de ingresos por línea de servicio.",
                },
            },
            {
                "text": "La reversión de márgenes acompaña la mezcla. El margen EBITDA tocó piso en 11,2% en el 4T24, "
                        "cuando la compañía absorbió el costo de recontratar talento senior, y se recuperó a 15,4% en "
                        "los últimos doce meses. La generación de caja siguió el mismo camino: el FCF yield de 5,6% es "
                        "el más alto desde la salida a bolsa.",
                "figure": {
                    "title": "Margen EBITDA trimestral: piso en el 4T24 y recuperación sostenida",
                    "svg": charts.waterfall_margin(
                        ["4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26"],
                        [0.112, 0.121, 0.133, 0.141, 0.148, 0.151, 0.158],
                    ),
                    "caption": "Margen EBITDA ajustado por trimestre.",
                    "ref": "Ref.: cálculo propio sobre 10-Q; EBITDA = resultado operativo + D&A.",
                },
            },
            {
                "text": "El apalancamiento no es una restricción para financiar la transición: la deuda neta equivale a "
                        "0,4x EBITDA y la compañía cerró el trimestre con caja por encima de la deuda de corto plazo. "
                        "El riesgo no está en el balance sino en la ejecución comercial — el backlog de IA todavía "
                        "depende de tres clientes que concentran 41% de esos mandatos.",
                "figure": {
                    "title": "Escala de la oportunidad y punto de partida de balance",
                    "stats": [
                        {"value": "31%", "label": "Ingresos de ingeniería de IA", "sub": "vs. 9% seis trimestres atrás"},
                        {"value": "+46 pb", "label": "Margen bruto incremental", "sub": "mandatos de IA vs. tradicional"},
                        {"value": "0,4x", "label": "Deuda neta / EBITDA", "tone": "navy", "sub": "LTM 2T26"},
                    ],
                    "svg": charts.gauge(0.4, vmax=3.0, bands=(1.0, 2.0)),
                    "caption": "Deuda neta / EBITDA, LTM 2T26 — margen de maniobra para financiar el plan.",
                    "ref": "Ref.: balance al 30/06/2026 y cálculo propio.",
                },
            },
        ],
    },
    "bull": [
        "La mezcla hacia ingeniería de IA sube el margen bruto estructural, no es un efecto de precio puntual",
        "Balance con deuda neta de 0,4x EBITDA y FCF yield de 5,6%, el más alto desde la IPO",
        "Cotiza con 28% de descuento en EV/EBITDA contra la mediana de comparables directos",
    ],
    "bear": [
        "Tres clientes concentran 41% del backlog de mandatos de IA",
        "El guidance de ingresos 2026 asume una tasa de conversión del pipeline que la compañía no alcanzó en 2025",
        "Exposición cambiaria: 38% de la base de costos está en monedas de Europa del Este",
    ],
    "guidance": {
        "rows": [
            {"k": "Ingresos 2026", "v": "USD 5.050M – 5.150M (+5% a +7%)"},
            {"k": "Margen EBITDA ajustado 2026", "v": "15,5% – 16,5%"},
            {"k": "EPS diluido ajustado 2026", "v": "USD 10,20 – 10,60"},
            {"k": "Tasa impositiva efectiva", "v": "≈ 23%"},
            {"k": "Capex", "v": "≈ 1,4% de los ingresos"},
        ],
        "source": "Fuente: 8-K del 31/07/2026, Exhibit 99.1 (press release de resultados del 2T26) presentado ante la SEC.",
    },
    "peers": {
        "title": "Posicionamiento contra comparables",
        "intro": "Contra el grupo de comparables directos, la compañía combina el segundo mayor crecimiento "
                 "con el múltiplo más bajo del grupo — la brecha que sostiene la tesis.",
        "columns": [
            {"name": "NBSY", "sub": "Northbeam"},
            {"name": "Peer A", "sub": "comparable"},
            {"name": "Peer B", "sub": "comparable"},
            {"name": "Mediana", "sub": "grupo"},
        ],
        "rows": [
            {"label": "EV / EBITDA", "cells": ["13,2x", "18,7x", "21,4x", "18,4x"]},
            {"label": "P/E forward", "cells": ["18,4x", "24,1x", "27,8x", "24,1x"]},
            {"label": "Margen EBITDA", "cells": ["15,4%", "17,2%", "19,1%", "17,2%"]},
            {"label": "Crecimiento de ingresos", "cells": ["8,4%", "6,1%", "11,2%", "6,9%"]},
            {"label": "FCF yield", "cells": ["5,6%", "3,8%", "2,9%", "3,6%"],
             "cls": "highlight"},
        ],
        "callouts": [
            {"big": "−28%", "text": "de descuento en EV/EBITDA contra la mediana del grupo, con crecimiento por encima de la mediana"},
            {"big": "+200 pb", "text": "de FCF yield contra el comparable más cercano, a estructura de capital similar"},
        ],
    },
    "disclaimer": "Documento de análisis elaborado con información pública: filings ante la SEC (10-K, 10-Q y 8-K), "
                  "datos de mercado de Yahoo Finance y stockanalysis.com, y datasets de industria de NYU Stern. Las "
                  "proyecciones son estimaciones propias sujetas a error y no constituyen garantía de resultados "
                  "futuros. Los múltiplos de comparables son niveles de mercado a la fecha indicada y varían a diario. "
                  "Este documento no constituye asesoramiento financiero, legal ni impositivo, ni una oferta o "
                  "invitación a comprar o vender valor alguno. Toda decisión de inversión debe adoptarse con análisis "
                  "propio y, de corresponder, asesoramiento profesional matriculado.",
    "signoff": {"name": "Mesa de Research", "line": "Northbeam Systems (NBSY) · Nota de inicio de cobertura"},
}


def main() -> None:
    payload = build(DATA, NARRATIVE)
    out = Path("outputs/NBSY_onepager_DEMO.pdf")
    render.render_onepager(payload, out)
    print("escrito:", out)


if __name__ == "__main__":
    main()
