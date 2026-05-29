# LegalMove AI Agent

Sistema multi-agente para **LegalMove** (LegalTech) que compara contratos originales con sus enmiendas (adendas). Procesa imágenes escaneadas, transcribe el texto con **GPT-4o Vision** (sin OCR tradicional), alinea cláusulas entre documentos y devuelve un reporte estructurado validado con **Pydantic v2**. Toda la ejecución se observa en **Langfuse** con trazas jerárquicas.

## Problema de negocio

El equipo de Compliance dedica más de 40 horas semanales a comparar manualmente contratos y enmiendas. Este pipeline automatiza la extracción de cambios y reduce errores humanos.

## Arquitectura del pipeline

Flujo **secuencial y jerárquico** en cuatro fases:

```
Imagen original ──► parse_original_contract ──┐
                                            ├──► contextualization_agent ──► extraction_agent ──► JSON
Imagen enmienda ──► parse_amendment_contract ┘
```

| Fase | Componente | Responsabilidad |
|------|------------|-----------------|
| 1 | `image_parser.parse_contract_image` | Transcripción multimodal (Base64 + GPT-4o) |
| 2 | `ContextualizationAgent` | Mapa de alineación contextual (no extrae el JSON final) |
| 3 | `ExtractionAgent` | Cambios estructurados en `ContractChangeOutput` |
| 4 | `models.ContractChangeOutput` | Validación Pydantic del resultado |

### Esquema de salida (`ContractChangeOutput`)

```json
{
  "sections_changed": ["1. Plazo", "3. Pago"],
  "topics_touched": ["Vigencia", "Precio"],
  "summary_of_the_change": "Descripción ejecutiva de los cambios detectados."
}
```

### Observabilidad (Langfuse)

Cada ejecución genera una **traza raíz** `contract-analysis` con spans hijos:

```
contract-analysis
├── parse_original_contract
├── parse_amendment_contract
├── contextualization_agent
└── extraction_agent
```

Las llamadas a OpenAI se registran como generaciones anidadas (tokens, latencia, modelo).

## Stack técnico

| Requisito | Implementación |
|-----------|----------------|
| Modelo | GPT-4o (visión + razonamiento) |
| Validación | Pydantic v2 |
| Observabilidad | Langfuse SDK (Python) |
| Configuración | `python-dotenv` (sin API keys en código) |
| Extracción de texto | Solo visión multimodal — **prohibido OCR** (Tesseract, etc.) |

## Estructura del repositorio

```
├── data/
│   ├── test_contracts/      # Imágenes de prueba (.jpg)
│   └── e2e_results/         # Salidas JSON de pruebas E2E
├── docs/
│   └── E2E_PHASE6_REPORT.md
├── frontend/                  # SPA React + Vite + Tailwind
├── src/
│   ├── agents/
│   │   ├── contextualization_agent.py
│   │   └── extraction_agent.py
│   ├── api.py                 # API REST (FastAPI)
│   ├── image_parser.py
│   ├── models.py
│   └── main.py
├── run_e2e.py                 # Suite E2E sobre los 3 pares de prueba
├── .env.example
├── requirements.txt
└── README.md
```

## Requisitos previos

- Python 3.11+
- Node.js 18+ (solo para la interfaz web)
- Cuenta en [OpenAI](https://platform.openai.com/)
- Proyecto en [Langfuse Cloud](https://cloud.langfuse.com)

## Instalación

```bash
# Clonar e ingresar al directorio del proyecto
cd legalmove-ai-agent

# Crear y activar entorno virtual
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

# Dependencias
pip install -r requirements.txt

# Variables de entorno
cp .env.example .env
# Editar .env con tus claves reales
```

### Variables de entorno (`.env`)

| Variable | Descripción |
|----------|-------------|
| `OPENAI_API_KEY` | API key de OpenAI |
| `LANGFUSE_PUBLIC_KEY` | Clave pública del proyecto Langfuse |
| `LANGFUSE_SECRET_KEY` | Clave secreta del proyecto Langfuse |
| `LANGFUSE_HOST` | URL del host (por defecto `https://cloud.langfuse.com`) |

## Uso

### Análisis de un par de contratos

```bash
python -m src.main \
  --original data/test_contracts/documento_1__original.jpg \
  --amendment data/test_contracts/documento_1__enmienda.jpg
```

En Windows (PowerShell), con codificación UTF-8 en consola:

```powershell
$env:PYTHONIOENCODING = "utf-8"
python -m src.main --original data/test_contracts/documento_1__original.jpg --amendment data/test_contracts/documento_1__enmienda.jpg
```

### Suite E2E (3 pares de prueba)

```bash
python run_e2e.py
```

Guarda resultados en `data/e2e_results/` (`documento_1.json`, `documento_2.json`, `documento_3.json`, `summary.json`).

## Interfaz web

La interfaz explica el sistema, permite cargar el **contrato original** y la **enmienda** por separado, y muestra el reporte estructurado.

### Desarrollo (dos terminales)

**Terminal 1 — API (backend):**

```bash
uvicorn src.api:app --reload --port 8000
```

**Terminal 2 — Frontend (Vite con proxy a `/api`):**

```bash
cd frontend
npm install
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173). Las peticiones a `/api/*` se redirigen al backend en el puerto 8000.

### Producción (un solo servidor)

```bash
cd frontend
npm install
npm run build
cd ..
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Abre [http://localhost:8000](http://localhost:8000). FastAPI sirve el build de React y expone `POST /api/analyze`.

### Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/health` | Estado del servicio |
| `POST` | `/api/analyze` | Análisis (multipart: `original`, `amendment`) |

## Ejemplo de salida

```json
{
  "sections_changed": [
    "1. Otorgamiento de Licencia",
    "2. Plazo",
    "3. Pago"
  ],
  "topics_touched": [
    "Licencia",
    "Duración del Contrato",
    "Pago"
  ],
  "summary_of_the_change": "La enmienda extiende el plazo de 12 a 24 meses y aumenta la tarifa anual de USD 12,000 a USD 15,000."
}
```

El agente de extracción está configurado para **redactar siempre en español** (`sections_changed`, `topics_touched`, `summary_of_the_change`).

## Pruebas E2E

Resultados documentados en [`docs/E2E_PHASE6_REPORT.md`](docs/E2E_PHASE6_REPORT.md). Resumen:

| Par | Duración aprox. | Estado |
|-----|-----------------|--------|
| documento_1 | ~19 s | OK |
| documento_2 | ~15 s | OK |
| documento_3 | ~12 s | OK |

## Langfuse

Tras cada ejecución, revisa en el dashboard de Langfuse la traza `contract-analysis` y confirma la jerarquía de los cuatro spans. El pipeline invoca `langfuse.flush()` al finalizar para enviar los eventos pendientes.

## Notas de desarrollo

- `load_dotenv()` se ejecuta **antes** de importar Langfuse/OpenAI en `main.py`.
- No se usa `pymupdf` ni OCR clásico; solo imágenes `.jpg` / `.png` vía GPT-4o Vision.
- Para ampliar cobertura, agrega pares en `data/test_contracts/` y actualiza `TEST_PAIRS` en `run_e2e.py`.

## Licencia

Proyecto académico — AI Engineering (Henry) / LegalMove.
