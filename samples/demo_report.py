"""Demo del informe completo, con la profundidad real que va a tener un ticker

Empresa FICTICIA (Northbeam Systems / NBSY). Sirve para validar que el
sistema de bloques (texto, tabla, figura, stats, callout) sostiene un
informe largo sin depender de una unica estructura fija por seccion.

Uso: python -m samples.demo_report
"""
from __future__ import annotations

from pathlib import Path

from render import charts, render
from render.build_onepager import money, mult, pct, usd

TICKER = "NBSY"
PRICE = 184.20
TARGET = 226.00
MCAP = 10_450_000_000

HEADER_KPIS = [
    {"label": "Precio", "value": money(PRICE), "tone": ""},
    {"label": "Precio objetivo", "value": money(TARGET), "tone": ""},
    {"label": "Upside", "value": pct(TARGET / PRICE - 1), "tone": "up"},
    {"label": "Market cap", "value": usd(MCAP), "tone": ""},
]

# ---------------------------------------------------------------------------
# Series fictícias, consistentes entre secciones
# ---------------------------------------------------------------------------
YEARS = ["2021", "2022", "2023", "2024", "2025", "LTM 2T26"]
REVENUE = [3210, 3640, 4120, 4310, 4445, 4820]
GROSS_PROFIT = [905, 1030, 1198, 1250, 1329, 1504]
EBITDA = [498, 545, 560, 483, 641, 742]
EBIT = [389, 421, 429, 341, 512, 606]
NET_INCOME = [261, 288, 274, 179, 349, 411]
CFO = [372, 401, 447, 356, 561, 636]
CAPEX = [61, 68, 71, 63, 88, 103]
FCF = [c - x for c, x in zip(CFO, CAPEX)]

Q_LABELS = ["4T24", "1T25", "2T25", "3T25", "4T25", "1T26", "2T26"]
Q_MARGIN = [0.112, 0.121, 0.133, 0.141, 0.148, 0.151, 0.158]
Q_MIX_TRAD = [91, 87, 80, 74, 69]
Q_MIX_IA = [9, 13, 20, 26, 31]
Q_MIX_LABELS = ["2T25", "3T25", "4T25", "1T26", "2T26"]

PEERS = ["NBSY", "Peer A", "Peer B", "Peer C", "Peer D", "Mediana"]
PEER_EV_EBITDA = [13.2, 18.7, 21.4, 16.1, 19.9, 18.7]
PEER_PE_FWD = [18.4, 24.1, 27.8, 20.3, 25.6, 24.1]
PEER_GROWTH = [8.4, 6.1, 11.2, 4.3, 7.0, 6.6]
PEER_EBITDA_MARGIN = [15.4, 17.2, 19.1, 14.8, 18.0, 17.2]
PEER_FCF_YIELD = [5.6, 3.8, 2.9, 4.4, 3.1, 3.5]
PEER_ROIC = [14.1, 12.8, 16.4, 10.2, 13.9, 13.4]
PEER_ND_EBITDA = [0.4, 1.6, 2.1, 0.8, 1.9, 1.6]


def _loc(s: str) -> str:
    return s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def _cells(vals, fmt="{:,.0f}"):
    return [_loc(fmt.format(v)) for v in vals]


# ---------------------------------------------------------------------------
# Capítulo 1 · Resumen ejecutivo
# ---------------------------------------------------------------------------
sec_resumen = {
    "eyebrow": "Resumen ejecutivo",
    "title": "Una transición de mezcla que el múltiplo todavía no reconoce",
    "new_chapter": False,
    "blocks": [
        {"type": "text", "text":
            "Iniciamos cobertura de Northbeam Systems (NBSY) con recomendación de COMPRAR y un "
            "precio objetivo de USD 226,00 a doce meses, un retorno potencial de 22,7% sobre el "
            "cierre de USD 184,20 del 5 de agosto de 2026. El objetivo surge de ponderar un modelo "
            "de flujos de caja descontados a la firma (70% de peso) con una valuación relativa por "
            "múltiplos de comparables (30% de peso)."},
        {"type": "text", "text":
            "La tesis descansa sobre tres pilares que desarrollamos en detalle en este informe: "
            "(1) una migración estructural de la mezcla de ingresos hacia mandatos de ingeniería de "
            "plataformas de IA, con márgenes brutos entre 8 y 11 puntos por encima del negocio "
            "tradicional de staffing de IT; (2) una reversión de márgenes ya visible y sostenida "
            "durante seis trimestres consecutivos; y (3) una estructura de capital con margen para "
            "financiar la transición sin recurrir a dilución ni a mercados de deuda."},
        {"type": "stats", "cards": [
            {"value": "31%", "label": "Ingresos de ingeniería de IA", "sub": "vs. 9% seis trimestres atrás"},
            {"value": "15,8%", "label": "Margen EBITDA, 2T26", "sub": "vs. 11,2% en el piso del 4T24", "tone": "navy"},
            {"value": "0,4x", "label": "Deuda neta / EBITDA", "sub": "el más bajo del grupo de comparables"},
        ]},
        {"type": "figure", "title": "Rango de valuación y precio objetivo",
         "svg": charts.target_range(low=142.0, base=226.0, high=278.0, current=PRICE, width=7.4, height=1.5),
         "caption": "Objetivo base por DCF (70%) y múltiplos (30%); escenarios por tasa de conversión del backlog de IA.",
         "ref": "Ref.: modelo propio sobre estados 10-Q y guidance del 2T26."},
        {"type": "bull_bear",
         "bull": [
             "La mezcla hacia ingeniería de IA sube el margen bruto estructural, no es un efecto de precio puntual",
             "Balance con deuda neta de 0,4x EBITDA y FCF yield de 5,6%, el más alto desde la salida a bolsa",
             "Cotiza con 28% de descuento en EV/EBITDA contra la mediana de comparables directos",
             "Retención de clientes del segmento de IA por encima de 95% en los últimos cuatro trimestres",
         ],
         "bear": [
             "Tres clientes concentran 41% del backlog de mandatos de IA",
             "El guidance de ingresos 2026 asume una tasa de conversión del pipeline que la compañía no alcanzó en 2025",
             "Exposición cambiaria: 38% de la base de costos está en monedas de Europa del Este",
             "La reversión de márgenes coincide con un ciclo de gasto en IA de los clientes que podría normalizarse",
         ]},
    ],
    "sidebar": [
        {"title": "Cifras clave", "kv": [
            {"k": "Ingresos LTM", "v": usd(4_820_000_000)},
            {"k": "EBITDA LTM", "v": usd(742_000_000)},
            {"k": "Margen EBITDA", "v": "15,4%"},
            {"k": "ROE", "v": "17,1%"},
            {"k": "EV/EBITDA", "v": "13,2x"},
            {"k": "FCF yield", "v": "5,6%"},
        ], "source": "Fuente: SEC EDGAR y cálculo propio."},
        {"title": "Mezcla de ingresos",
         "svg": charts.donut(["Ingeniería de IA", "Servicios tradicionales"], [31, 69], center="31%",
                              width=2.0, height=2.0),
         "source": "Fuente: 10-Q 2T26."},
        {"title": "Estadística de mercado", "kv": [
            {"k": "Beta (5a, sem.)", "v": "1,24"},
            {"k": "R² vs. SPY", "v": "0,48"},
            {"k": "Vol. anualizada", "v": "34,2%"},
            {"k": "Máx. drawdown (5a)", "v": "−52,1%"},
        ], "source": "Fuente: regresión propia sobre precios semanales."},
    ],
}

