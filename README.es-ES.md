

<p align="center">
  <h1 align="center">Idea Evolve</h1>
  <p align="center">
    <strong>Optimización evolutiva de código mediante sesiones de trabajo colaborativas de agentes de IA</strong>
  </p>
  <p align="center">
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+"></a>
    <a href="https://github.com/aleksanderborodin/idea_evolve/stargazers"><img src="https://img.shields.io/github/stars/aleksanderborodin/idea_evolve?style=social" alt="GitHub Stars"></a>
  </p>
</p>

Múltiples agentes de Claude especializados — arquitectos, exploradores, explotadores, investigadores — trabajan en paralelo a través de generaciones para evolucionar soluciones cada vez mejores a problemas de optimización complejos. Sin intervención humana. El sistema construye una base de conocimiento compartida que se vuelve más inteligente en cada generación.

> **Ejemplo de resultado:** Problema de conjuntos de Sidon (encontrar la secuencia B2 más grande en {0..10000}).
> Línea base voraz: **66 elementos**. Después de 7 generaciones de trabajo autónomo de agentes: **89 elementos** (+35%). Objetivo teórico: ~100.

![Dashboard Overview](images/overview.png)

## ¿Cómo Funciona?

Un orquestador sin estado ejecuta generaciones de agentes de IA. Cada generación:

```
Architect  ->  Agent Work  ->  Evaluator  ->  System Critic  ->  Consistency  ->  Finalize
 (plan)       (parallel AI      (score +       (diagnose         (audit           (rank +
               agents write      extract        pipeline          knowledge        update
               solutions)        knowledge)     issues)           base)            scores)
```

1. Un agente **Arquitecto** planifica la estrategia y asigna agentes especializados
2. **3-8 agentes** trabajan en paralelo — escribiendo soluciones, evaluándolas e iterando (40+ ciclos cada uno)
3. Un **Evaluador** extrae conocimiento (ideas, patrones, hechos) a una base de conocimiento compartida
4. Un **Crítico del Sistema** diagnostica problemas en el pipeline y recomienda mejoras
5. Un **Revisor de Consistencia** audita periódicamente la base de conocimiento
6. **Finalizar** actualiza clasificaciones, puntuaciones y detecta cualquier intervención manual

Todo el estado reside en archivos. Si el orquestador falla, reanuda exactamente desde donde se detuvo.

## Tipos de Agentes

| Agente | Rol |
|-------|------|
| **Explorar (Explore)** | Enfoques novedosos — estructuralmente diferentes de las soluciones existentes |
| **Explotar (Exploit)** | Refinar las mejores soluciones con mejoras específicas |
| **Genético (Genetic)** | Cruce: combinar fortalezas de dos soluciones padre |
| **Completo (Full)** | Autonomía total — leer todo, probar cualquier cosa |
| **Investigar (Research)** | Investigación matemática — leer artículos, derivar nuevos enfoques |
| **Experimentador (Experimentator)** | Crear utilidades auxiliares compartidas para todos los agentes |

## Inicio Rápido

### Requisitos Previos

