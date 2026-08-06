"""Render final: Jinja -> HTML -> PDF (wkhtmltopdf).

Dos modos:
  - one-pager: hoja continua, sin cortes, recortada al alto exacto del
    contenido (igual que el documento de referencia).
  - informe: A4 multipagina con numeracion.
"""
from __future__ import annotations

import shutil
import logging
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

log = logging.getLogger(__name__)

HERE = Path(__file__).parent
WKHTML = shutil.which("wkhtmltopdf") or "wkhtmltopdf"

# Ancho de hoja del documento de referencia (666 pt).
SHEET_WIDTH_PT = 666
PROBE_HEIGHT_PT = 5200


def _env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(HERE)),
        autoescape=select_autoescape(default=False),  # los SVG se insertan crudos
    )
    return env


def build_html(template: str, data: dict) -> str:
    css = (HERE / "theme.css").read_text(encoding="utf-8")
    return _env().get_template(template).render(d=data, css=css)


def _run_wkhtml(html: str, out: Path, args: list[str]) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(html)
        src = fh.name
    cmd = [WKHTML, "--enable-local-file-access", "--print-media-type",
           "--disable-smart-shrinking", *args, src, str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    Path(src).unlink(missing_ok=True)
    if proc.returncode != 0 and not out.exists():
        raise RuntimeError(f"wkhtmltopdf fallo:\n{proc.stderr[-2000:]}")


def _content_height_pt(pdf: Path) -> float | None:
    """Alto real del contenido, para recortar la hoja al final del texto."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return None

    doc = fitz.open(pdf)
    page = doc[0]
    rect = None
    for blk in page.get_text("blocks"):
        r = fitz.Rect(blk[:4])
        rect = r if rect is None else rect | r
    for dr in page.get_drawings():
        r = dr["rect"]
        if r.height < page.rect.height * 0.98:  # ignora el fondo de hoja completa
            rect = r if rect is None else rect | r
    doc.close()
    return (rect.y1 if rect else None)


def render_onepager(data: dict, out: Path) -> Path:
    """Hoja unica continua, recortada al alto del contenido."""
    html = build_html("onepager.html.j2", data)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    base = [
        "--page-width", f"{SHEET_WIDTH_PT}pt",
        "--margin-top", "0", "--margin-bottom", "0",
        "--margin-left", "0", "--margin-right", "0",
        "--dpi", "96",
    ]

    probe = out.with_suffix(".probe.pdf")
    _run_wkhtml(html, probe, base + ["--page-height", f"{PROBE_HEIGHT_PT}pt"])

    height = _content_height_pt(probe)
    if height:
        final_h = round(height + 26)
        _run_wkhtml(html, out, base + ["--page-height", f"{final_h}pt"])
        probe.unlink(missing_ok=True)
        log.info("one-pager %s (%s x %s pt)", out.name, SHEET_WIDTH_PT, final_h)
    else:
        probe.replace(out)
        log.warning("PyMuPDF no disponible: hoja sin recortar")

    return out


def render_report(data: dict, out: Path, *, template: str = "report.html.j2") -> Path:
    """Informe largo en A4 con pie de pagina numerado."""
    html = build_html(template, data)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    _run_wkhtml(
        html,
        out,
        [
            "--page-size", "A4",
            "--margin-top", "0mm", "--margin-bottom", "16mm",
            "--margin-left", "0mm", "--margin-right", "0mm",
            "--footer-font-name", "Carlito",
            "--footer-font-size", "7",
            "--footer-spacing", "6",
            "--footer-left", data.get("footer_left", ""),
            "--footer-right", "[page] / [topage]",
        ],
    )
    return out
