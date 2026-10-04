# Alternativas gratuitas de LLM para CV Analyzer

## Objetivo

Para el proyecto **CV Analyzer with LLM**, la propuesta es implementar
una arquitectura de *fallback multi-provider* con 5 o 6 proveedores de
modelos de lenguaje. El sistema debería cambiar automáticamente de
proveedor cuando uno alcance su cuota, tenga un error o deje de estar
disponible.

No es necesario depender exclusivamente de OpenAI ni modificar la
arquitectura hexagonal actual.

Conviene separar dos conceptos:

-   **Proveedor:** Google, Groq, OpenRouter, Mistral, Cloudflare,
    Hugging Face, etc.
-   **Modelo:** Gemini, Llama, Qwen, DeepSeek, entre otros.

Así se puede cambiar de proveedor o de modelo sin modificar la lógica de
evaluación de CVs.

> Las cuotas, los modelos gratuitos y sus condiciones cambian con
> frecuencia. Antes de publicar la aplicación, hay que verificar los
> límites y términos vigentes de cada servicio.

## 1. Proveedores de LLM gratuitos

### 1. Google Gemini API

Una de las primeras opciones que evaluaría.

-   Cuenta con un nivel gratuito en Google AI Studio.
-   Modelos Gemini Flash y Flash-Lite adecuados para tareas de análisis
    de texto.
-   Buena capacidad para interpretar descripciones de puestos,
    requisitos y CVs.
-   SDK e integración con Python y LangChain.

La cuota depende del modelo y del proyecto. También hay que revisar las
condiciones de privacidad del nivel gratuito.

Sitio: <https://aistudio.google.com/>

### 2. GroqCloud

Una alternativa especialmente interesante por su velocidad.

-   Inferencia muy rápida.
-   Acceso a modelos abiertos, según disponibilidad.
-   API compatible con el formato de OpenAI.
-   Límites por modelo, solicitudes y tokens.

Es útil si se busca reducir el tiempo de procesamiento de muchos CVs. No
todos los modelos del catálogo son necesariamente gratuitos.

Sitio: <https://console.groq.com/>

### 3. OpenRouter

Permite acceder a múltiples modelos mediante una única API.

-   Diferentes proveedores y modelos.
-   Modelos con el sufijo `:free`.
-   API compatible con OpenAI.
-   Facilita probar modelos sin desarrollar un adaptador desde cero para
    cada uno.

Su principal desventaja es que las cuotas gratuitas pueden ser reducidas
y la disponibilidad puede cambiar. Lo usaría como proveedor alternativo,
no como único proveedor.

Sitio: <https://openrouter.ai/>

### 4. Mistral AI

Otra opción que vale la pena evaluar.

-   Modelos propios con buenas capacidades lingüísticas.
-   Modelos pequeños que pueden ser suficientes para clasificar y
    evaluar CVs.
-   API propia y SDK para Python.
-   Opciones de experimentación sujetas a restricciones.

Es interesante para comparar la calidad de las evaluaciones frente a
Gemini y Groq. Hay que revisar las condiciones de privacidad y los
límites vigentes.

Sitio: <https://console.mistral.ai/>

### 5. Cloudflare Workers AI

Una alternativa para diversificar los proveedores.

-   Acceso a modelos abiertos.
-   API y herramientas de integración.
-   Cuota gratuita medida en unidades de consumo llamadas *neurons*.
-   Posibilidad de integrar otros servicios de Cloudflare en el futuro.

La configuración y la medición de cuotas son diferentes a las de otros
proveedores. Lo consideraría como respaldo.

Sitio: <https://developers.cloudflare.com/workers-ai/>

### 6. Hugging Face

Una opción útil para experimentar con distintos modelos.

-   Gran catálogo de modelos abiertos.
-   Servicios de inferencia.
-   Crédito gratuito limitado en algunos planes.
-   Posibilidad de cambiar entre diferentes modelos.

No lo consideraría un respaldo garantizado: la cuota incluida es
limitada y la disponibilidad depende del modelo y del servicio elegido.

Sitio: <https://huggingface.co/>

### Selección inicial sugerida

Empezaría evaluando:

1.  Gemini
2.  Groq
3.  OpenRouter
4.  Mistral
5.  Cloudflare Workers AI
6.  Hugging Face

Son opciones con características diferentes, aunque algunas tienen
límites más estrictos que otras.

## 2. Arquitectura de fallback

La arquitectura actual, basada en `CVEvaluatorService`,
`CVEvaluationChainPort` y `OpenAICVEvaluationChainAdapter`, ya ofrece
una buena base.

No haría que `CVEvaluatorService` conozca los seis proveedores ni
pondría la lógica de selección dentro de cada adaptador.

En su lugar, agregaría un componente que implemente el mismo puerto:
`FallbackCVEvaluationChainAdapter`.

