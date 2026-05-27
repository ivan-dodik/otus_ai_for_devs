# Модуль сервера (`src/server/`)

## Назначение

Модуль сервера реализует MCP-протокол через stdio-транспорт. Он отвечает за:
- Регистрацию всех 7 инструментов (tools)
- Обработку входящих запросов (`list_tools`, `call_tool`)
- Логирование каждого вызова инструмента
- Инициализацию зависимостей (PathGuard, ChipMap, SdkIndexer)
- Ленивую индексацию SDK при первом вызове

## Файлы модуля

| Файл | Назначение |
|------|-----------|
| `__init__.py` | Пакетный инициализатор |
| `mcp_server.py` | MCP сервер: регистрация хендлеров, диспетчеризация инструментов |
| `logger.py` | Настройка структурированного логирования (structlog) |

## Диаграмма зависимостей

```mermaid
graph TD
    MS["mcp_server.py<br/>OpenBcmMcpServer"] --> PG["security/path_guard.py<br/>PathGuard"]
    MS --> CM["indexer/chip_map.py<br/>ChipMap"]
    MS --> SI["indexer/sdk_indexer.py<br/>SdkIndexer"]
    MS --> LG["logger.py<br/>Logger"]
    MS --> T1["tools/ping.py"]
    MS --> T2["tools/get_sdk_info.py"]
    MS --> T3["tools/find_bcm_api.py"]
    MS --> T4["tools/find_api_examples.py"]
    MS --> T5["tools/trace_implementation.py"]
    MS --> T6["tools/get_chip_info.py"]
    MS --> T7["tools/find_cint_scripts.py"]
```

## Поток данных

```mermaid
sequenceDiagram
    participant Client as IDE Agent
    participant Server as OpenBcmMcpServer
    participant Logger as Logger
    participant Tool as Tool Function

    Client->>Server: list_tools
    Server-->>Client: TOOL_DEFINITIONS (7 tools)

    Client->>Server: call_tool(name, arguments)
    Server->>Logger: info("tool_call", tool, params)
    Server->>Server: _dispatch_tool(name, arguments)
    Server->>Tool: вызов функции инструмента
    Tool-->>Server: dict (ToolResult)
    Server->>Logger: info("tool_result", status, elapsed_ms)
    Server-->>Client: CallToolResult (JSON)

    alt ошибка
        Server->>Logger: error("tool_result", error)
        Server-->>Client: CallToolResult (error)
    end