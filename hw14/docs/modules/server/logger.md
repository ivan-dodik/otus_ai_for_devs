# `logger.py` — Настройка логирования

## Назначение

Настройка структурированного логирования с использованием библиотеки `structlog`. Обеспечивает единообразный формат логов для всех компонентов сервера.

## Конфигурация

```python
def setup_logger(level: str = "INFO") -> structlog.stdlib.BoundLogger
```

**Параметры:**
- `level` — уровень логирования (DEBUG, INFO, WARNING, ERROR). По умолчанию `INFO`.

**Формат вывода:**
```
[timestamp  ] level event key1=value1 key2=value2
```

Пример:
```
[2026-05-28T01:00:00.000Z] info     tool_call tool=find_bcm_api params={"api": "bcm_vlan_create", "chip": "all"}
[2026-05-28T01:00:00.050Z] info     tool_result tool=find_bcm_api status=success elapsed_ms=50
```

## Использование

```python
from src.server.logger import setup_logger

logger = setup_logger("INFO")
logger.info("server_start", sdk_path="/path/to/sdk")
logger.error("index_error", error="File not found")
```

## Ключевые события логирования

| Событие | Уровень | Контекст |
|---------|---------|----------|
| `server_start` | INFO | sdk_path, cache_dir |
| `tool_call` | INFO | tool, params |
| `tool_result` | INFO | tool, status, elapsed_ms |
| `tool_result` (ошибка) | ERROR | tool, error, elapsed_ms |
| `index` (start) | INFO | status=starting |
| `index` (done) | INFO | functions, macros, modules, elapsed_ms |

## Преимущества structlog

- **Структурированные ключ-значение** — легко парсить и фильтровать
- **Автоматические временные метки** — ISO 8601 формат
- **Цветной вывод** — в терминале (при наличии tty)
- **Лёгкая интеграция** — с MCP сервером через стандартный `logging`