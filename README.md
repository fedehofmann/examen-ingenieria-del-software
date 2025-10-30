# Examen Ingeniería de Datos

Integrantes:
- Matías Caccia
- Federico Hofmann
- Sebastián Mesch Henriques

### API para gestión de pagos

Este repo contiene una API mínima de pagos construida con FastAPI (Python 3.11), un set de tests con Pytest, y un pipeline CI/CD en GitHub Actions. La app persiste datos en un archivo data.json para simplificar el TP.

### Pasos para develop local del proyecto:

1) Requisitos

* Python 3.11
* pip actualizado

2) Instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate # En Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Levantar la API

```bash
uvicorn main:app --reload --port 8000
```

4) Correr los tests por línea de comando

```bash
pytest tests/test_payments.py -v
```

### Endpoints principales (resumen rápido)

Notar que, por cómo está definido el código, los campos se pasan como query params (no en el body), p. ej. ?amount=...&payment_method=...

* GET /
   Healthcheck.
   200 → {"ok": true}

* GET /payments
   Devuelve el contenido completo de data.json.

* POST /payments/{payment_id}
   Registra el pago inicial.
   Query: amount: float, payment_method: "CREDIT_CARD" | "PAYPAL"
   200 → {"message": "Payment registered"}
   400 → si payment_id ya existe.

* POST /payments/{payment_id}/update
   Actualiza amount y/o payment_method.
   Solo si el pago está REGISTRADO.
   404 si no existe, 400 si no está REGISTRADO.

* POST /payments/{payment_id}/pay
   Ejecuta la validación y marca PAGADO o FALLIDO.
   404 si no existe, 400 si no está REGISTRADO.

* POST /payments/{payment_id}/revert
   Revierten pagos FALLIDO → REGISTRADO.
   404 si no existe, 400 si el estado no es FALLIDO.

### Reglas de validación (negocio)

* CREDIT_CARD → válido solo si amount < 10000, y la cantidad de pagos REGISTRADO con CREDIT_CARD en el sistema es <= 1. (Es decir, si hay más de uno “pendiente” de ese método, se rechaza.)

* PAYPAL → válido solo si amount < 5000.

### URL en producción

La app se publica con Render usando Auto Deploy desde la rama production (ver CI/CD más abajo).
URL: https://mia-soft-ing.onrender.com/docs#/default

### CI/CD Pipeline

Archivo: .github/workflows/ci-cd.yml

**Disparadores**

* pull_request a main
* push a main y production

**Jobs**

* test: instala deps en Python 3.11 y corre pytest tests/test_payments.py -v.
* production-note: solo en production muestra una nota (Render hace el deploy automáticamente desde esa rama; no se hace deploy manual dentro del workflow).

**Flujo de release recomendado**

1. Merge a main → corre tests.
2. Cuando está listo para producción, merge/rebase a production. Render detecta el cambio en production y hace Auto Deploy.

### Tests (Pytest)

**Qué cubren**: los tests prueban que al registrar un pago quede en REGISTRADO y bien guardado; que pagar con tarjeta con monto chico termina en PAGADO; que con tarjeta y monto grande termina en FALLIDO; y que con PayPal y amount=4500 paga ok. Cada prueba arranca con el data.json vacío gracias al setup_function().

**Qué no cubren**: no hay caso de PayPal inválido (monto >= 5000), tampoco se prueba la regla de “hay más de un REGISTRADO con tarjeta” que debería fallar. No se testean los errores de flujo (cuando intentás update/pay/revert en estados que no corresponden) ni los 404 para IDs inexistentes. También faltan los casos felices de update y revert.

### Estrategia/Diseño

El trabajo está hecho en un monolito simple: una app de FastAPI que expone endpoints, aplica reglas y persiste en data.json. Consideramos que es funcional para los objetivos del examen por su simplicidad y facilidad de despliegue.

Si quisiéramos evolucionarlo, convendría modularizar el monolito: separar capas (API --> servicio/dominio --> repositorio), usar schemas Pydantic con bodies JSON, introducir un repositorio sobre una base de datos transaccional (p. ej. Postgres), aplicar DI para testear sin I/O, y patrones como Strategy (validación por método) y, si crecen los estados, State.