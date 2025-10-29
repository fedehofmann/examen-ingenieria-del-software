from fastapi import FastAPI, HTTPException

app = FastAPI()

# Simulación de almacenamiento en memoria
payments = {}

# Constantes del flujo
STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "STATUS_PAGADO"
STATUS_FALLIDO = "FALLIDO"

PAYMENT_METHOD_CREDIT = "CREDIT_CARD"
PAYMENT_METHOD_PAYPAL = "PAYPAL"

@app.get("/payments")
async def get_payments():
    return payments


@app.get("/")
async def health():
    return {"ok": True}


@app.post("/payments/{payment_id}")
async def register_payment(payment_id: str, amount: float, payment_method: str):

    if payment_id in payments:
        raise HTTPException(status_code=400, detail="Payment already exists")

    payments[payment_id] = {
        "amount": amount,
        "payment_method": payment_method,
        "status": STATUS_REGISTRADO
    }
    return {"message": "Payment registered"}


@app.post("/payments/{payment_id}/update")
async def update_payment(payment_id: str, amount: float, payment_method: str):
    if payment_id not in payments:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payments[payment_id]["status"] != STATUS_REGISTRADO:
        raise HTTPException(status_code=400, detail="Only REGISTRADO payments can be updated")

    payments[payment_id]["amount"] = amount
    payments[payment_id]["payment_method"] = payment_method

    return {"message": "Payment updated"}


@app.post("/payments/{payment_id}/pay")
async def pay(payment_id: str):
    if payment_id not in payments:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = payments[payment_id]

    if payment["status"] != STATUS_REGISTRADO:
        raise HTTPException(status_code=400, detail="Only REGISTRADO payments can be paid")

    valid = False

    if payment["payment_method"] == PAYMENT_METHOD_CREDIT:
        # Validación crédito
        if payment["amount"] < 10000:
            registered_credit_count = sum(
                1 for p in payments.values()
                if p["payment_method"] == PAYMENT_METHOD_CREDIT and p["status"] == STATUS_REGISTRADO
            )
            valid = registered_credit_count <= 1

    elif payment["payment_method"] == PAYMENT_METHOD_PAYPAL:
        # Validación PayPal
        valid = payment["amount"] < 5000

    if valid:
        payment["status"] = STATUS_PAGADO
    else:
        payment["status"] = STATUS_FALLIDO

    return {"status": payment["status"]}


@app.post("/payments/{payment_id}/revert")
async def revert(payment_id: str):
    if payment_id not in payments:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = payments[payment_id]

    if payment["status"] != STATUS_FALLIDO:
        raise HTTPException(status_code=400, detail="Only FALLIDO payments can be reverted")

    payment["status"] = STATUS_REGISTRADO
    return {"message": "Payment reverted"}
