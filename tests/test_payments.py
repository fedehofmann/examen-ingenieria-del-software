from fastapi.testclient import TestClient
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

def test_pay_paypal_valid():
    # Primero, registra un pago con PayPal
    response = client.post("/payments/4?amount=4500&payment_method=PAYPAL")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Payment registered"
    
    # Luego, intenta realizar el pago
    response = client.post("/payments/4/pay")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "STATUS_PAGADO"