# ---------------------------------------------------------------------------
# Capítulo 2 · Descripción del negocio
# ---------------------------------------------------------------------------
sec_negocio = {
    "eyebrow": "Descripción del negocio",
    "title": "De proveedor de staffing de IT a socio de ingeniería de plataformas de IA",
    "new_chapter": True,
    "blocks": [
        {"type": "subhead", "text": "Qué hace la compañía"},
        {"type": "text", "text":
            "Northbeam Systems presta servicios de tecnología a empresas medianas y grandes de "
            "Norteamérica y Europa, organizados en dos segmentos: Servicios Tradicionales de IT "
            "(dotación de personal técnico, soporte de infraestructura y modernización de sistemas "
            "heredados) e Ingeniería de Plataformas de IA (diseño e implementación de pipelines de "
            "datos, MLOps y integración de modelos de lenguaje en productos de los clientes). El "
            "segundo segmento, inexistente como línea reportable hasta 2024, ya explica 31% de la "
            "facturación."},
        {"type": "subhead", "text": "Historia y hitos"},
        {"type": "text", "text":
            "La compañía fue fundada en 2009 como una consultora de staffing de IT enfocada en el "
            "sector financiero, y completó su oferta pública inicial en 2018. Entre 2019 y 2023 el "
            "negocio operó como un proveedor de mano de obra técnica de márgenes moderados, con "
            "crecimiento de un dígito y alta sensibilidad al ciclo de gasto en tecnología de sus "
            "clientes. El punto de inflexión llegó a mediados de 2024, cuando la compañía formó una "
            "práctica dedicada de ingeniería de IA a partir de la adquisición de un equipo de "
            "veinticinco ingenieros de una startup de MLOps, y reorientó la venta cruzada hacia "
            "clientes existentes del segmento financiero y de salud."},
        {"type": "text", "text":
            "Desde entonces, la compañía firmó contratos plurianuales con cuatro de sus veinte "
            "clientes más grandes para migrar sus stacks de datos a arquitecturas compatibles con "
            "modelos de lenguaje, lo que explica gran parte de la aceleración de ingresos de "
            "ingeniería de IA que se detalla en la sección de segmentos."},
        {"type": "table", "title": "Ingresos por segmento",
         "columns": [{"name": q} for q in Q_MIX_LABELS],
         "rows": [
             {"label": "Servicios tradicionales (%)", "cells": [f"{v}%" for v in Q_MIX_TRAD]},
             {"label": "Ingeniería de IA (%)", "cells": [f"{v}%" for v in Q_MIX_IA], "cls": "highlight"},
         ],
         "note": "Fuente: desagregación de ingresos por línea de servicio, 10-Q 2T26."},
        {"type": "figure_row", "figures": [
            {"title": "Mezcla de ingresos por trimestre",
             "svg": charts.bars_grouped(Q_MIX_LABELS, {"Tradicional": Q_MIX_TRAD, "Ingeniería de IA": Q_MIX_IA},
                                        width=3.6, height=2.3),
             "caption": "Participación en la facturación trimestral, en porcentaje."},
            {"title": "Ingresos por geografía, LTM 2T26",
             "svg": charts.donut(["Norteamérica", "Europa Occidental", "Europa del Este"], [61, 23, 16],
                                 width=2.4, height=2.4),
             "caption": "Fuente: 10-K, nota de segmentos geográficos."},
        ]},
        {"type": "subhead", "text": "Modelo de ingresos y clientes"},
        {"type": "text", "text":
            "El negocio tradicional factura mayormente por tiempo y materiales, con contratos "
            "renovables anualmente y baja visibilidad más allá de doce meses. El segmento de "
            "ingeniería de IA, en cambio, opera con contratos de alcance fijo de doce a veinticuatro "
            "meses y una porción creciente de fees de retención mensual, lo que empieza a darle a la "
            "compañía una visibilidad de ingresos que no tenía en su negocio original. Los veinte "
            "clientes más grandes explican 54% de la facturación total y 68% del segmento de IA, la "
            "concentración que señalamos como riesgo a vigilar en el resumen ejecutivo."},
    ],
    "sidebar": [
        {"title": "Perfil", "kv": [
            {"k": "Fundación", "v": "2009"},
            {"k": "IPO", "v": "2018 · NasdaqGS"},
            {"k": "Sede", "v": "Austin, Texas"},
            {"k": "Empleados", "v": "≈ 6.400"},
            {"k": "Sector", "v": "Technology"},
            {"k": "Industria", "v": "IT Services"},
        ], "source": "Fuente: 10-K, perfil de la compañía."},
        {"title": "Segmentos", "kv": [
            {"k": "Servicios tradicionales", "v": "69%"},
            {"k": "Ingeniería de IA", "v": "31%"},
        ], "source": "Fuente: 10-Q 2T26."},
    ],
}

