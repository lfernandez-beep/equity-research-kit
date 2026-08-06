# Equity Research Kit

Genera dos documentos de análisis de acciones US a partir de un ticker:

- **One-pager** — hoja continua, tesis en tres bloques con gráfico de apoyo, snapshot, guidance, peers y rango de valuación.
- **Informe completo** — A4 multipágina con portada, resumen ejecutivo, análisis financiero, valuación y apéndice de fuentes.

Ambos comparten la misma identidad visual (`render/theme.css`) y la misma librería de gráficos.

---

## Por qué hay dos partes

Los sitios de datos financieros no son accesibles desde el entorno donde se
redacta el análisis. La recolección corre en **GitHub Actions**, que sí tiene
salida libre a internet, y deja un JSON commiteado en el repo. El análisis
después lee ese JSON por la URL `raw.githubusercontent.com`.

```
GitHub Actions  →  data/{TICKER}/latest.json  →  análisis y redacción  →  PDF
```

---

## Puesta en marcha

1. Crear un repo (puede ser privado) y subir estos archivos.
2. En **Settings → Secrets and variables → Actions**, crear el secret
   `SEC_USER_AGENT` con el formato que exige la SEC:
   `Nombre Apellido mail@dominio.com`. Sin esto, EDGAR bloquea los pedidos.
3. En **Settings → Actions → General → Workflow permissions**, habilitar
   *Read and write permissions* para que el workflow pueda commitear.

## Uso

**Recolectar datos** — desde la pestaña Actions, workflow `fetch-ticker`,
botón *Run workflow*, con el ticker y opcionalmente los comparables. O por API:

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/USUARIO/REPO/actions/workflows/fetch.yml/dispatches \
  -d '{"ref":"main","inputs":{"ticker":"AAPL","peers":"MSFT,IBM,ACN"}}'
```

El resultado queda en `data/AAPL/latest.json`.

**Generar los PDF** — local, con el JSON ya descargado:

```bash
pip install -r requirements.txt
sudo apt-get install -y wkhtmltopdf

python -m samples.demo_onepager   # one-pager de ejemplo
python -m samples.demo_report     # informe de ejemplo
```

Los PDF salen en `outputs/`.

---

## Estructura

```
fetch/
  http.py           cliente con User-Agent de SEC, throttling y reintentos
  sec_edgar.py      XBRL companyfacts + 8-K item 2.02 con exhibits 99.x
  stockanalysis.py  ratios, consenso, estimates y peers
  yahoo.py          precios, perfil, price targets, holders
  stats.py          beta OLS, R², vol, drawdown, CAPM, WACC
  damodaran.py      benchmarks de industria (NYU Stern)
  ratios.py         profitability, growth, valuation, solvencia y ratios forward
  run.py            orquesta todo y escribe el JSON

render/
  theme.css         identidad visual compartida
  charts.py         8 tipos de gráfico en SVG
  onepager.html.j2  template del one-pager
  report.html.j2    template del informe
  build_onepager.py arma el one-pager desde el JSON
  render.py         HTML → PDF con wkhtmltopdf
```

---

## Fuentes

| Bloque | Fuente | Notas |
|---|---|---|
| Estados contables | SEC EDGAR (API XBRL) | Oficial, sin API key |
| Guidance | SEC EDGAR — 8-K item 2.02, Exhibit 99.1/99.2 | Press release oficial, no un resumen de terceros |
| Ratios, consenso, peers | stockanalysis.com | JSON embebido de Next.js |
| Precios y datos de mercado | Yahoo Finance (`yfinance`) | Endpoint no oficial: todo con `try/except` |
| Benchmarks de industria | NYU Stern — datasets de Damodaran | Actualizados cada enero |
| Beta y estadística | Cálculo propio | Regresión OLS, no tomado de terceros |

**Análisis cualitativo (Seeking Alpha, Simply Wall St)**: no se scrapean. Se
cargan a mano imprimiendo la página a PDF y adjuntándola junto con el ticker.
Se usan como insumo para redactar un análisis propio, parafraseando y citando
la fuente — nunca reproduciendo el texto original, que tiene derechos de autor.

---

## Notas técnicas

- `wkhtmltopdf` usa un WebKit viejo: **no hay flexbox ni grid**. Todo el layout
  se resuelve con `table`, `inline-block` y `float`.
- En Jinja, `items` y `values` colisionan con los métodos de `dict`. Las claves
  de datos usan `rows` y `cells`.
- El one-pager se renderiza con una altura de sondeo y después se recorta al
  alto real del contenido usando PyMuPDF, para que quede una sola hoja continua.
- Los SVG de matplotlib se topean a su ancho natural (`max-width`): si escalaran
  al 100%, el texto de los ejes escalaría con ellos.

## Advertencia

Los documentos generados son material de análisis con información pública. No
constituyen asesoramiento financiero ni recomendación de inversión.
