"""Graficos de apoyo, con la paleta y el estilo del one-pager de referencia.

Todos devuelven SVG como string, que se embebe inline en el HTML. Sin ejes
decorativos ni grillas pesadas: cada grafico existe para sostener un punto de
la tesis, igual que en el documento de referencia.
"""
from __future__ import annotations

import io
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

# Paleta muestreada del PDF de referencia
NAVY = "#13304E"
NAVY_SOFT = "#243859"
GOLD = "#AB8A69"
GOLD_DEEP = "#AF8D4E"
GREEN = "#436554"
GREEN_BRIGHT = "#397050"
RUST = "#A0592B"
TEAL = "#2F6B5E"
GREY = "#C9C6BC"
PAPER = "#F7F6F2"
INK = "#3A3A38"

SANS = "Carlito" if any(
    f.name == "Carlito" for f in font_manager.fontManager.ttflist
) else "DejaVu Sans"

plt.rcParams.update(
    {
        "font.family": SANS,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.edgecolor": "#D8D5CC",
        "svg.fonttype": "none",
        "figure.facecolor": "none",
        "axes.facecolor": "none",
    }
)


def _n(value: float, fmt: str = "{:.1f}") -> str:
    """Formato numerico en convencion local: coma decimal, punto de miles."""
    s = fmt.format(value)
    return s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def _svg(fig) -> str:
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)
    svg = buf.getvalue()
    svg = svg[svg.index("<svg") :]
    # matplotlib fija width/height en pt. Se reemplaza por un ancho fluido
    # topeado al tamano natural: el grafico se achica si no entra, pero nunca
    # se agranda (si escalara, el texto de los ejes escalaria con el).
    natural_pt = fig.get_size_inches()[0] * 72
    head_end = svg.index(">")
    head = re.sub(r'\s(width|height)="[^"]*"', "", svg[:head_end])
    head += (
        f' width="100%" preserveAspectRatio="xMidYMid meet"'
        f' style="max-width:{natural_pt:.0f}pt;height:auto"'
    )
    return head + svg[head_end:]


def _clean(ax, *, keep_bottom: bool = True) -> None:
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_visible(keep_bottom)
    ax.tick_params(length=0, labelsize=8)
    ax.grid(False)


def bars_series(
    labels: list[str],
    values: list[float],
    *,
    fmt: str = "{:.0f}",
    highlight_last: bool = True,
    width: float = 7.6,
    height: float = 2.5,
) -> str:
    """Barras simples con el valor sobre cada una. Para revenue, EBITDA, EPS."""
    fig, ax = plt.subplots(figsize=(width, height))
    colors = [NAVY_SOFT] * len(values)
    if highlight_last and colors:
        colors[-1] = GOLD_DEEP
    bars = ax.bar(labels, values, color=colors, width=0.62)

    span = (max(values) - min(min(values), 0)) or 1
    for b, v in zip(bars, values):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + span * 0.04 * (1 if v >= 0 else -1.6),
            _n(v, fmt),
            ha="center",
            va="bottom" if v >= 0 else "top",
            fontsize=8.5,
            fontweight="bold",
            color=NAVY,
        )
    _clean(ax)
    ax.set_yticks([])
    ax.margins(y=0.22)
    if min(values) < 0:
        ax.axhline(0, color="#D8D5CC", lw=0.8)
    return _svg(fig)


def bars_grouped(
    labels: list[str],
    series: dict[str, list[float]],
    *,
    fmt: str = "{:.0f}",
    width: float = 7.6,
    height: float = 2.7,
) -> str:
    """Dos series lado a lado. Para actual vs. estimado, o empresa vs. peers."""
    fig, ax = plt.subplots(figsize=(width, height))
    names = list(series)
    n_series = len(names)
    palette = [NAVY_SOFT, GOLD_DEEP, TEAL]
    step = 0.8 / n_series
    xs = range(len(labels))

    span = max(max(v) for v in series.values()) or 1
    for i, name in enumerate(names):
        off = (i - (n_series - 1) / 2) * step
        vals = series[name]
        ax.bar(
            [x + off for x in xs],
            vals,
            width=step * 0.9,
            label=name,
            color=palette[i % len(palette)],
        )
        for x, v in zip(xs, vals):
            ax.text(
                x + off, v + span * 0.03, _n(v, fmt),
                ha="center", va="bottom", fontsize=7.6, color=NAVY,
            )
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels)
    _clean(ax)
    ax.set_yticks([])
    ax.margins(y=0.2)
    ax.legend(
        frameon=False, fontsize=8, ncol=n_series, loc="upper center",
        bbox_to_anchor=(0.5, 1.22), handlelength=1.1,
    )
    return _svg(fig)


