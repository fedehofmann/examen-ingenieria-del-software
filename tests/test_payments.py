import sys
sys.path.append('..')

from fastapi.testclient import TestClient
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
client = TestClient(app)

# Ruta del archivo de datos
DATA_PATH = "data.json"

# Función para cargar los pagos desde el archivo JSON
def load_payments():
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Si el archivo no existe, devolvemos un diccionario vacío

# Función para guardar los pagos en el archivo JSON
def save_payments(payments):
    with open(DATA_PATH, "w") as f:
        json.dump(payments, f, indent=4)

def setup_function():
    # Reiniciar los datos antes de cada prueba
    payments = load_payments()
    payments.clear()  # Limpiar todos los pagos
    save_payments(payments)  # Guardar los cambios en el archivo

def test_register_payment():
    response = client.post("/payments/1?amount=2000&payment_method=CREDIT_CARD")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Payment registered"
    
    # Verificar que el pago fue registrado correctamente en el archivo
    payments = load_payments()
    assert "1" in payments
    assert payments["1"]["amount"] == 2000
    assert payments["1"]["payment_method"] == "CREDIT_CARD"
    assert payments["1"]["status"] == "REGISTRADO"

def test_pay_credit_card_valid():
    client.post("/payments/2?amount=2000&payment_method=CREDIT_CARD")
    response = client.post("/payments/2/pay")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "PAGADO"
    
    # Verificar el estado del pago en el archivo
    payments = load_payments()
    assert payments["2"]["status"] == "PAGADO"

def test_pay_credit_card_invalid_limit():
    client.post("/payments/3?amount=20000&payment_method=CREDIT_CARD")
    response = client.post("/payments/3/pay")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "FALLIDO"
    
    # Verificar el estado del pago en el archivo
    payments = load_payments()
    assert payments["3"]["status"] == "FALLIDO"

def test_pay_paypal_valid():
    # Primero, registra un pago con PayPal
    response = client.post("/payments/4?amount=4500&payment_method=PAYPAL")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Payment registered"
    
    # Verificar que el pago fue registrado correctamente en el archivo
    payments = load_payments()
    assert "4" in payments
    assert payments["4"]["amount"] == 4500
    assert payments["4"]["payment_method"] == "PAYPAL"
    assert payments["4"]["status"] == "REGISTRADO"
    
    # Luego, intenta realizar el pago
    response = client.post("/payments/4/pay")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "PAGADO"
    
    # Verificar el estado del pago en el archivo
    payments = load_payments()
    assert payments["4"]["status"] == "PAGADO"
