"""
Exporta el contrato OpenAPI de la API a openapi.json (COMPLETO -- no lo modifiques).

    python -m app.exportar_openapi
"""
import json
from pathlib import Path

from app.main import app

RUTA = Path(__file__).resolve().parent.parent / "openapi.json"


def main():
    RUTA.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Contrato exportado en {RUTA}")


if __name__ == "__main__":
    main()