def line_indexed(
    dates: list[str],
    series: dict[str, list[float]],
    *,
    width: float = 7.6,
    height: float = 2.7,
) -> str:
    """Evolucion indexada a 100. Para precio vs. benchmark o vs. peers."""
    fig, ax = plt.subplots(figsize=(width, height))
    palette = [GOLD_DEEP, NAVY_SOFT, GREY, TEAL]
    for i, (name, vals) in enumerate(series.items()):
        base = next((v for v in vals if v), 1)
        ax.plot(
            range(len(vals)),
            [v / base * 100 for v in vals],
            label=name,
            color=palette[i % len(palette)],
            lw=1.6 if i == 0 else 1.1,
        )
    ax.axhline(100, color="#D8D5CC", lw=0.7, ls=(0, (3, 3)))
    step = max(1, len(dates) // 5)
    ax.set_xticks(range(0, len(dates), step))
    ax.set_xticklabels([dates[i][:7] for i in range(0, len(dates), step)])
    _clean(ax)
    ax.tick_params(axis="y", labelsize=8)
    ax.legend(
        frameon=False, fontsize=8, ncol=len(series), loc="upper center",
        bbox_to_anchor=(0.5, 1.2), handlelength=1.4,
    )
    return _svg(fig)


def donut(
    labels: list[str],
    values: list[float],
    *,
    center: str = "",
    width: float = 2.5,
    height: float = 2.5,
) -> str:
    """Composicion: mix de ingresos por segmento o por geografia."""
    fig, ax = plt.subplots(figsize=(width, height))
    colors = [GOLD_DEEP, TEAL, NAVY, GREY, GREEN, RUST][: len(values)]
    ax.pie(
        values,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 1.5},
    )
    if center:
        ax.text(0, 0, center, ha="center", va="center", fontsize=11,
                fontweight="bold", color=NAVY)
    ax.set(aspect="equal")
    return _svg(fig)


def gauge(
    value: float,
    *,
    vmax: float = 3.0,
    bands: tuple[float, float] = (1.0, 2.0),
    label_fmt: str = "{:.1f}x",
    width: float = 4.6,
    height: float = 0.85,
) -> str:
    """Barra semaforo con marcador. Calcado del gauge de leverage del ejemplo."""
    fig, ax = plt.subplots(figsize=(width, height))
    lo, hi = bands
    ax.barh(0, lo, color=GREEN_BRIGHT, height=0.42)
    ax.barh(0, hi - lo, left=lo, color=GOLD_DEEP, height=0.42)
    ax.barh(0, vmax - hi, left=hi, color=RUST, height=0.42)

    pos = min(max(value, 0), vmax)
    ax.plot([pos], [0.33], marker="v", markersize=9, color=NAVY, clip_on=False)
    ax.text(pos, 0.62, _n(value, label_fmt), ha="center", fontsize=9.5,
            fontweight="bold", color=NAVY)

    ax.set_xlim(0, vmax)
    ax.set_ylim(-0.35, 0.9)
    ax.set_yticks([])
    ticks = [0, lo, hi, vmax]
    ax.set_xticks(ticks)
    ax.set_xticklabels([_n(t, label_fmt) for t in ticks], fontsize=7.5)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    return _svg(fig)


def waterfall_margin(
    labels: list[str],
    values: list[float],
    *,
    width: float = 7.6,
    height: float = 2.4,
) -> str:
    """Progresion de margenes por periodo, coloreada por signo."""
    fig, ax = plt.subplots(figsize=(width, height))
    colors = [RUST if v < 0 else (GOLD_DEEP if v < 0.15 else GREEN_BRIGHT) for v in values]
    bars = ax.bar(labels, [v * 100 for v in values], color=colors, width=0.6)
    for b, v in zip(bars, values):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v * 100 + (1.4 if v >= 0 else -3.2),
            _n(v * 100, "{:.1f}") + "%",
            ha="center",
            fontsize=8.5,
            fontweight="bold",
            color=NAVY,
        )
    ax.axhline(0, color="#D8D5CC", lw=0.8)
    _clean(ax, keep_bottom=False)
    ax.set_yticks([])
    ax.margins(y=0.26)
    return _svg(fig)