``` mermaid
flowchart TD
    A["FastAPI Controller"] --> B["CVEvaluatorService"]
    B --> C["CVEvaluationChainPort"]
    C --> D["FallbackCVEvaluationChainAdapter"]
    D --> E["Provider 1: Gemini"]
    D --> F["Provider 2: Groq"]
    D --> G["Provider 3: OpenRouter"]
    D --> H["Provider 4: Mistral"]
    D --> I["Provider 5: Cloudflare"]
    D --> J["Provider 6: Hugging Face"]
    E --> K["LLM Response"]
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
```

El flujo sería:

1.  `CVEvaluatorService` solicita una evaluación.
2.  El adaptador de fallback consulta el primer proveedor habilitado.
3.  Si funciona, devuelve el resultado.
4.  Si se alcanza un límite de cuota, ocurre un timeout o el proveedor
    no está disponible, intenta con el siguiente.
5.  Si todos fallan, devuelve un error controlado.

Así, `CVEvaluatorService` no necesita saber qué proveedor terminó
procesando el CV.

### Estructura de directorios propuesta

``` text
src/
├── adapters/
│   ├── inbound/
│   │   └── api/
│   │
│   └── outbound/
│       └── llm/
│           ├── fallback_adapter.py
│           ├── gemini_adapter.py
│           ├── groq_adapter.py
│           ├── openrouter_adapter.py
│           ├── mistral_adapter.py
│           ├── cloudflare_adapter.py
│           └── huggingface_adapter.py
│
├── application/
│   └── services/
│       └── cv_evaluator_service.py
│
├── domain/
│   └── ports/
│       └── cv_evaluation_chain.py
│
└── infrastructure/
    └── config.py
```

Es una estructura orientativa. Si el proyecto ya tiene directorios para
prompts, cadenas de LangChain y modelos de dominio, conviene
conservarlos en lugar de duplicarlos.

## 3. Implementación del fallback

El puerto podría tener una interfaz como esta:

``` python
from typing import Protocol


class CVEvaluationChainPort(Protocol):

    async def evaluate(
        self,
        job_description: str,
        requirements: list[str],
    ) -> dict:
        ...
```

Cada adaptador implementaría ese contrato.

El componente de fallback recibiría una lista ordenada de
implementaciones del puerto y probaría cada una:

``` python
class FallbackCVEvaluationChainAdapter:

    def __init__(self, providers):
        self.providers = providers

    async def evaluate(
        self,
        job_description: str,
        requirements: list[str],
    ) -> dict:

        errors = []

        for provider in self.providers:
            try:
                return await provider.evaluate(
                    job_description=job_description,
                    requirements=requirements,
                )
            except RetryableLLMError as exc:
                errors.append(exc)

        raise AllProvidersUnavailable(errors)
```

`RetryableLLMError` y `AllProvidersUnavailable` son excepciones
ilustrativas que habría que definir en el proyecto.

No conviene capturar indiscriminadamente todas las excepciones y pasar
al siguiente proveedor. Por ejemplo, si el prompt está mal construido o
el esquema de respuesta es inválido, cambiar de proveedor puede ocultar
un error que debería corregirse.

### Clasificación de errores sugerida

  -----------------------------------------------------------------------
  Error                               Comportamiento
  ----------------------------------- -----------------------------------
  HTTP 429, cuota agotada             Pasar al siguiente proveedor

  HTTP 500, 502, 503                  Reintentar de forma limitada o
                                      pasar al siguiente

  Timeout                             Pasar al siguiente proveedor

  API key inválida                    Deshabilitar temporalmente ese
                                      proveedor y registrar el error

  Error de validación del prompt      No hacer fallback automáticamente

  Respuesta inválida                  Permitir un reintento limitado o
                                      probar otro proveedor

  Todos los proveedores fallaron      Devolver un error controlado
  -----------------------------------------------------------------------

Es importante evitar reintentos ilimitados. Si un proveedor está caído,
no conviene perder tiempo y recursos intentando conectarse
repetidamente.

## 4. Administración de cuotas

No todos los proveedores ofrecen un endpoint para consultar el saldo o
la cuota disponible. Algunos informan límites mediante cabeceras HTTP,
otros muestran datos en sus paneles y otros solo indican que se alcanzó
el límite cuando falla una petición.

Por eso, implementaría un `ProviderQuotaManager`.

Sus responsabilidades serían:

-   Llevar un registro de solicitudes y errores por proveedor.
-   Guardar los límites conocidos.
-   Leer las cabeceras de rate limit cuando estén disponibles.
-   Aplicar períodos de enfriamiento (*cooldown*) ante errores de cuota.
-   Evitar proveedores temporalmente inactivos.
-   Permitir configurar prioridades manualmente.

