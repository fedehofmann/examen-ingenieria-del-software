from fastapi import FastAPI, HTTPException
from .storage import save_payment, load_payment, load_all_payments, save_payment_data
from .helpers import validate_payment, can_update, can_revert
from .models import *

app = FastAPI()

@app.get("/payments")
async def get_payments():
    return load_all_payments()

@app.post("/payments/{payment_id}")
async def register_payment(payment_id: str, amount: float, payment_method: str):
    existing = load_payment(payment_id)
    if existing is not None:
        raise HTTPException(status_code=400, detail="Payment already exists")

    save_payment(payment_id, amount, payment_method, STATUS_REGISTRADO)
    return {"message": "Payment registered"}

@app.post("/payments/{payment_id}/update")
async def update_payment(payment_id: str, amount: float, payment_method: str):
    payment = load_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not can_update(payment):
        raise HTTPException(status_code=400, detail="Only REGISTRADO payments can be updated")

    payment[AMOUNT] = amount
    payment[PAYMENT_METHOD] = payment_method
    save_payment_data(payment_id, payment)
    return {"message": "Payment updated"}

@app.post("/payments/{payment_id}/pay")
async def pay(payment_id: str):
    payment = load_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment[STATUS] != STATUS_REGISTRADO:
        raise HTTPException(status_code=400, detail="Only REGISTRADO payments can be paid")

    if validate_payment(payment):
        payment[STATUS] = STATUS_PAGADO
    else:
        payment[STATUS] = STATUS_FALLIDO

    save_payment_data(payment_id, payment)
    return {"status": payment[STATUS]}

@app.post("/payments/{payment_id}/revert")
async def revert(payment_id: str):
    payment = load_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not can_revert(payment):
        raise HTTPException(status_code=400, detail="Only FALLIDO payments can be reverted")

    payment[STATUS] = STATUS_REGISTRADO
    save_payment_data(payment_id, payment)
    return {"message": "Payment reverted"}
