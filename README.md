# Examen Ingeniería de Datos

## Integrantes

* Matías Caccia
* Federico Hofmann
* Sebastián Mesch Henriques

# 1. Descripción general

Este proyecto consiste en una API REST para la gestión de pagos, desarrollada con FastAPI (Python 3.11).
La API permite:

* Registrar nuevos pagos
* Actualizar pagos siempre que sigan en estado REGISTRADO
* Ejecutar validaciones y marcar un pago como PAGADO o FALLIDO
* Revertir pagos de FALLIDO → REGISTRADO
* Guardar el estado de manera simple usando un archivo JSON

Además, incluye:

* Tests unitarios con Pytest
* Pipeline de CI/CD implementado en GitHub Actions
* Deploy automatizado mediante Render
* Documentación sobre decisiones, diseño y patrones utilizados

El objetivo general es mostrar criterios profesionales de diseño y desarrollo, tanto a nivel técnico como organizacional.

# 2. Arquitectura general

El proyecto se mantiene dentro de una estructura monolítica, pero ordenada y fácil de navegar:

```
/
│ main.py                → Lógica principal de la API, validaciones y persistencia
│ data.json              → Archivo simple de almacenamiento
│ requirements.txt       → Dependencias del proyecto
│ README.md              → Documentación general
│
└── tests/
       test_payments.py
└── .github/workflows/
       ci-cd.yml
```

No depende de servicios externos, lo que facilita enfocarse en patrones, pruebas y CI/CD.

# 3. Decisiones de diseño — Justificación técnica

A continuación se detallan las decisiones más relevantes del proyecto y el porqué detrás de cada una.

## 3.1 Persistencia en JSON (trade-offs)

Se optó por un archivo `data.json` como mecanismo de persistencia.

### Ventajas

* Requiere cero configuración adicional.
* Permite manipular el estado para pruebas rápidamente.
* Evita complejidades externas al objetivo principal del examen.

### ✘ Desventajas

* No ofrece garantías de concurrencia ni escalabilidad.
* No existen transacciones reales.
* Ante múltiples escrituras simultáneas existe riesgo de corrupción de datos.

## 3.2 Manejo de estados con lógica explícita

El sistema requiere transiciones de estado muy concretas. Para mantener todo simple, se implementó una “máquina de estados” implícita dentro del propio monolito, sin dividir en módulos adicionales.
Esto mantiene el código accesible, pero deja claro que hay una lógica de estados bien definida.

## 3.3 Patrones de diseño aplicados

Aunque no era obligatorio reestructurar todo el monolito, la consigna pedía justificar decisiones y aplicar patrones cuando correspondiera. Por eso se documentó cómo ciertos patrones encajan en este tipo de problema y por qué son útiles si el proyecto creciera.

### Strategy Pattern

Se utiliza para encapsular las reglas de cada método de pago y evitar condicionales extensos.

Reglas actuales:

| Método      | Regla                                               |
| ----------- | --------------------------------------------------- |
| CREDIT_CARD | amount < 10000 y solo 1 pago REGISTRADO con tarjeta |
| PAYPAL      | amount < 5000                                       |

### Por qué es adecuado

* La lógica de validación queda separada por método.
* Permite sumar nuevos métodos sin tocar el endpoint.
* Facilita el testeo aislado de cada estrategia.

## 3.4 Parámetros como Query Params

Siguiendo exactamente la consigna, el formato utilizado es:

```
/payments/{payment_id}?amount=100&payment_method=CREDIT_CARD
```

### Motivos

* Es el ejemplo provisto en el enunciado.
* Evita necesidad de definir modelos Pydantic específicos.
* Mantiene el desarrollo simple para este examen.

# 4. Endpoints

Resumen (la lista completa figura en el enunciado):

| Endpoint                | Método | Descripción                   |
| ----------------------- | ------ | ----------------------------- |
| `/payments`             | GET    | Listar todos los pagos        |
| `/payments/{id}`        | POST   | Registrar un pago             |
| `/payments/{id}/update` | POST   | Modificar un pago REGISTRADO  |
| `/payments/{id}/pay`    | POST   | Validar y procesar un pago    |
| `/payments/{id}/revert` | POST   | Revertir FALLIDO → REGISTRADO |