# ---------------------------------------------------------------------------
# Capítulo 3 · Posicionamiento competitivo (continúa el mismo capítulo, sin salto)
# ---------------------------------------------------------------------------
sec_competencia = {
    "eyebrow": "Posicionamiento competitivo",
    "title": "El descuento del mercado asume una categoría que la compañía ya dejó atrás",
    "new_chapter": False,
    "blocks": [
        {"type": "text", "text":
            "Northbeam compite en dos categorías con dinámicas distintas. En staffing tradicional de "
            "IT enfrenta a proveedores de escala global con estructuras de costos más eficientes, "
            "donde compite principalmente por relación y conocimiento de dominio en clientes "
            "financieros. En ingeniería de plataformas de IA, el grupo de comparables directos es "
            "mucho más chico y de mayor múltiplo, lo que es precisamente la base de la tesis: el "
            "mercado sigue valuando a la compañía como si fuera enteramente del primer grupo."},
        {"type": "text", "text":
            "Contra el grupo de comparables directos, la compañía combina el segundo mayor "
            "crecimiento de ingresos con el múltiplo de EV/EBITDA más bajo del grupo — la brecha que "
            "sostiene la tesis de valuación que desarrollamos en la sección correspondiente."},
        {"type": "table", "title": "Posicionamiento contra comparables",
         "columns": [{"name": p} for p in PEERS],
         "rows": [
             {"label": "EV / EBITDA", "cells": [_loc(f"{v:.1f}") + "x" for v in PEER_EV_EBITDA]},
             {"label": "P/E forward", "cells": [_loc(f"{v:.1f}") + "x" for v in PEER_PE_FWD]},
             {"label": "Margen EBITDA", "cells": [_loc(f"{v:.1f}") + "%" for v in PEER_EBITDA_MARGIN]},
             {"label": "Crecimiento de ingresos", "cells": [_loc(f"{v:.1f}") + "%" for v in PEER_GROWTH]},
             {"label": "FCF yield", "cells": [_loc(f"{v:.1f}") + "%" for v in PEER_FCF_YIELD], "cls": "highlight"},
         ],
         "note": "Fuente: stockanalysis.com y Yahoo Finance, precios de cierre del 5/8/2026."},
        {"type": "callout", "big": "−28%", "text": "de descuento en EV/EBITDA contra la mediana del grupo, con crecimiento por encima de la mediana"},
        {"type": "text", "text":
            "El foso competitivo del segmento de IA no está todavía en la propiedad intelectual —la "
            "compañía no licencia software propio— sino en el conocimiento regulatorio de los "
            "clientes financieros y de salud, donde la implementación de modelos de lenguaje exige "
            "cumplimiento específico que los comparables de propósito general no dominan con la misma "
            "profundidad. Es un foso más frágil que uno de producto, y por eso lo tratamos como "
            "ventaja a vigilar más que como activo permanente."},
    ],
    "sidebar": [
        {"title": "Crecimiento vs. múltiplo",
         "svg": charts.peers_scatter(
             [{"ticker": t, "revenue_growth": g / 100, "ev_ebitda": e}
              for t, g, e in zip(PEERS[:-1], PEER_GROWTH[:-1], PEER_EV_EBITDA[:-1])],
             highlight="NBSY", width=2.5, height=2.2),
         "source": "Fuente: cálculo propio."},
    ],
}

