import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient  # noqa: E402

from app import datos  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def cliente():
    """Un cliente HTTP de prueba con los datos recién reiniciados."""
    datos.reiniciar()
    return TestClient(app)
