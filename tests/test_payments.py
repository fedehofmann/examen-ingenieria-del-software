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

def load_payments():
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_payments(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def setup_function():
    """Se ejecuta antes de cada test."""
    payments = {}
    save_payments(payments)

# ---------------------------------------------------------
# 1) Test: PayPal inválido (amount >= 5000)
# ---------------------------------------------------------
def test_paypal_invalid_amount():
    client.post("/payments/10?amount=6000&payment_method=PAYPAL")
    response = client.post("/payments/10/pay")

    assert response.status_code == 200
    assert response.json()["status"] == "FALLIDO"

    payments = load_payments()
    assert payments["10"]["status"] == "FALLIDO"

# ---------------------------------------------------------
# 2) Test: Más de un crédito REGISTRADO → segundo debe fallar
# ---------------------------------------------------------
def test_credit_card_multiple_registered_should_fail():
    # Primer pago con tarjeta (válido)
    client.post("/payments/11?amount=100&payment_method=CREDIT_CARD")

    # Segundo pago con tarjeta (registrado simultáneamente)
    client.post("/payments/12?amount=200&payment_method=CREDIT_CARD")

    # Al intentar pagar el segundo → FALLIDO por regla del examen
    response = client.post("/payments/12/pay")
    assert response.json()["status"] == "FALLIDO"

# ---------------------------------------------------------
# 3) Test: Update permitido solo si está REGISTRADO
# ---------------------------------------------------------
def test_update_not_registered_fails():
    client.post("/payments/20?amount=100&payment_method=PAYPAL")
    client.post("/payments/20/pay")  # pasa a PAGADO

    response = client.post("/payments/20/update?amount=500&payment_method=CREDIT_CARD")

    assert response.status_code == 400
    assert response.json()["detail"] == "Only REGISTRADO payments can be updated"

# ---------------------------------------------------------
# 4) Test: Update exitoso en estado REGISTRADO
# ---------------------------------------------------------
def test_update_successful():
    client.post("/payments/21?amount=100&payment_method=PAYPAL")

    response = client.post("/payments/21/update?amount=300&payment_method=CREDIT_CARD")
    assert response.status_code == 200

    payments = load_payments()
    assert payments["21"]["amount"] == 300
    assert payments["21"]["payment_method"] == "CREDIT_CARD"

# ---------------------------------------------------------
# 5) Test: Revert exitoso (FALLIDO → REGISTRADO)
# ---------------------------------------------------------
def test_revert_successful():
    client.post("/payments/30?amount=20000&payment_method=CREDIT_CARD")
    client.post("/payments/30/pay")  # debe quedar FALLIDO

    response = client.post("/payments/30/revert")
    assert response.status_code == 200

    payments = load_payments()
    assert payments["30"]["status"] == "REGISTRADO"

# ---------------------------------------------------------
# 6) Test: Revert falla si no está FALLIDO
# ---------------------------------------------------------
def test_revert_invalid_state():
    client.post("/payments/31?amount=100&payment_method=PAYPAL")  # REGISTRADO

    response = client.post("/payments/31/revert")
    assert response.status_code == 400
    assert response.json()["detail"] == "Only FALLIDO payments can be reverted"

# ---------------------------------------------------------
# 7) Test: 404 cuando payment_id no existe en PAY
# ---------------------------------------------------------
def test_pay_404_not_found():
    response = client.post("/payments/999/pay")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

# ---------------------------------------------------------
# 8) Test: 404 cuando payment_id no existe en UPDATE
# ---------------------------------------------------------
def test_update_404_not_found():
    response = client.post("/payments/888/update?amount=10&payment_method=PAYPAL")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

# ---------------------------------------------------------
# 9) Test: 404 cuando payment_id no existe en REVERT
# ---------------------------------------------------------
def test_revert_404_not_found():
    response = client.post("/payments/777/revert")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"