# ---------------------------------------------------------------------------
# Capítulo 4 · Análisis financiero
# ---------------------------------------------------------------------------
sec_financiero = {
    "eyebrow": "Análisis financiero",
    "title": "Márgenes, caja y estructura de capital",
    "new_chapter": True,
    "blocks": [
        {"type": "subhead", "text": "Evolución de ingresos y rentabilidad"},
        {"type": "text", "text":
            "Los ingresos crecieron a una tasa anual compuesta de 8,5% entre 2021 y el último año "
            "móvil, con una desaceleración visible en 2023-2024 cuando el negocio tradicional sintió "
            "el ajuste de presupuestos de IT de sus clientes, y una reaceleración a partir de 2025 de "
            "la mano del segmento de IA. El margen EBITDA sigue el mismo patrón: tocó piso en 11,2% "
            "en el 4T24, cuando la compañía absorbió el costo de recontratar talento senior tras una "
            "ola de renuncias, y se recuperó de forma ininterrumpida hasta 15,8% en el 2T26."},
        {"type": "text", "text":
            "La recuperación de margen no se explica por recortes de plantilla: la dotación total "
            "creció 6% interanual en el mismo período, lo que refuerza que el motor es la mezcla de "
            "ingresos y no un ajuste de costos puntual."},
        {"type": "table", "title": "Estado de resultados resumido (USD millones)",
         "columns": [{"name": y} for y in YEARS],
         "rows": [
             {"label": "Ingresos", "cells": _cells(REVENUE)},
             {"label": "Utilidad bruta", "cells": _cells(GROSS_PROFIT)},
             {"label": "Margen bruto", "cells": [_loc(f"{g/r*100:.1f}") + "%" for g, r in zip(GROSS_PROFIT, REVENUE)]},
             {"label": "EBITDA", "cells": _cells(EBITDA)},
             {"label": "Margen EBITDA", "cells": [_loc(f"{e/r*100:.1f}") + "%" for e, r in zip(EBITDA, REVENUE)], "cls": "highlight"},
             {"label": "Resultado operativo (EBIT)", "cells": _cells(EBIT)},
             {"label": "Resultado neto", "cells": _cells(NET_INCOME)},
         ],
         "note": "Fuente: cálculo propio sobre 10-K y 10-Q presentados ante la SEC."},
        {"type": "figure_row", "figures": [
            {"title": "Ingresos anuales (USD M)",
             "svg": charts.bars_series(YEARS, REVENUE, fmt="{:,.0f}", width=3.6, height=2.3),
             "caption": "Fuente: SEC EDGAR."},
            {"title": "Margen EBITDA trimestral",
             "svg": charts.waterfall_margin(Q_LABELS, Q_MARGIN, width=3.6, height=2.3),
             "caption": "Piso en el 4T24, recuperación sostenida desde entonces."},
        ]},
        {"type": "subhead", "text": "Balance y estructura de capital"},
        {"type": "text", "text":
            "La deuda neta equivale a 0,4x EBITDA al cierre del segundo trimestre de 2026, tras una "
            "reducción sostenida desde 1,2x en 2024, cuando la compañía financió la adquisición del "
            "equipo de MLOps con deuda de corto plazo que ya canceló en su totalidad. El patrimonio "
            "neto no muestra dilución relevante: la compañía no emitió acciones nuevas desde 2022, y "
            "el aumento de capital propio se explica enteramente por utilidades retenidas."},
        {"type": "table", "title": "Balance resumido (USD millones)",
         "columns": [{"name": y} for y in YEARS[2:]],
         "rows": [
             {"label": "Caja y equivalentes", "cells": ["312", "298", "356", "441"]},
             {"label": "Activo corriente", "cells": ["890", "902", "988", "1.102"]},
             {"label": "Activo total", "cells": ["2.140", "2.205", "2.410", "2.680"]},
             {"label": "Deuda total", "cells": ["672", "580", "440", "300"]},
             {"label": "Pasivo corriente", "cells": ["510", "534", "561", "612"]},
             {"label": "Patrimonio neto", "cells": ["1.240", "1.389", "1.680", "2.010"], "cls": "highlight"},
         ],
         "note": "Fuente: cálculo propio sobre 10-K y 10-Q."},
        {"type": "figure", "title": "Apalancamiento: deuda neta / EBITDA",
         "svg": charts.gauge(0.4, vmax=3.0, bands=(1.0, 2.0), width=6.4, height=1.0),
         "caption": "Deuda neta / EBITDA, LTM 2T26 — margen de maniobra para financiar el plan.",
         "ref": "Ref.: balance al 30/06/2026 y cálculo propio."},
        {"type": "subhead", "text": "Generación de caja y capex"},
        {"type": "text", "text":
            "La conversión de EBITDA a flujo operativo se mantuvo por encima de 90% en cinco de los "
            "últimos seis años, y el flujo libre de caja alcanzó USD 533 millones en el último año "
            "móvil, un FCF yield de 5,6% sobre el market cap actual — el más alto desde la salida a "
            "bolsa. El capex se mantiene estructuralmente bajo (2,1% de los ingresos en el LTM) porque "
            "el negocio no requiere activos fijos intensivos; el crecimiento se financia con capital "
            "humano, no con planta."},
        {"type": "figure_row", "figures": [
            {"title": "Flujo operativo vs. capex (USD M)",
             "svg": charts.bars_grouped(YEARS, {"CFO": CFO, "Capex": CAPEX}, fmt="{:,.0f}", width=3.6, height=2.3),
             "caption": "Fuente: estado de flujo de efectivo, 10-K."},
            {"title": "Flujo libre de caja (USD M)",
             "svg": charts.bars_series(YEARS, FCF, fmt="{:,.0f}", width=3.6, height=2.3),
             "caption": "FCF = flujo operativo − capex."},
        ]},
    ],
    "sidebar": [
        {"title": "Ratios de rentabilidad", "kv": [
            {"k": "ROE", "v": "17,1%"},
            {"k": "ROA", "v": "9,8%"},
            {"k": "ROIC", "v": "14,1%"},
            {"k": "Margen neto", "v": "8,5%"},
        ], "source": "Fuente: cálculo propio."},
        {"title": "Liquidez", "kv": [
            {"k": "Current ratio", "v": "1,8x"},
            {"k": "Caja / deuda CP", "v": "≈ 3,1x"},
            {"k": "Cobertura de intereses", "v": "≈ 11x"},
        ], "source": "Fuente: cálculo propio sobre 10-Q."},
    ],
}

