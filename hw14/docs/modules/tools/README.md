# Модуль инструментов (`src/tools/`)

## Назначение

Модуль содержит реализацию 7 инструментов MCP-сервера. Каждый инструмент — отдельный файл с функцией, вызываемой из `mcp_server.py`.

## Инструменты

| # | Файл | Инструмент | Назначение |
|---|------|-----------|-----------|
| 1 | `ping.py` | `ping` | Health-check сервера |
| 2 | `get_sdk_info.py` | `get_sdk_info` | Информация о SDK |
| 3 | `find_bcm_api.py` | `find_bcm_api` | Поиск декларации API |
| 4 | `find_api_examples.py` | `find_api_examples` | Поиск примеров использования |
| 5 | `trace_implementation.py` | `trace_api_implementation` | Трассировка цепочки реализации |
| 6 | `get_chip_info.py` | `get_chip_info` | Информация о ASIC |
| 7 | `find_cint_scripts.py` | `find_cint_scripts` | Поиск CINT скриптов |

## Общий паттерн

Каждый инструмент следует единому паттерну:

```python
async def run_<tool_name>(params...) -> dict:
    start = time.time()
    # ... логика инструмента ...
    return ToolResult(
        ok=True,
        result=result.model_dump(),
        meta=ToolMeta(elapsed_ms=..., source=...),
    ).model_dump()
```

- Все функции асинхронные
- Принимают именованные параметры (валидируются Pydantic через MCP SDK)
- Возвращают `dict` в формате `ToolResult`
- Включают мета-информацию: время выполнения, источник данных

## Источники данных

| Инструмент | Основной источник | Fallback |
|-----------|------------------|----------|
| `ping` | Внутреннее состояние | — |
| `get_sdk_info` | SQLite (SdkIndexer) | — |
| `find_bcm_api` | SQLite (SdkIndexer) | ripgrep + fuzzy search |
| `find_api_examples` | ripgrep | — |
| `trace_api_implementation` | ripgrep | — |
| `get_chip_info` | ChipMap (JSON) + ripgrep | — |
| `find_cint_scripts` | ripgrep | — |

## Диаграмма зависимостей

```mermaid
graph TD
    subgraph Tools["src/tools/"]
        PING["ping.py"]
        SDKINFO["get_sdk_info.py"]
        BCMAPI["find_bcm_api.py"]
        EXAMPLES["find_api_examples.py"]
        TRACE["trace_implementation.py"]
        CHIPINFO["get_chip_info.py"]
        CINT["find_cint_scripts.py"]
    end

    subgraph Dependencies["Зависимости"]
        IDX["indexer/sdk_indexer.py"]
        CM["indexer/chip_map.py"]
        RG["search/rg_search.py"]
        CP["search/cint_parser.py"]
        MP["search/macro_parser.py"]
        AP["search/api_parser.py"]
        MOD["models/schemas.py"]
    end

    PING --> MOD
    SDKINFO --> IDX
    SDKINFO --> MOD
    BCMAPI --> IDX
    BCMAPI --> MOD
    EXAMPLES --> RG
    EXAMPLES --> CP
    EXAMPLES --> MOD
    TRACE --> RG
    TRACE --> MP
    TRACE --> MOD
    CHIPINFO --> CM
    CHIPINFO --> RG
    CHIPINFO --> CP
    CHIPINFO --> MOD
    CINT --> RG
    CINT --> CP
    CINT --> MOD