Ejemplo de estado ilustrativo:

  Proveedor        Prioridad Estado
  -------------- ----------- ------------------------
  Gemini                   1 Disponible
  Groq                     2 Disponible
  Mistral                  3 Límite alcanzado
  OpenRouter               4 Disponible
  Cloudflare               5 Temporalmente inactivo
  Hugging Face             6 Disponible

Esta tabla no representa información en tiempo real.

También se puede implementar un patrón *circuit breaker*. Cuando un
proveedor falla reiteradamente, se lo desactiva temporalmente. Pasado un
período, se prueba si volvió a estar disponible.

La recomendación es comenzar con prioridades fijas y un registro de uso.
Más adelante, con métricas suficientes, se puede incorporar una
selección dinámica.

## 5. Evitar consumir los créditos de OpenAI

Como ya existe una API key de OpenAI con saldo, tomaría una precaución
adicional:

**No incluiría OpenAI de pago en el fallback automático.**

Se puede conservar para pruebas y comparaciones, pero deshabilitar su
uso en el entorno público.

Por ejemplo:

``` env
ENABLE_OPENAI=false
ENABLE_GEMINI=true
ENABLE_GROQ=true
ENABLE_OPENROUTER=true
ENABLE_MISTRAL=true
ENABLE_CLOUDFLARE=true
ENABLE_HUGGINGFACE=true
```

También agregaría una lista de proveedores permitidos por entorno y
validaría que OpenAI no pueda activarse accidentalmente.

Esto es más seguro que confiar únicamente en la lógica de fallback.

## 6. Privacidad de los CVs

Un CV puede contener nombres, correos electrónicos, teléfonos,
direcciones, historial laboral y otros datos identificatorios.

Antes de publicar la aplicación, revisaría cuidadosamente las
condiciones de privacidad y retención de cada proveedor. Algunos
servicios gratuitos pueden tener condiciones de uso de datos distintas
de los planes comerciales.

También implementaría:

-   Anonimización de los CVs antes de enviarlos, cuando sea posible.
-   Eliminación de información sensible de los logs.
-   Gestión segura de las API keys.
-   Límites de solicitudes por usuario.
-   Protección contra solicitudes automatizadas abusivas.
-   Consentimiento informado sobre el procesamiento de datos por
    proveedores externos.

**No publiques ninguna API key en el frontend ni en el repositorio.**
Todas las llamadas a los modelos deben pasar por el backend.

## 7. Implementación por etapas

No intentaría integrar seis proveedores de golpe. Primero verificaría
que el mecanismo de fallback funcione correctamente con dos o tres.

### Etapa 1: Gemini + Groq

Implementar dos adaptadores concretos y el fallback. Validar que el
sistema pueda pasar de un proveedor al otro ante un error simulado de
cuota.

### Etapa 2: Mistral + OpenRouter

Incorporar otros dos proveedores. Comparar calidad de las evaluaciones,
velocidad y consistencia de las respuestas.

### Etapa 3: Administrador de cuotas

Agregar registro de consumo, detección de límites, *cooldown* y *circuit
breaker*.

### Etapa 4: Pruebas de calidad

Crear un conjunto de CVs de prueba y descripciones laborales con
resultados esperados. Evaluar qué tan bien puntúa cada modelo, si
justifica sus conclusiones y si genera respuestas estructuradas válidas.

### Etapa 5: Cloudflare + Hugging Face

Incorporar los proveedores de respaldo adicionales si las pruebas
muestran que aportan disponibilidad real y una calidad aceptable.

## 8. Recomendación final

Seis proveedores no significan necesariamente seis veces más capacidad.
Hay límites compartidos dentro de algunos ecosistemas, cuotas que pueden
cambiar y modelos que no ofrecen la misma calidad.

Por eso, medir el rendimiento real del conjunto de proveedores es mucho
más importante que simplemente acumular integraciones.

Para la arquitectura actual, elegiría estos componentes:

-   **`CVEvaluatorService`:** orquesta el caso de uso de evaluación.
-   **`CVEvaluationChainPort`:** define el contrato.
-   **Adaptadores específicos:** implementan las integraciones con cada
    proveedor.
-   **`FallbackCVEvaluationChainAdapter`:** administra la selección y
    los cambios entre proveedores.
-   **`ProviderQuotaManager`:** administra el estado y el uso de las
    cuotas.

Con este diseño, si mañana aparece un nuevo proveedor gratuito que
ofrece un modelo excelente, solo será necesario crear un nuevo adaptador
e incorporarlo al sistema, sin tocar la lógica de negocio.

Como estás usando LangChain, podés aprovechar sus integraciones para
simplificar la construcción de los modelos y las cadenas. Sin embargo,
mantendría la lógica de fallback fuera de LangChain, en la capa de
adaptadores. Así evitás que la lógica de negocio dependa de un mecanismo
de enrutamiento particular de una librería.