# 5. Estrategia de testing

La suite de Pytest cubre tanto casos exitosos como fallos esperados.

### Casos positivos

* Registro de nuevos pagos
* Pagos válidos con tarjeta y PayPal
* Updates permitidos
* Reversiones correctas

### Casos negativos

* Reglas de validación que deben fallar
* Restricción de “solo un pago REGISTRADO” por tarjeta
* Updates no permitidos por estado
* Reversiones inválidas
* IDs inexistentes en todos los endpoints

Esto garantiza:

* Cobertura completa de las reglas del dominio
* Manejo adecuado de errores HTTP 400 / 404
* Validación del estado persistido

# 6. CI/CD

El pipeline está implementado mediante GitHub Actions.

## Continuous Integration (CI)

En cada Pull Request a main, se ejecuta:

* Setup de Python 3.11
* Instalación de dependencias
* Ejecución completa de tests

Esto evita merges que rompan la API.

## Continuous Deployment (CD)

* La rama `production` está conectada a Render.
* Cualquier push o merge a esa rama dispara un deploy automático.
* El workflow aclara explícitamente que el deploy final lo hace Render.

### Razones

* Se separa claramente el trabajo en desarrollo (`main`) del código listo para producción (`production`).
* Reduce errores humanos en el deployment.
* Cumple de forma precisa lo pedido en la consigna.

# 7. Cómo correr el proyecto localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

# 8. Suposiciones tomadas

* Solo existen los métodos de pago CREDIT_CARD y PAYPAL.
* `payment_id` se interpreta como un string único.
* No hay concurrencia en el acceso a `data.json`.
* Las validaciones se mantienen todas en memoria.
* Los parámetros llegan por query, tal como indica la consigna.

# 9. Limitaciones y posibles mejoras

Aunque la consigna plantea mantener un enfoque monolítico y sencillo, es posible identificar varias líneas de evolución que permitirían llevar el proyecto a un nivel más robusto y cercano a un entorno real.

### 9.1. Separar la arquitectura en capas (API / Servicios / Dominio)

La lógica del proyecto está actualmente centralizada para mantener simplicidad. Aun así, dividirla en capas permitiría:

* Encapsular reglas de negocio en un módulo dedicado (Dominio).
* Aislar la lógica de acceso a datos del resto del sistema (Persistencia).
* Mantener controladores del API más limpios y fáciles de leer.
* Facilitar testeo unitario sin necesidad de moquear todo el sistema.

Una arquitectura en capas también facilita el crecimiento y la colaboración entre desarrolladores.

### 9.2. Extraer Strategy y State a módulos independientes

Aunque los patrones están aplicados conceptualmente, se encuentran dentro del monolito. Llevarlos a módulos propios permite:

* Documentar explícitamente los comportamientos y transiciones.
* Hacer que la lógica de validación sea extensible simplemente agregando clases.
* Permitir que nuevos métodos o estados se implementen sin modificar código existente.
* Reforzar la separación de responsabilidades y mejorar testabilidad.

Esto también favorece la incorporación futura de comportamientos dinámicos o configurables.

### 9.3. Incorporar logs estructurados

El proyecto aún carece de un sistema de registro estructurado. Incluirlo aportaría:

* Trazabilidad clara de cada operación ejecutada.
* Diagnóstico más sencillo ante errores o comportamientos inesperados.
* Posibilidad de integrar herramientas de monitoreo o dashboards.
* Mejor comprensión del flujo en entornos productivos.

### 9.4. Incorporar tests de integración completos

* Validar el sistema como un todo, incluyendo rutas, parámetros y serialización.
* Detectar inconsistencias entre controladores y lógica interna.
* Garantizar que la API se comporte de acuerdo al contrato esperado por clientes externos.
* Aumentar la robustez del pipeline de CI.