- **Python 3.12+** — orquestador, panel de control, evaluación
- **Node.js 22+** — entorno de ejecución de la CLI de Claude Code (arnés predeterminado)
- **Clave API de Anthropic** — [console.anthropic.com](https://console.anthropic.com)
- *(opcional)* **[OpenCode](https://opencode.ai)** — arnés alternativo para enrutar agentes individuales a través de proveedores que no sean Anthropic (por ejemplo, vía ModelGate)

### Instalación

```bash
git clone https://github.com/aleksanderborodin/idea_evolve.git
cd idea_evolve

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Claude Code CLI (default harness)
npm install -g @anthropic-ai/claude-code

# (optional) OpenCode — only needed if you route any agent to the opencode harness
curl -fsSL https://opencode.ai/install | bash

# Secrets: store in .env at the repo root (gitignored)
cat > .env <<'EOF'
ANTHROPIC_API_KEY=sk-ant-...
# Only needed for the opencode harness via ModelGate:
MODELGATE_API_KEY=rp_...
MODELGATE_BASE_URL=https://api.modelgate.ru/v1
EOF

# Load secrets before running
set -a; source .env; set +a
```

### Ejecución

```bash
source venv/bin/activate
cd idea-evolve

# Start a new run on a problem
python3 orchestrator.py . --problem sidon --new-attempt --single

# Continue latest attempt (1 generation)
python3 orchestrator.py . --problem sidon --single

# Full run (all generations)
python3 orchestrator.py . --problem sidon

# Preview without launching agents
python3 orchestrator.py . --problem sidon --dry-run
```

Dos orquestadores pueden ejecutarse simultáneamente en problemas diferentes; cada uno trabaja en su propio directorio aislado.

## Arnaces (Harnesses): enrutamiento de agentes a diferentes CLIs

Cada sesión de agente se inicia a través de un **adaptador de arnés**. Hay tres integrados:

| Arnés | Binario | Alcance de proveedores |
|---|---|---|
| `claude-code` *(predeterminado)* | `npx @anthropic-ai/claude-code` | Anthropic (Claude) |
| `opencode` | `opencode run` | Cualquier proveedor soportado por opencode: Anthropic, OpenAI, Gemini, local o enrutado vía ModelGate |
| `codex` | `codex exec` | Modelos de OpenAI disponibles para tu CLI de Codex |

Todos los adaptadores exponen el mismo contrato `launch()` / `resume()`, por lo que la recuperación de resumen y informe después de un tiempo de espera funciona de manera idéntica. Los IDs de sesión de OpenCode y Codex se capturan desde eventos JSON en streaming; Claude Code acepta UUID asignados por el llamante. Detalles y pruebas de contrato: [idea-evolve/orchestrator_harness.py](idea-evolve/orchestrator_harness.py), [idea-evolve/tests/test_adapters.py](idea-evolve/tests/test_adapters.py).

### Selección de un arnés por agente

Edita [idea-evolve/user/config.yaml](idea-evolve/user/config.yaml):

```yaml
harnesses:
  default: claude-code        # or: opencode | codex
  per_agent: {}               # override by role — only list the EXCEPTIONS
                              # (listing a role whose harness == default is a no-op)
  per_model: {}               # optional model-tier routing, e.g. {opus: codex}

models:
  opencode:                   # alias → provider/model (only consulted by the opencode harness)
    opus:   modelgate/claude-sonnet-4-5
    sonnet: modelgate/minimax-m2.7
    haiku:  modelgate/minimax-m2.7
  codex:                      # alias → model id (only consulted by the codex harness)
    opus:   gpt-5.5
    sonnet: gpt-5.4
    haiku:  gpt-5.4-mini
  codex_reasoning_effort:     # optional alias → low | medium | high | xhigh
    opus: high
```

Orden de resolución en cada punto de lanzamiento: `per_agent[role]` → `per_model[model]` → `default` → `claude-code` (con advertencia para nombres desconocidos). Solo lista en `per_agent` los roles cuyo arnés difiere de `default`.

**Ejemplo A — mantener todo en Claude, enrutar exploradores solo a través de opencode:**

```yaml
harnesses:
  default: claude-code
  per_agent:
    explore: opencode
```

**Ejemplo B — cambiar el predeterminado a opencode, mantener solo el arquitecto en claude-code:**

```yaml
harnesses:
  default: opencode
  per_agent:
    architect: claude-code
```

**Ejemplo C — predeterminado a GLM vía OpenCode, enrutar `opus` a Codex con alto razonamiento:**

```yaml
architect_model: opus
default_model: sonnet

harnesses:
  default: opencode
  per_model:
    opus: codex

models:
  opencode:
    sonnet: zai/glm-5.1
  codex:
    opus: gpt-5.5
  codex_reasoning_effort:
    opus: high
```

**Notas sobre fidelidad.** OpenCode y Codex no tienen un equivalente a `--max-turns`; el tiempo de espera absoluto (wall-clock timeout) es el único límite (se registra una advertencia única por ejecución). Las plantillas de prompts de los agentes están optimizadas para Claude, por lo que enrutar `architect` o `evaluator` a un modelo que no sea Claude podría degradar la calidad del razonamiento; mantén esos en `claude-code` a menos que quieras validar específicamente lo contrario.

## Definir Tu Propio Problema

Crea un directorio en `problems/{your-problem}/` con:

| Archivo | Propósito |
|------|---------|
| `description.md` | Enunciado del problema y contexto |
| `constraints.md` | Restricciones estrictas que las soluciones deben cumplir |
| `evaluate.py` | Arnés de evaluación (almacena en caché los resultados por hash de contenido) |
| `validate.py` | Verificación de corrección — las soluciones inválidas obtienen puntuación centinela (0) |
| `metrics.yaml` | Dirección de aptitud (`higher_is_better` / `lower_is_better`), objetivo, decimales |
| `helpers/` | Funciones de utilidad compartidas disponibles para todos los agentes |
| `initial_programs/` | Soluciones base para sembrar la generación 0 |

Consulta los problemas existentes (`gemm`, `permcodes`, `sidon`) para ver ejemplos.

## Panel de Control (Dashboard)

```bash
source venv/bin/activate
python dashboard/app.py        # http://localhost:5000
```

El panel de control lee directamente desde el sistema de archivos; no hay base de datos. Detecta automáticamente todos los problemas e intentos.

| Pestaña | Qué muestra |
|-----|---------------|
| **Visión General** | Progresión de puntuación, línea temporal de generaciones, métricas clave, baliza de estado en vivo |
| **Pipeline** | Estado por agente (esperando/ejecutando/completado/fallido), flujo de datos entre fases |
| **Arquitectura** | Estructura del directorio de ejecución, jerarquía de conocimiento, ciclo de vida de las ideas |
| **Soluciones** | Tabla ordenable de cada solución evaluada, codificada por colores según validez |
| **Conocimiento** | Jerarquía de tres capas: Estado de los Hechos -> Clusters -> Ideas/Patrones/Hechos |
| **Informes** | Informes de cierre de agentes y retroalimentación del sistema por generación |

### Pipeline
![Pipeline](images/pipeline.png)

### Arquitectura
![Architecture](images/architecture.png)

### Soluciones
![Solutions](images/solutions.png)

### Conocimiento
![Knowledge](images/knowledge.png)

### Informes
![Reports](images/reports.png)

## Estructura del Proyecto

```
idea-evolve/
├── orchestrator.py          # Stateless main loop (~3200 lines)
├── agents/                  # Prompt templates (10 agent types)
├── prompts/                 # Shared prompt fragments
├── user/                    # config.yaml, initial_ideas.md
├── problems/                # Problem definitions (read-only at runtime)
│   ├── gemm/                #   Binary-ternary GEMM optimization
│   ├── permcodes/           #   Permutation codes M(n,d)
│   └── sidon/               #   Sidon sets (B2 sequences)
└── runs/                    # All evolution data, per problem + attempt
    └── {problem}/{attempt}/ #   population/, knowledge/, history/, reports/, ...

dashboard/                   # Flask web UI (reads filesystem, no database)
```

## Recuperación de Errores

Si el orquestador falla, simplemente reinicia con el mismo comando. Los agentes completados se omiten, los procesos huérfanos se eliminan y cada fase verifica la finalización antes de volver a ejecutarse. No se necesita limpieza manual.

## Contribuciones

¡Las contribuciones son bienvenidas! Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para ver las directrices sobre cómo agregar problemas, ampliar tipos de agentes y enviar cambios.

## Licencia

[MIT](LICENSE)

## Documentación

- [CLAUDE.md](CLAUDE.md) — Referencia operativa, todos los problemas conocidos, decisiones arquitectónicas
- [IDEA_EVOLVE_COMPLETE_V4.md](IDEA_EVOLVE_COMPLETE_V4.md) — Especificación completa del sistema
- [dashboard/README.md](dashboard/README.md) — Arquitectura del panel de control y puntos finales de la API