# ---------------------------------------------------------------------------
# Capítulo 5 · Valuación
# ---------------------------------------------------------------------------
BETA_POINTS = charts  # placeholder to keep import used; real points generated below
import random  # noqa: E402
random.seed(7)
_scatter_pts = []
for _ in range(180):
    x = random.gauss(0, 0.021)
    y = 0.006 + 1.24 * x + random.gauss(0, 0.024)
    _scatter_pts.append([x, y])

sec_valuacion = {
    "eyebrow": "Valuación",
    "title": "Flujos descontados y contraste con múltiplos de comparables",
    "new_chapter": True,
    "blocks": [
        {"type": "subhead", "text": "Metodología"},
        {"type": "text", "text":
            "El modelo principal es un flujo de caja descontado a la firma (FCFF) a diez años, con "
            "una etapa explícita de cinco años, una etapa de convergencia de cinco años hacia el "
            "crecimiento de la industria, y un valor terminal por crecimiento perpetuo de 2,5%. El "
            "costo de capital surge de un CAPM con beta propia calculada por regresión de retornos "
            "semanales de cinco años contra el SPY, y una prima de riesgo de mercado tomada de los "
            "datasets de industria de NYU Stern."},
        {"type": "text", "text":
            "Ponderamos 70% al resultado del DCF y 30% a una valuación relativa que aplica la mediana "
            "de EV/EBITDA del grupo de comparables sobre el EBITDA estimado 2026 de la compañía. La "
            "elección de peso refleja que el DCF captura mejor la transición de mezcla de ingresos, "
            "que los múltiplos de mercado todavía no reflejan del todo."},
        {"type": "table", "title": "Parámetros del modelo",
         "columns": [{"name": "Valor"}, {"name": "Fuente"}],
         "rows": [
             {"label": "Beta (regresión propia)", "cells": ["1,24", "Precios semanales 5a vs. SPY"]},
             {"label": "Tasa libre de riesgo", "cells": ["4,10%", "UST 10 años"]},
             {"label": "Prima de riesgo de mercado", "cells": ["4,60%", "NYU Stern (Damodaran)"]},
             {"label": "Costo del equity (CAPM)", "cells": ["9,80%", "Cálculo propio"]},
             {"label": "Costo de la deuda pre-tax", "cells": ["5,20%", "Yield de la deuda vigente"]},
             {"label": "WACC", "cells": ["9,20%", "Cálculo propio"], "cls": "highlight"},
             {"label": "Crecimiento perpetuo", "cells": ["2,50%", "Supuesto propio"]},
         ],
         "note": "Fuente: elaboración propia. La tasa libre de riesgo y la prima de riesgo varían con el mercado."},
        {"type": "figure", "title": "Dispersión de retornos semanales vs. SPY (5 años)",
         "svg": charts.regression_scatter(_scatter_pts, beta=1.24, alpha=0.006, width=7.2, height=3.0),
         "caption": "Cada punto es un par de retornos semanales; la recta es la regresión OLS.",
         "ref": "Ref.: cálculo propio sobre precios de cierre semanales, Yahoo Finance."},
        {"type": "subhead", "text": "Escenarios"},
        {"type": "text", "text":
            "Construimos tres escenarios según la velocidad de conversión del backlog de mandatos de "
            "IA. El escenario bajista asume que la concentración de clientes se traduce en pérdida de "
            "dos mandatos grandes durante 2027; el base asume la conversión de guidance actual; y el "
            "alcista asume que la compañía repite en dos clientes adicionales el patrón de expansión "
            "que ya mostró en sus cuatro cuentas ancla."},
        {"type": "stats", "cards": [
            {"value": "USD 142", "label": "Escenario bajista", "sub": "pérdida de 2 mandatos ancla en 2027"},
            {"value": "USD 226", "label": "Escenario base", "sub": "conversión según guidance vigente", "tone": "navy"},
            {"value": "USD 278", "label": "Escenario alcista", "sub": "expansión a 2 clientes adicionales"},
        ]},
        {"type": "subhead", "text": "Sensibilidad del precio objetivo"},
        {"type": "table", "title": "Precio objetivo según WACC y crecimiento perpetuo",
         "columns": [{"name": "g = 1,5%"}, {"name": "g = 2,5%"}, {"name": "g = 3,5%"}],
         "rows": [
             {"label": "WACC 8,2%", "cells": ["USD 241", "USD 268", "USD 305"]},
             {"label": "WACC 9,2%", "cells": ["USD 211", "USD 226", "USD 246"], "cls": "highlight"},
             {"label": "WACC 10,2%", "cells": ["USD 188", "USD 198", "USD 211"]},
         ],
         "note": "Fuente: modelo propio, sensibilidad sobre el escenario base."},
        {"type": "subhead", "text": "Cruce con múltiplos de comparables"},
        {"type": "text", "text":
            "Aplicando la mediana de EV/EBITDA del grupo (18,7x) sobre el EBITDA estimado 2026 de "
            "USD 812 millones, la valuación relativa devuelve un valor de la firma de USD 15.180 "
            "millones, equivalente a USD 202,10 por acción tras descontar la deuda neta. El resultado "
            "queda 10,6% por debajo del objetivo del DCF, consistente con la idea de que el mercado "
            "ya empieza a reconocer parte —pero no la totalidad— de la transición de mezcla."},
        {"type": "callout", "big": "USD 226", "text": "precio objetivo ponderado: 70% flujos descontados, 30% múltiplos de comparables"},
    ],
    "sidebar": [
        {"title": "Convergencia de metodologías", "kv": [
            {"k": "DCF (70%)", "v": "USD 236,40"},
            {"k": "Múltiplos (30%)", "v": "USD 202,10"},
            {"k": "Objetivo ponderado", "v": "USD 226,00"},
        ], "source": "Fuente: modelo propio."},
        {"title": "Rango de valuación",
         "svg": charts.target_range(low=142.0, base=226.0, high=278.0, current=PRICE, width=2.5, height=1.5),
         "source": "Fuente: modelo propio."},
    ],
}

