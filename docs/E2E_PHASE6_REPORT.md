# Fase 6 — Reporte E2E (LegalMove)

**Fecha:** 2026-05-26  
**Entorno:** Windows, Python 3.11.9, venv local  
**Modelo:** GPT-4o (visión + agentes)

## Objetivo

Validar el pipeline completo contra los 3 pares de imágenes en `data/test_contracts/`, verificando:

- Ejecución sin errores de extremo a extremo
- Salida conforme al esquema `ContractChangeOutput` (Pydantic v2)
- Coherencia semántica de las extracciones
- Envío de trazas a Langfuse (flush exitoso)

## Comandos ejecutados

```bash
# Par individual
python -m src.main --original data/test_contracts/documento_1__original.jpg --amendment data/test_contracts/documento_1__enmienda.jpg

# Suite completa (reproducible)
python run_e2e.py
```

## Resultados

| Par | Duración | Secciones detectadas | Estado |
|-----|----------|----------------------|--------|
| documento_1 | 19.2 s | 6 | OK |
| documento_2 | 15.0 s | 4 | OK |
| documento_3 | 11.6 s | 3 | OK |

Artefactos guardados en `data/e2e_results/`:

- `documento_1.json`, `documento_2.json`, `documento_3.json`
- `summary.json`

## Validación por caso

### documento_1 — Licencia de software

- **Tipo:** Contrato de licencia + enmienda
- **Cambios detectados:** licencia (elimina “intransferible”), plazo 12→24 meses, pago USD 12k→15k, soporte chat, terminación 30→60 días, nueva cláusula de protección de datos
- **Evaluación:** Coherente con un escenario típico de enmienda comercial/legal

### documento_2 — Servicios profesionales

- **Cambios detectados:** alcance (+ análisis regulatorio), duración 6→9 meses, honorarios USD 8k→9.5k, entregables (reportes quincenales), nueva cláusula de propiedad intelectual
- **Evaluación:** Identifica modificaciones sustantivas y temas comerciales correctos

### documento_3 — SaaS / servicio

- **Cambios detectados:** precio USD 1,200→1,250, SLA 99.5%→99.9%, soporte con ticketing online
- **Evaluación:** Resumen en inglés (documento posiblemente bilingüe); contenido técnicamente válido

## Criterios de aceptación (Fase 6)

| Criterio | Resultado |
|----------|-----------|
| Pipeline completa 4 fases sin excepción | Cumplido (3/3) |
| JSON con `sections_changed`, `topics_touched`, `summary_of_the_change` | Cumplido |
| Sin OCR tradicional (solo GPT-4o visión) | Cumplido |
| `langfuse.flush()` al finalizar | Cumplido |

## Pendiente manual (Fase 5 — auditoría Langfuse UI)

Revisar en [Langfuse Cloud](https://cloud.langfuse.com) que cada ejecución muestre:

```
contract-analysis
├── parse_original_contract
├── parse_amendment_contract
├── contextualization_agent
└── extraction_agent
```

Con generaciones OpenAI hijas (tokens/latencia) bajo los spans de parsing y agentes.

## Observaciones y mejoras sugeridas

1. **documento_3:** En la corrida inicial el resumen salió en inglés; se corrigió forzando español en `ExtractionAgent` (post-Fase 7).
2. **Consola Windows:** Usar `PYTHONIOENCODING=utf-8` para evitar caracteres corruptos en logs de terminal (los JSON en disco están correctos).
3. **`pymupdf`:** Eliminado de `requirements.txt` (no formaba parte del pipeline de imágenes).

## Siguiente fase

- Fase 7: Documentación (`README.md`)
- Fase 5 (cierre): Captura de pantalla o enlace de traza Langfuse para entrega académica