def peers_scatter(
    points: list[dict],
    *,
    x_key: str = "revenue_growth",
    y_key: str = "ev_ebitda",
    x_label: str = "Crecimiento de ingresos",
    y_label: str = "EV / EBITDA",
    highlight: str | None = None,
    width: float = 7.0,
    height: float = 3.2,
) -> str:
    """Posicionamiento contra comparables: crecimiento vs. multiplo."""
    fig, ax = plt.subplots(figsize=(width, height))
    for p in points:
        x, y = p.get(x_key), p.get(y_key)
        if x is None or y is None:
            continue
        is_self = p.get("ticker") == highlight
        ax.scatter(
            x * 100 if abs(x) < 5 else x,
            y,
            s=110 if is_self else 55,
            color=GOLD_DEEP if is_self else NAVY_SOFT,
            zorder=3,
            edgecolor="white",
            linewidth=1,
        )
        ax.annotate(
            p.get("ticker", ""),
            (x * 100 if abs(x) < 5 else x, y),
            textcoords="offset points",
            xytext=(0, 9),
            ha="center",
            fontsize=8,
            fontweight="bold" if is_self else "normal",
            color=NAVY if is_self else INK,
        )
    ax.set_xlabel(x_label, fontsize=8.5)
    ax.set_ylabel(y_label, fontsize=8.5)
    ax.grid(True, color="#EAE8E1", lw=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=8, length=0)
    ax.margins(0.18)
    return _svg(fig)


def regression_scatter(
    points: list[list[float]],
    *,
    beta: float,
    alpha: float,
    x_label: str = "Retorno semanal del benchmark",
    y_label: str = "Retorno semanal de la acción",
    width: float = 5.2,
    height: float = 3.0,
) -> str:
    """Dispersion de retornos con la recta de regresion. points=[[x,y], ...]."""
    fig, ax = plt.subplots(figsize=(width, height))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, s=14, color=NAVY_SOFT, alpha=0.55, edgecolor="none")

    lo, hi = min(xs), max(xs)
    ax.plot([lo, hi], [alpha + beta * lo, alpha + beta * hi],
            color=GOLD_DEEP, lw=1.8)
    ax.axhline(0, color="#D8D5CC", lw=0.6)
    ax.axvline(0, color="#D8D5CC", lw=0.6)

    ax.set_xlabel(x_label, fontsize=8.5)
    ax.set_ylabel(y_label, fontsize=8.5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=7.5, length=0)
    ax.grid(True, color="#EFEDE6", lw=0.5)
    return _svg(fig)


def target_range(
    *, low: float, base: float, high: float, current: float,
    width: float = 6.6, height: float = 1.5,
) -> str:
    """Rango de precio objetivo con el precio actual marcado."""
    fig, ax = plt.subplots(figsize=(width, height))
    ax.hlines(0, low, high, color=GREY, lw=7, zorder=1)
    ax.hlines(0, min(current, base), max(current, base),
              color=GOLD_DEEP if base > current else RUST, lw=7, zorder=2)

    for x, lbl, col, up in (
        (low, "Bear", RUST, False),
        (base, "Objetivo", NAVY, True),
        (high, "Bull", GREEN_BRIGHT, False),
    ):
        ax.plot([x], [0], marker="|", markersize=17, color=col, mew=2.2, zorder=4)
        ax.text(x, 0.42 if up else -0.55, lbl + "\n" + _n(x, "{:,.2f}"), ha="center",
                va="bottom" if up else "top", fontsize=8.5,
                fontweight="bold" if up else "normal", color=col)

    ax.plot([current], [0], marker="o", markersize=8, color=NAVY,
            markeredgecolor="white", mew=1.5, zorder=5)
    ax.text(current, -0.55, "Hoy\n" + _n(current, "{:,.2f}"), ha="center", va="top",
            fontsize=8.5, color=INK)

    pad = (high - low) * 0.14 or 1
    ax.set_xlim(min(low, current) - pad, max(high, current) + pad)
    ax.set_ylim(-1.25, 1.05)
    ax.axis("off")
    return _svg(fig)
