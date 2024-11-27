import pytest
import requests
from servidor import app
from cliente import obtener_productos

@pytest.fixture(scope="module")
def app_cliente():
    """Crea un cliente de prueba para el servidor Flask."""
    with app.test_client() as test_client:
        yield test_client

def test_servidor_responde(app_cliente):
    """Verifica que el servidor responda correctamente."""
    response = app_cliente.get('/productos')
    assert response.status_code == 200

def test_formato_json(app_cliente):
    """Verifica que la respuesta del servidor esté en formato JSON."""
    response = app_cliente.get('/productos')
    assert response.content_type == 'application/json'

def test_contenido_respuesta(app_cliente):
    """Verifica el contenido de la respuesta del servidor."""
    response = app_cliente.get('/productos')
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 4  # Verificar que hay 4 productos iniciales
    assert data[0]['id'] == 1
    assert data[0]['nombre'] == "Agua"

def test_cliente_obtiene_productos(app_cliente):
    """Prueba que el cliente obtenga correctamente los productos."""
    base_url = "http://localhost:5000"  # URL base del servidor de prueba
    with app.test_request_context():
        productos = obtener_productos(base_url)
        assert productos is not None
        assert len(productos) == 4
        assert productos[0]['id'] == 1
        assert productos[0]['nombre'] == "Agua"

def test_cliente_error_servidor():
    """Simula un error al conectar con el servidor."""
    productos = obtener_productos('http://localhost:5001')  # Puerto incorrecto
    assert productos is None
