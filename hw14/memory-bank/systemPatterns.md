# System Patterns: OpenBCM Helper MCP Server

## Архитектура

```
┌──────────────┐     stdio      ┌──────────────────────┐
│   IDE Agent  │◄──────────────►│   MCP Server          │
│  (Cline/     │                │   (src/server/)       │
│   Continue)  │                │                        │
└──────────────┘                └──────────┬───────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
               ┌────▼────┐          ┌──────▼──────┐        ┌─────▼─────┐
               │  Tools  │          │   Search     │        │  Indexer  │
               │(src/    │          │  (src/search/)│        │(src/      │
               │ tools/) │          │              │        │ indexer/) │
               └────┬────┘          └──────┬───────┘        └─────┬─────┘
                    │                      │                      │
               ┌────▼────┐          ┌──────▼───────┐        ┌─────▼─────┐
               │ Models  │          │  Security     │        │  SQLite   │
               │(src/    │          │ (src/security/)│       │  cache/   │
               │ models/)│          │              │        │           │
               └─────────┘          └──────────────┘        └───────────┘
```

## Компоненты и их ответственность

### 1. Server Layer (`src/server/`)
- `mcp_server.py` — MCP сервер с stdio транспортом
- Регистрация всех 7 tools
- Логирование каждого вызова
- Инициализация зависимостей (PathGuard, ChipMap, SdkIndexer)
- `logger.py` — настройка structlog

### 2. Tools Layer (`src/tools/`)
Каждый tool — отдельный модуль с функцией, декорированной `@server.tool()`.
- Принимает параметры, валидированные Pydantic
- Вызывает search/indexer слой
- Возвращает структурированный JSON

### 3. Search Layer (`src/search/`)
- `rg_search.py` — обёртка над ripgrep (subprocess, whitelist только rg)
- `api_parser.py` — парсинг C-деклараций функций
- `macro_parser.py` — парсинг #define / #ifdef
- `cint_parser.py` — парсинг заголовков CINT скриптов

### 4. Indexer Layer (`src/indexer/`)
- `sdk_indexer.py` — индексация SDK в SQLite
- `chip_map.py` — загрузка маппинга чипов из JSON
- `schema.sql` — SQLite схема

### 5. Security Layer (`src/security/`)
- `path_guard.py` — PathGuard sandbox
- Защита от path traversal, symlink, доступ только внутри SDK_ROOT

### 6. Models Layer (`src/models/`)
- `schemas.py` — Pydantic модели для всех I/O контрактов
- Generic `ToolResult[T]` для единообразного ответа

## Паттерны проектирования

| Паттерн | Где используется |
|---------|-----------------|
| **Tool-ориентированная архитектура** | Каждый инструмент — отдельный модуль с единым интерфейсом |
| **Repository pattern** | SQLite как репозиторий для индекса функций |
| **Strategy pattern** | Разные парсеры (api_parser, macro_parser, cint_parser) |
| **Guard pattern** | PathGuard проверяет каждый путь |
| **Lazy Initialization** | Индексация SDK при первом вызове |
| **Result pattern** | ToolResult<T> с ok/error/meta |

## Критические пути выполнения

```
Запрос агента → MCP Transport (stdio)
  → Server._register_tools() определяет tool
  → Tool функция выполняется:
    1. Логирование вызова (имя, параметры)
    2. PathGuard.validate() для всех путей
    3. Поиск в индексе SQLite (если нужно)
    4. Fallback через rg (если индекс не дал результата)
    5. Парсинг результатов (api_parser, cint_parser)
    6. Формирование ToolResult
    7. Логирование завершения (статус, время)
  → JSON ответ → MCP Transport → Агент
```

## Поток данных

```
Client Request
  │
  ▼
MCP Server (stdio)
  │
  ▼
Tool Router (по имени инструмента)
  │
  ├──► ping → проверка SDK_PATH и индекса → ответ
  ├──► get_sdk_info → indexer.get_stats() → ответ
  ├──► find_bcm_api → indexer.search_api() + rg → ответ
  ├──► find_api_examples → rg_search() + cint_parser → ответ
  ├──► trace_api_implementation → rg_search() + macro_parser → ответ
  ├──► get_chip_info → chip_map + rg + indexer → ответ
  └──► find_cint_scripts → rg_search() + cint_parser → ответ
```

## Ссылки на документацию
- `docs/ARCHITECTURE.md` — Mermaid-диаграммы: общая архитектура, компоненты, sequence-диаграмма, ER-диаграмма БД, безопасность, трассировка
- `docs/modules/server/mcp_server.md` — детали реализации MCP сервера
- `docs/modules/indexer/schema.md` — ER-диаграмма SQLite
- `docs/modules/security/path_guard.md` — диаграмма безопасности PathGuard
