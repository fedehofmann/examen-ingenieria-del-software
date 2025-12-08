# Examen Ingeniería de Datos

## **Integrantes**

* **Matías Caccia**
* **Federico Hofmann**
* **Sebastián Mesch Henriques**

---

# **1. Descripción general**

Este proyecto implementa una **API REST para gestionar pagos**, desarrollada en **FastAPI (Python 3.11)**.
La API permite:

* Registrar pagos
* Actualizar pagos (si están en estado REGISTRADO)
* Ejecutar validaciones y marcar como PAGADO o FALLIDO
* Revertir pagos FALLIDO → REGISTRADO
* Persistir información de manera simple mediante un archivo JSON

Incluye además:

* Tests unitarios con Pytest
* Pipeline de **CI/CD** con GitHub Actions
* Deploy automático mediante Render
* Documentación extendida sobre diseño, patrones, decisiones y arquitectura

El objetivo es demostrar criterios profesionales de diseño, colaboración y desarrollo de software.

---

# **2. Arquitectura general**

El proyecto mantiene una **estructura monolítica**, pero organizada de manera clara:

```
/
│ main.py                → Lógica de API, validación y persistencia
│ data.json              → Persistencia simple para pruebas
│ requirements.txt       → Dependencias
│ README.md              → Documentación del proyecto
│
└── tests/
       test_payments.py
└── .github/workflows/
       ci-cd.yml
```

La API es completamente funcional sin necesidad de servicios externos, lo cual permite centrarse en patrones, pruebas y CI/CD.

---

# **3. Decisiones de diseño — Justificación técnica**

A continuación se detallan las decisiones más relevantes y los motivos detrás de cada una, tal como requiere el examen.

## **3.1 Persistencia en JSON (trade-offs)**

Se eligió un archivo `data.json` para persistir el estado por las siguientes razones:

### Ventajas

* Simplicidad total del setup (sin instalar Postgres ni SQLite).
* Facilita el testing al manipular el estado rápidamente.
* Reduce ruido ajeno al objetivo del examen (enfocado en diseño, CI/CD y patrones).

### ✘ Desventajas

* No soporta concurrencia ni escalabilidad.
* No hay transacciones reales.
* Riesgo de corrupción si múltiples procesos escriben simultáneamente.

## **3.2 Manejo de estados con lógica explícita**

El flujo del pago requiere transiciones muy concretas. Decidimos representarlas con un pequeño “state machine conceptual” sin separar en módulos (manteniendo monolito). Esto permite cumplir la consigna sin sobreingeniería, pero dejando documentado que existe un modelo de estados bien definido.

## **3.3 Patrones de diseño aplicados**

Aunque el examen no requería reescribir todo el monolito, sí exige **comprender e implementar patrones** cuando corresponde. Por eso se extendió el razonamiento y la documentación del diseño actual, justificando por qué estos patrones serían adecuados **si el sistema creciera**.

---

### **Strategy Pattern**

Cada método de pago (CREDIT_CARD, PAYPAL) tiene reglas distintas. El patrón Strategy permite encapsularlas y evitar if/else anidados.

**Reglas implementadas:**

| Método      | Condición                                                     |
| ----------- | ------------------------------------------------------------- |
| CREDIT_CARD | amount < 10000 AND no más de 1 pago REGISTRADO usando tarjeta |
| PAYPAL      | amount < 5000                                                 |

### Justificación

* Aísla la lógica por método.
* Facilita agregar nuevos métodos sin modificar el endpoint.
* Permite testear validaciones sin tocar la API.

---

## **3.4 Parámetros como query params**

Se respetó lo dado en la consigna:

```
/payments/{payment_id}?amount=100&payment_method=CREDIT_CARD
```

### Justificación

* Es el formato mostrado en el enunciado.
* Evita necesidad de modelos Pydantic para request bodies.
* Simplifica el código al reducir validación y parsing.

---

# **4. Endpoints**

(Simplificados aquí; la lista completa está en el enunciado)

| Endpoint                | Método | Descripción                   |
| ----------------------- | ------ | ----------------------------- |
| `/payments`             | GET    | Lista todos los pagos         |
| `/payments/{id}`        | POST   | Registra un pago              |
| `/payments/{id}/update` | POST   | Actualiza un pago REGISTRADO  |
| `/payments/{id}/pay`    | POST   | Ejecuta validación y paga     |
| `/payments/{id}/revert` | POST   | Revertir FALLIDO → REGISTRADO |

---

# **5. Estrategia de testing**

La suite de tests cubre:

### Casos positivos:

* Registro de pagos
* Pago válido con tarjeta
* Pago válido con PayPal
* Update en estado permitido
* Revert correcto

### Casos negativos:

* Pago PayPal inválido
* Regla de “más de 1 crédito REGISTRADO”
* Updates no permitidos
* Revert no permitido
* IDs inexistentes en cada endpoint

Esto demuestra:

* Comprensión de reglas del dominio
* Cobertura completa de bifurcaciones
* Validación de errores HTTP 400 / 404
* Testing de estado persistido

---

# **6. CI/CD**

El flujo está implementado con GitHub Actions:

## Continuous Integration (CI)

Cada **Pull Request hacia main** ejecuta:

* Setup de Python 3.11
* Instalación de dependencias
* Ejecución de toda la suite de tests

Esto impide merges que rompan el sistema.

## Continuous Deployment (CD)

* La rama `production` está conectada a Render.
* Cuando hay un push o merge a `production`, el deploy es automático.
* El workflow aclara que el deploy lo realiza Render (no el workflow).

### Justificación

* Separación clara entre versiones en desarrollo (`main`) y releases productivos (`production`).
* Evita deploys accidentales.
* Cumple exactamente los requisitos del examen.

---

# **7. Cómo correr el proyecto localmente**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

# **8. Suposiciones tomadas**

* Los métodos de pago disponibles son solo **CREDIT_CARD** y **PAYPAL**.
* `payment_id` es string único por pago.
* No existe concurrencia de escritura en `data.json`.
* Todas las validaciones se ejecutan en memoria.
* Los parámetros vienen por Query (según consigna), no por body.

---

# 🚀 **9. Limitaciones y mejoras futuras**

Aunque la consigna exige un monolito simple, algunas mejoras posibles a contemplar:

### Migrar JSON → Base de datos (SQLite / Postgres)

### Separar en capas (API / Servicios / Dominio / Persistencia)

### Implementar Strategy y State en archivos dedicados

### Incorporar logs estructurados

### Test de integración con cliente HTTP real

### Manejo de concurrencia en las escrituras
