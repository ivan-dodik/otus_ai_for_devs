# `mcp_server.py` — MCP сервер

## Назначение

Главный модуль сервера, реализующий MCP-протокол. Содержит класс `OpenBcmMcpServer`, который:
- Регистрирует 7 инструментов через `list_tools` / `call_tool` хендлеры
- Диспетчеризирует вызовы к соответствующим функциям инструментов
- Обеспечивает ленивую индексацию SDK
- Логирует каждый вызов (имя, параметры, статус, время выполнения)

## Класс `OpenBcmMcpServer`

### Конструктор

```python
def __init__(self, settings: Settings, logger) -> None
```

**Параметры:**
- `settings` — объект `Settings` с конфигурацией из переменных окружения
- `logger` — настроенный логгер (structlog)

**Инициализация:**
- Создаёт MCP Server с именем `"openbcm-helper"`
- Инициализирует `PathGuard` с путём к SDK
- Загружает `ChipMap` из `config/chip_map.json`
- Создаёт `SdkIndexer` для индексации SDK
- Регистрирует хендлеры `list_tools` и `call_tool`

### Методы

| Метод | Описание |
|-------|----------|
| `_register_handlers()` | Регистрирует `handle_list_tools` и `handle_call_tool` |
| `_dispatch_tool(tool_name, arguments)` | Вызывает функцию соответствующего инструмента |
| `_ensure_indexed()` | Запускает индексацию SDK при первом вызове |
| `run()` | Запускает сервер через stdio транспорт |

### Определения инструментов

Константа `TOOL_DEFINITIONS: list[Tool]` содержит описание всех 7 инструментов:

| Инструмент | Описание | Обязательные параметры |
|-----------|----------|----------------------|
| `ping` | Health-check сервера | — |
| `get_sdk_info` | Информация о SDK | — |
| `find_bcm_api` | Поиск декларации API | `api` |
| `find_api_examples` | Поиск примеров использования | `api` |
| `trace_api_implementation` | Трассировка цепочки реализации | `api` |
| `get_chip_info` | Информация о ASIC | `chip` |
| `find_cint_scripts` | Поиск CINT скриптов | `query` |

### Обработка вызова инструмента

```python
@self.server.call_tool()
async def handle_call_tool(tool_name: str, arguments: dict) -> CallToolResult
```

1. Засекает время начала
2. Логирует вызов: `info("tool_call", tool=tool_name, params=arguments)`
3. Вызывает `_dispatch_tool(tool_name, arguments)`
4. Логирует результат: `info("tool_result", status, elapsed_ms)`
5. Возвращает `CallToolResult` с JSON-ответом
6. При ошибке логирует `error("tool_result", error)` и возвращает ошибку

### Диспетчеризация

```python
async def _dispatch_tool(self, tool_name: str, arguments: dict) -> dict
```

- `ping`, `get_sdk_info`, `find_bcm_api` — требуют индексации (`_ensure_indexed()`)
- `find_api_examples`, `trace_api_implementation`, `get_chip_info`, `find_cint_scripts` — работают напрямую через ripgrep

### Запуск сервера

```python
async def run(self) -> None:
    async with stdio_server() as (read_stream, write_stream):
        await self.server.run(read_stream, write_stream, ...)
```

Сервер запускается через `stdio_server()` — читает из stdin, пишет в stdout.