# ---------------------------------------------------------------------------
# Capítulo 6 · Riesgos de inversión
# ---------------------------------------------------------------------------
sec_riesgos = {
    "eyebrow": "Riesgos de inversión",
    "title": "Los riesgos están más en la ejecución comercial que en el balance",
    "new_chapter": True,
    "blocks": [
        {"type": "subhead", "text": "Concentración de clientes"},
        {"type": "text", "text":
            "Tres clientes concentran 41% del backlog de mandatos de ingeniería de IA. La pérdida o "
            "postergación de uno solo de estos contratos tendría un impacto desproporcionado sobre el "
            "crecimiento del segmento de mayor margen, precisamente el que sostiene la tesis de "
            "revalorización. La compañía no reporta cláusulas de exclusividad ni penalidades "
            "significativas por cancelación anticipada en sus contratos tipo, según se desprende de "
            "la nota de compromisos del 10-K."},
        {"type": "subhead", "text": "Ejecución del guidance"},
        {"type": "text", "text":
            "El guidance de ingresos 2026 (USD 5.050-5.150 millones) asume una tasa de conversión del "
            "pipeline comercial de ingeniería de IA que la compañía no alcanzó durante 2025, cuando el "
            "pipeline reportado a comienzos de año se convirtió a una tasa ocho puntos porcentuales "
            "menor a la asumida. Un desvío similar en 2026 dejaría los ingresos del segmento de IA "
            "por debajo del rango bajo del guidance."},
        {"type": "subhead", "text": "Exposición cambiaria"},
        {"type": "text", "text":
            "El 38% de la base de costos está denominada en monedas de Europa del Este, donde la "
            "compañía tiene sus centros de desarrollo de software. La compañía cubre parcialmente "
            "esta exposición con contratos forward a seis meses, pero no cubre la totalidad, por lo "
            "que una apreciación sostenida de esas monedas frente al dólar comprimiría el margen "
            "bruto del segmento de IA más que el tradicional, que se factura mayormente en dólares."},
        {"type": "subhead", "text": "Normalización del ciclo de gasto en IA de los clientes"},
        {"type": "text", "text":
            "Parte de la reversión de márgenes coincide con un ciclo de gasto en inteligencia "
            "artificial de los clientes de la compañía que podría normalizarse. Si el gasto en "
            "proyectos de IA de las empresas clientes se desacelera de forma generalizada —un riesgo "
            "de mercado más que específico de la compañía— la tasa de conversión de pipeline podría "
            "resentirse independientemente de la ejecución de Northbeam."},
        {"type": "subhead", "text": "Factores de riesgo declarados por la compañía"},
        {"type": "text", "text":
            "El Item 1A del último 10-K de la compañía —la sección de factores de riesgo que integra "
            "el propio filing ante la SEC— agrega dos riesgos que no priorizamos arriba por "
            "considerarlos de menor probabilidad, pero que forman parte de la divulgación oficial: "
            "dependencia de un número reducido de proveedores de talento técnico especializado en "
            "modelos de lenguaje, y litigios laborales pendientes en dos jurisdicciones europeas por "
            "clasificación de contratistas."},
    ],
}

# ---------------------------------------------------------------------------
# Capítulo 7 · Gobierno corporativo y propiedad
# ---------------------------------------------------------------------------
sec_gobierno = {
    "eyebrow": "Gobierno corporativo y propiedad",
    "title": "Estructura accionaria y alineación de incentivos",
    "new_chapter": False,
    "blocks": [
        {"type": "text", "text":
            "Los fundadores y el equipo directivo controlan 14,2% del capital, sin acciones de voto "
            "múltiple ni estructuras duales que separen propiedad de control. Los inversores "
            "institucionales explican 71,8% del free float, con una base de tenedores relativamente "
            "estable: los cinco principales institucionales no cambiaron su posición combinada en más "
            "de dos puntos porcentuales en los últimos cuatro trimestres."},
        {"type": "table", "title": "Principales tenedores institucionales",
         "columns": [{"name": "% del capital"}],
         "rows": [
             {"label": "Vanguard Group", "cells": ["9,8%"]},
             {"label": "BlackRock", "cells": ["8,1%"]},
             {"label": "State Street", "cells": ["5,4%"]},
             {"label": "T. Rowe Price", "cells": ["4,2%"]},
             {"label": "Wellington Management", "cells": ["3,6%"]},
         ],
         "note": "Fuente: Yahoo Finance, institutional holders."},
    ],
    "sidebar": [
        {"title": "Estructura de propiedad", "kv": [
            {"k": "Fundadores y directivos", "v": "14,2%"},
            {"k": "Institucionales", "v": "71,8%"},
            {"k": "Público minorista", "v": "14,0%"},
        ], "source": "Fuente: Yahoo Finance, major holders."},
    ],
}

