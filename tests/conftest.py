# tests/conftest.py

import pytest
from pathlib import Path
import sys

# Agregar el proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_producto_data():
    return {
        "id": "123",
        "nombre": "Producto Test",
        "precio": 100.50
    }

# @pytest.fixture
# def mock_repository():
#     from unittest.mock import Mock
#     from core.domain.producto.repository import ProductoRepository
#     return Mock(spec=ProductoRepository)
