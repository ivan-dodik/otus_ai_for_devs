# Coding Standards: LangChain Anime Recommendation Agent

## Python Style
- **Python 3.10+** with type hints for all function signatures
- Follow PEP 8 — use 4 spaces for indentation
- Maximum line length: 100 characters

## Naming Conventions
- **Files:** `snake_case.py` (e.g., `kitsu_tools.py`, `session_store.py`)
- **Functions:** `snake_case` (e.g., `search_anime()`, `process_query()`)
- **Classes:** `PascalCase` (e.g., `MemorySaver`, `ConversationBufferMemory`)
- **Constants:** `UPPER_CASE` (e.g., `OLLAMA_BASE_URL`, `FLASK_PORT`)
- **Modules:** short, descriptive lowercase names (e.g., `tools/`, `agent/`, `web/`)

## Imports
Order imports in groups:
1. Standard library (e.g., `os`, `sys`, `logging`)
2. Third-party libraries (e.g., `langchain`, `flask`, `requests`)
3. Local application modules (e.g., `config`, `tools`, `agent`)

Separate groups with a blank line.

Example:
```python
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from langchain.agents import create_react_agent
from langchain_ollama import ChatOllama

from config import config
```

## Docstrings
All functions must have docstrings in Russian or English (consistent within project):
```python
def search_anime(query: str) -> dict:
    """Поиск аниме по названию или ключевым словам.
    
    Args:
        query: Название аниме или ключевые слова для поиска
        
    Returns:
        dict: {"status": "success"|"error", "data": ..., "action": ..., "errors": ...}
    """
```

## Logging
- Use Python `logging` module, not `print()`
- Debug output: `logger.debug()` — hidden behind `--debug` flag
- Info level: `logger.info()` for normal operation
- Warning level: `logger.warning()` for recoverable issues
- Error level: `logger.error()` for failures

```python
import logging
logger = logging.getLogger(__name__)
```

## Error Handling
- All external calls (API, LLM) wrapped in try/except
- Tools return structured error dicts: `{"status": "error", "data": None, "action": "...", "errors": "..."}`
- Never expose raw exception messages to the user

## Tools Pattern
```python
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Описание инструмента на русском."""
    logger.debug(f"my_tool called with param={param}")
    try:
        result = api_call(param)
        return json.dumps({"status": "success", "data": result, "action": "...", "errors": "нет"})
    except Exception as e:
        return json.dumps({"status": "error", "data": None, "action": "...", "errors": str(e)})
```

## Configuration
- Environment variables via `python-dotenv`
- All config accessed through `config.py` module
- Never hardcode sensitive values
- Document all env vars in `.env.example`