# ---------------------------------------------------------------------------
# Capítulo 8 · Apéndice financiero (ancho completo, sin sidebar)
# ---------------------------------------------------------------------------
sec_apendice_fin = {
    "eyebrow": "Apéndice",
    "title": "Estados financieros completos",
    "new_chapter": True,
    "sidebar": None,
    "blocks": [
        {"type": "table", "title": "Estado de resultados (USD millones)",
         "columns": [{"name": y} for y in YEARS],
         "rows": [
             {"label": "Ingresos", "cells": _cells(REVENUE)},
             {"label": "Costo de ingresos", "cells": _cells([r - g for r, g in zip(REVENUE, GROSS_PROFIT)])},
             {"label": "Utilidad bruta", "cells": _cells(GROSS_PROFIT), "cls": "highlight"},
             {"label": "Gastos de venta y administración", "cells": _cells([g - e - 40 for g, e in zip(GROSS_PROFIT, EBIT)])},
             {"label": "I+D", "cells": _cells([40] * 6)},
             {"label": "Resultado operativo (EBIT)", "cells": _cells(EBIT)},
             {"label": "Depreciación y amortización", "cells": _cells([e1 - e2 for e1, e2 in zip(EBITDA, EBIT)])},
             {"label": "EBITDA", "cells": _cells(EBITDA), "cls": "highlight"},
             {"label": "Resultado financiero neto", "cells": _cells([-18, -22, -31, -35, -24, -14])},
             {"label": "Impuesto a las ganancias", "cells": _cells([-110, -111, -124, -127, -139, -181])},
             {"label": "Resultado neto", "cells": _cells(NET_INCOME), "cls": "highlight"},
             {"label": "EPS diluido (USD)", "cells": ["5,98", "6,54", "6,15", "3,98", "7,63", "8,84"]},
         ],
         "note": "Fuente: cálculo propio sobre 10-K y 10-Q presentados ante la SEC. Cifras en USD millones salvo EPS."},
        {"type": "table", "title": "Balance (USD millones)",
         "columns": [{"name": y} for y in YEARS[2:]],
         "rows": [
             {"label": "Caja y equivalentes", "cells": ["312", "298", "356", "441"]},
             {"label": "Cuentas por cobrar", "cells": ["468", "489", "520", "561"]},
             {"label": "Activo corriente", "cells": ["890", "902", "988", "1.102"]},
             {"label": "Activo fijo neto", "cells": ["340", "355", "382", "410"]},
             {"label": "Llave de negocio e intangibles", "cells": ["610", "648", "740", "868"]},
             {"label": "Activo total", "cells": ["2.140", "2.205", "2.410", "2.680"], "cls": "highlight"},
             {"label": "Deuda de corto plazo", "cells": ["120", "95", "80", "70"]},
             {"label": "Pasivo corriente", "cells": ["510", "534", "561", "612"]},
             {"label": "Deuda de largo plazo", "cells": ["552", "485", "360", "230"]},
             {"label": "Pasivo total", "cells": ["1.240", "1.219", "1.191", "1.282"]},
             {"label": "Patrimonio neto", "cells": ["1.240", "1.389", "1.680", "2.010"], "cls": "highlight"},
         ],
         "note": "Fuente: cálculo propio sobre 10-K y 10-Q."},
        {"type": "table", "title": "Flujo de efectivo (USD millones)",
         "columns": [{"name": y} for y in YEARS],
         "rows": [
             {"label": "Flujo operativo (CFO)", "cells": _cells(CFO)},
             {"label": "Capex", "cells": _cells([-c for c in CAPEX])},
             {"label": "Flujo libre de caja (FCF)", "cells": _cells(FCF), "cls": "highlight"},
             {"label": "Adquisiciones", "cells": ["0", "-45", "0", "-62", "0", "0"]},
             {"label": "Recompra de acciones", "cells": ["-30", "-35", "-20", "0", "-40", "-55"]},
             {"label": "Pago neto de deuda", "cells": ["20", "-25", "-40", "-135", "-125", "-160"]},
         ],
         "note": "Fuente: estado de flujo de efectivo, 10-K."},
    ],
}

