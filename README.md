# claude-code-api

Ejercicios del curso [Claude with the Anthropic API](https://anthropic.skilljar.com/claude-with-the-anthropic-api/287746), explorando el SDK de Anthropic en Python: mensajes básicos, chat con memoria, streaming, generación de datasets sintéticos y evaluación de prompts.

## Requisitos

- Python 3.14
- Una API key de Anthropic en un archivo `.env`:

```
ANTHROPIC_API_KEY=tu-api-key
```

## Instalación

```bash
pipenv install
```

## Archivos

| Archivo | Descripción |
|---|---|
| [claude_api.py](claude_api.py) | `ClaudeClient`, un wrapper reutilizable sobre el SDK de Anthropic (mensajes, system prompt, stop sequences). |
| [main.py](main.py) | Chatbot de consola con historial de mensajes; ejemplo de system prompt como tutor de matemáticas para kinder. |
| [stream.py](stream.py) | Ejemplo de respuesta en streaming con `client.messages.stream`. |
| [generate_dataset.py](generate_dataset.py) | Genera un dataset sintético de casos de prueba usando Claude, forzando salida JSON con "prefill" + `stop_sequences`. |
| [prompt-evaluation.py](prompt-evaluation.py) | Pipeline de evaluación de prompts: valida la salida por código (JSON/Python/regex) y por un segundo modelo como juez (LLM-as-judge), y promedia los scores. |
| [prompting_completed.py](prompting_completed.py) | Versión extendida de la evaluación de prompts, con generación de casos de prueba y ejecución concurrente. |

## Uso

```bash
python main.py
python stream.py
python generate_dataset.py
python prompt-evaluation.py
```
