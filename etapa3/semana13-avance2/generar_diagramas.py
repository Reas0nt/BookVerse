"""Render the PlantUML diagrams of Avance #2 (RF-11) to PNG through kroki.io.

Usage: ../../venv/bin/python generar_diagramas.py
Needs internet access. Only the standard library is used.
"""

import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIAGRAMS = HERE / "diagramas"
KROKI_URL = "https://kroki.io/plantuml/png"
TIMEOUT_SECONDS = 60


def render(source: Path) -> Path:
    """POST one .puml file to kroki.io and write the PNG next to it."""
    request = urllib.request.Request(
        KROKI_URL,
        data=source.read_bytes(),
        headers={"Content-Type": "text/plain", "User-Agent": "bookverse-diagramas/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        png = response.read()
    target = source.with_suffix(".png")
    target.write_bytes(png)
    return target


def main() -> int:
    sources = sorted(DIAGRAMS.glob("*.puml"))
    if not sources:
        print(f"[ERROR] No .puml files found in {DIAGRAMS}")
        return 1
    for source in sources:
        try:
            target = render(source)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:500]
            print(f"[ERROR] kroki.io rejected {source.name} (HTTP {error.code}): {detail}")
            return 1
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"[ERROR] Cannot reach kroki.io ({error}). Check your internet connection and retry.")
            return 1
        print(f"[OK] {source.name} -> {target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