sec_apendice_mercado = {
    "eyebrow": "Apéndice",
    "title": "Consenso de analistas y comparables",
    "new_chapter": False,
    "sidebar": None,
    "blocks": [
        {"type": "table", "title": "Consenso de analistas — estimates",
         "columns": [{"name": "2026E"}, {"name": "2027E"}, {"name": "2028E"}],
         "rows": [
             {"label": "Ingresos (USD M)", "cells": ["5.098", "5.512", "5.940"]},
             {"label": "EBITDA (USD M)", "cells": ["812", "912", "1.020"], "cls": "highlight"},
             {"label": "EPS diluido (USD)", "cells": ["10,42", "11,88", "13,20"]},
             {"label": "Número de analistas", "cells": ["14", "12", "8"]},
         ],
         "note": "Fuente: Yahoo Finance y stockanalysis.com, consenso al 5/8/2026."},
        {"type": "table", "title": "Distribución de recomendaciones",
         "columns": [{"name": "Analistas"}],
         "rows": [
             {"label": "Comprar / Sobreponderar", "cells": ["9"]},
             {"label": "Mantener", "cells": ["4"]},
             {"label": "Vender / Subponderar", "cells": ["1"]},
         ],
         "note": "Fuente: Yahoo Finance, recommendations summary."},
        {"type": "table", "title": "Comparables — detalle ampliado",
         "columns": [{"name": p} for p in PEERS],
         "rows": [
             {"label": "EV / EBITDA", "cells": [_loc(f"{v:.1f}") + "x" for v in PEER_EV_EBITDA]},
             {"label": "P/E forward", "cells": [_loc(f"{v:.1f}") + "x" for v in PEER_PE_FWD]},
             {"label": "Margen EBITDA", "cells": [_loc(f"{v:.1f}") + "%" for v in PEER_EBITDA_MARGIN]},
             {"label": "Crecimiento de ingresos", "cells": [_loc(f"{v:.1f}") + "%" for v in PEER_GROWTH]},
             {"label": "FCF yield", "cells": [_loc(f"{v:.1f}") + "%" for v in PEER_FCF_YIELD]},
             {"label": "ROIC", "cells": [_loc(f"{v:.1f}") + "%" for v in PEER_ROIC]},
             {"label": "Deuda neta / EBITDA", "cells": [_loc(f"{v:.1f}") + "x" for v in PEER_ND_EBITDA]},
         ],
         "note": "Fuente: stockanalysis.com, Yahoo Finance, cálculo propio. Precios de cierre del 5/8/2026."},
        {"type": "subhead", "text": "Glosario"},
        {"type": "kv", "rows": [
            {"k": "EV/EBITDA", "v": "Enterprise Value sobre EBITDA; múltiplo de valuación agnóstico a la estructura de capital."},
            {"k": "FCF yield", "v": "Flujo libre de caja sobre capitalización de mercado."},
            {"k": "ROIC", "v": "Retorno sobre el capital invertido: EBIT después de impuestos sobre deuda más patrimonio."},
            {"k": "WACC", "v": "Costo promedio ponderado de capital, usado como tasa de descuento en el DCF."},
            {"k": "Beta", "v": "Sensibilidad del retorno de la acción al retorno del mercado, estimada por regresión."},
        ]},
    ],
}

REPORT = {
    "company": {"name": "Northbeam Systems, Inc.", "ticker": TICKER},
    "header": {
        "eyebrow": "Equity research · Informe de inicio de cobertura",
        "tagline": "De proveedor de servicios de IT a socio de ingeniería de plataformas de IA",
        "source_line": "Elaborado con filings ante la SEC, datos de mercado y modelo propio · 6 de agosto de 2026",
        "kpis": HEADER_KPIS,
        "toc": [
            {"name": "Resumen ejecutivo", "page": "2"},
            {"name": "Descripción del negocio", "page": "3"},
            {"name": "Posicionamiento competitivo", "page": "4"},
            {"name": "Análisis financiero", "page": "5"},
            {"name": "Valuación", "page": "7"},
            {"name": "Riesgos de inversión", "page": "9"},
            {"name": "Gobierno corporativo y propiedad", "page": "10"},
            {"name": "Apéndice: estados financieros", "page": "11"},
            {"name": "Apéndice: consenso y comparables", "page": "12"},
            {"name": "Fuentes y advertencias", "page": "13"},
        ],
    },
    "call": {"rating": "COMPRAR", "rating_sub": "recomendación · horizonte 12m",
             "pill": "Riesgo medio", "pill_class": "warn"},

    "sections": [
        sec_resumen, sec_negocio, sec_competencia, sec_financiero,
        sec_valuacion, sec_riesgos, sec_gobierno,
        sec_apendice_fin, sec_apendice_mercado,
    ],

    "sources": [
        {"k": "Estados contables", "v": "SEC EDGAR — API XBRL companyfacts (10-K y 10-Q)"},
        {"k": "Guidance", "v": "SEC EDGAR — 8-K item 2.02, Exhibit 99.1 del 31/07/2026"},
        {"k": "Negocio, riesgos y MD&A", "v": "SEC EDGAR — 10-K, Item 1, Item 1A e Item 7"},
        {"k": "Datos de mercado", "v": "Yahoo Finance y stockanalysis.com"},
        {"k": "Benchmarks de industria", "v": "NYU Stern — datasets de Aswath Damodaran, enero 2026"},
        {"k": "Beta y estadística", "v": "Cálculo propio por regresión OLS sobre precios semanales"},
    ],
    "disclaimer":
        "Documento de análisis elaborado con información pública: filings ante la SEC (10-K, 10-Q y 8-K), "
        "datos de mercado de Yahoo Finance y stockanalysis.com, y datasets de industria de NYU Stern. Las "
        "proyecciones son estimaciones propias sujetas a error y no constituyen garantía de resultados "
        "futuros. Los múltiplos de comparables son niveles de mercado a la fecha indicada y varían a diario. "
        "Este documento no constituye asesoramiento financiero, legal ni impositivo, ni una oferta o "
        "invitación a comprar o vender valor alguno. Toda decisión de inversión debe adoptarse con análisis "
        "propio y, de corresponder, asesoramiento profesional matriculado.",
    "signoff": {"name": "Mesa de Research",
                "line": "Northbeam Systems (NBSY) · Informe de inicio de cobertura"},
    "footer_left": "Northbeam Systems (NBSY) · Informe de inicio de cobertura · agosto 2026",
}


def main() -> None:
    out = Path("outputs/NBSY_informe_DEMO.pdf")
    render.render_report(REPORT, out)
    print("escrito:", out)


if __name__ == "__main__":
    main()
