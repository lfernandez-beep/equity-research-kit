"""Cliente HTTP compartido: user-agent, reintentos con backoff y rate limiting.

La SEC exige un User-Agent identificable y limita a 10 req/s. Yahoo y
stockanalysis tiran 429 si los golpeas rapido. Todo pasa por aca.
"""
from __future__ import annotations

import os
import time
import random
import logging

import requests

log = logging.getLogger(__name__)

# La SEC pide nombre + mail de contacto. Se define como secret/env en Actions.
SEC_UA = os.environ.get("SEC_USER_AGENT", "equity-research-kit contacto@ejemplo.com")

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

_last_call: dict[str, float] = {}


def _throttle(host: str, min_gap: float) -> None:
    prev = _last_call.get(host, 0.0)
    wait = min_gap - (time.time() - prev)
    if wait > 0:
        time.sleep(wait)
    _last_call[host] = time.time()


def get(
    url: str,
    *,
    sec: bool = False,
    min_gap: float = 0.35,
    timeout: int = 30,
    retries: int = 4,
    **kwargs,
) -> requests.Response:
    """GET con reintentos. sec=True usa el User-Agent exigido por la SEC."""
    host = url.split("/")[2]
    headers = {
        "User-Agent": SEC_UA if sec else BROWSER_UA,
        "Accept-Encoding": "gzip, deflate",
    }
    headers.update(kwargs.pop("headers", {}))

    last_exc: Exception | None = None
    for attempt in range(retries):
        _throttle(host, min_gap)
        try:
            r = requests.get(url, headers=headers, timeout=timeout, **kwargs)
            if r.status_code == 429 or 500 <= r.status_code < 600:
                raise requests.HTTPError(f"{r.status_code} en {url}")
            r.raise_for_status()
            return r
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            backoff = (2**attempt) + random.random()
            log.warning("intento %s fallo (%s), reintento en %.1fs", attempt + 1, exc, backoff)
            time.sleep(backoff)

    raise RuntimeError(f"no se pudo traer {url}") from last_exc


def get_json(url: str, **kwargs) -> dict:
    return get(url, **kwargs).json()
