from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, payments

client = TestClient(app)

def setup_function():
    payments.clear()  # Reiniciamos el "storage" en memoria

def test_register_payment():
    response = client.post("/payments/1?amount=2000&payment_method=CREDIT_CARD")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Payment registered"

def test_pay_credit_card_valid():
    client.post("/payments/2?amount=2000&payment_method=CREDIT_CARD")
    response = client.post("/payments/2/pay")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "STATUS_PAGADO"

def test_pay_credit_card_invalid_limit():
    client.post("/payments/3?amount=20000&payment_method=CREDIT_CARD")
    response = client.post("/payments/3/pay")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "FALLIDO"
