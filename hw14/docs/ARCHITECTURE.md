# Архитектура OpenBCM Helper MCP Server

## Общее описание

**OpenBCM Helper MCP Server** — это MCP-сервер для навигации по OpenBCM SDK. Он помогает AI-ассистентам (Cline, Continue, OpenCode) находить API, искать примеры использования, трассировать цепочки реализации и получать информацию о доступности функций на разных ASIC.

Сервер реализует протокол MCP (Model Context Protocol) через stdio-транспорт и предоставляет 7 инструментов для работы с SDK.

---

## 1. Общая архитектура

```mermaid
graph TB
    subgraph IDE["IDE / AI Agent"]
        A1["Cline (VS Code)"]
        A2["Continue"]
        A3["OpenCode"]
    end

    subgraph MCP["MCP Server (Python)"]
        direction TB
        S["Server Layer<br/>src/server/mcp_server.py"]
        T["Tools Layer<br/>src/tools/ (7 tools)"]
        SR["Search Layer<br/>src/search/"]
        IX["Indexer Layer<br/>src/indexer/"]
        SG["Security Layer<br/>src/security/"]
        M["Models Layer<br/>src/models/"]
        CF["Config Layer<br/>src/config.py"]
    end

    subgraph SDK["OpenBCM SDK (локально)"]
        H["include/bcm/*.h<br/>Заголовочные файлы"]
        SRC["src/*.c<br/>Исходный код"]
        EX["src/examples/*.c<br/>CINT скрипты"]
    end

    subgraph CACHE["Кэш"]
        DB["SQLite index.db<br/>Индекс функций и макросов"]
    end

    IDE -- "stdio (stdin/stdout)" --> S
    S --> T
    T --> SR
    T --> IX
    T --> SG
    T --> M
    S --> CF
    IX --> DB
    SR -- "ripgrep (subprocess)" --> SDK
    IX --> SDK
    SG --> SDK
```

---

## 2. Sequence-диаграмма запроса

```mermaid
sequenceDiagram
    participant Agent as AI Agent (Cline)
    participant Server as MCP Server
    participant Tool as Tool Handler
    participant Indexer as SdkIndexer (SQLite)
    participant Search as rg_search (ripgrep)
    participant SDK as OpenBCM SDK

    Agent->>Server: list_tools
    Server-->>Agent: список 7 инструментов

    Agent->>Server: call_tool(name, params)
    Server->>Server: логирование вызова
    Server->>Tool: _dispatch_tool(name, params)

    alt требует индекс
        Tool->>Indexer: _ensure_indexed()
        Indexer->>SDK: сканирование .h файлов
        Indexer->>Indexer: парсинг деклараций
        Indexer->>Indexer: сохранение в SQLite
    end

    Tool->>Indexer: search_api(name, chip, fuzzy)
    alt найдено в индексе
        Indexer-->>Tool: результаты из SQLite
    else не найдено
        Tool->>Search: rg_search(pattern, path)
        Search->>SDK: subprocess rg --json
        SDK-->>Search: JSON-результаты
        Search-->>Tool: RgMatch[]
    end

    Tool->>Tool: парсинг результатов
    Tool->>Tool: формирование ToolResult
    Server->>Server: логирование завершения
    Server-->>Agent: CallToolResult (JSON)
```

---

## 3. Компонентная диаграмма модулей

```mermaid
classDiagram
    class OpenBcmMcpServer {
        +Server server
        +PathGuard path_guard
        +ChipMap chip_map
        +SdkIndexer indexer
        +_register_handlers()
        +_dispatch_tool()
        +_ensure_indexed()
        +run()
    }

    class PathGuard {
        +Path sdk_root
        +validate(path) Path
        +validate_absolute(path) Path
    }

    class ChipMap {
        +get_chip(name) dict
        +list_chips() list
        +get_feature_macros(chip) list
    }

    class SdkIndexer {
        +Path sdk_path
        +Path cache_dir
        +db_path
        +index() IndexStats
        +search_api(name, chip, fuzzy) list
        +get_stats() IndexStats
    }

    class RgSearch {
        +rg_search(pattern, path, ...) list~RgMatch~
        +rg_count(pattern, path) int
        +rg_files(pattern, path) list~Path~
    }

    class ApiParser {
        +parse_function_declaration(text) FunctionDecl
        +extract_doxygen_comment(lines, line) DocComment
        +extract_module(name) str
    }

    class MacroParser {
        +extract_macros(lines) list~MacroDef~
        +extract_chip_guards(lines, line) list
        +extract_chip_conditions(lines, line) list
    }

    class CintParser {
        +is_cint_script(file_path) bool
        +extract_script_header(file_path) str
        +parse_header_comment(comment) dict
        +extract_used_apis(file_path) list
    }

    class ToolResult {
        +bool ok
        +T result
        +str error
        +ToolMeta meta
    }

    OpenBcmMcpServer --> PathGuard
    OpenBcmMcpServer --> ChipMap
    OpenBcmMcpServer --> SdkIndexer
    SdkIndexer --> ApiParser
    SdkIndexer --> MacroParser
    SdkIndexer --> RgSearch
    SdkIndexer --> ChipMap
    Tools --> RgSearch
    Tools --> CintParser
    Tools --> MacroParser
    Tools --> ToolResult
```

---

## 4. ER-диаграмма SQLite

```mermaid
erDiagram
    functions {
        int id PK
        string name UK
        string signature
        string return_type
        string file_path
        int line
        int line_end
        string module
        string description
        string doc_comment
        string chip_macros
        timestamp indexed_at
    }

    function_params {
        int function_id FK
        int param_index
        string name
        string param_type
        string description
    }

    macros {
        int id PK
        string name UK
        string definition_file
        int definition_line
        string definition_value
        string chip_association
        string description
    }

    api_macros {
        string api_name PK
        string macro_name PK
    }

    functions ||--o{ function_params : "has"
    functions ||--o{ api_macros : "associated with"
    macros ||--o{ api_macros : "associated with"
```

---

## 5. Диаграмма безопасности (PathGuard)

```mermaid
flowchart TD
    REQ["Запрос к файлу SDK"] --> PG["PathGuard.validate(path)"]
    PG --> RESOLVE["(sdk_root / path).resolve()"]
    RESOLVE --> CHECK_START{"Начинается с<br/>sdk_root?"}
    CHECK_START -- "Нет" --> ERR1["SecurityError:<br/>Path traversal detected"]
    CHECK_START -- "Да" --> CHECK_SYMLINK{"Это симлинк?"}
    CHECK_SYMLINK -- "Да" --> ERR2["SecurityError:<br/>Symlinks not allowed"]
    CHECK_SYMLINK -- "Нет" --> CHECK_EXISTS{"Файл существует?"}
    CHECK_EXISTS -- "Нет" --> ERR3["FileNotFoundError"]
    CHECK_EXISTS -- "Да" --> OK["✅ Resolved Path"]
```

---

## 6. Диаграмма потока трассировки

```mermaid
flowchart TD
    API["trace_api_implementation(api='bcm_l2_addr_add')"] --> ESW["Поиск bcm_esw_l2_addr_add<br/>в src/"]
    ESW --> FOUND{"Найдена<br/>реализация?"}
    FOUND -- "Нет" --> FALLBACK["Поиск bcm_l2_addr_add<br/>в src/ (fallback)"]
    FOUND -- "Да" --> LEVEL1["Уровень 1: entry point"]
    LEVEL1 --> CHIP_COND{"Есть SOC_IS_*<br/>условия?"}
    CHIP_COND -- "Да" --> BRANCH["Создать ChipBranch"]
    CHIP_COND -- "Нет" --> NEXT_LEVEL
    BRANCH --> NEXT_LEVEL["Поиск _internal / _\w+<br/>функций (уровень 2)"]
    NEXT_LEVEL --> DEPTH{"Глубина < max_depth?"}
    DEPTH -- "Да" --> CHIP_COND
    DEPTH -- "Нет" --> RESULT["Формирование TraceResult"]
```

---

## 7. Принцип работы

### MCP протокол

1. **Инициализация**: IDE запускает MCP-сервер как дочерний процесс через stdio
2. **list_tools**: IDE запрашивает список доступных инструментов, сервер возвращает 7 инструментов с JSON Schema
3. **call_tool**: IDE вызывает инструмент с именем и параметрами, сервер выполняет логику и возвращает структурированный JSON

### Жизненный цикл запроса

1. **Логирование вызова** — имя инструмента, параметры (исключая чувствительные)
2. **Ленивая индексация** — при первом вызове `ping`, `get_sdk_info` или `find_bcm_api` запускается индексация SDK
3. **PathGuard** — все пути к файлам SDK проходят проверку безопасности
4. **Поиск** — сначала в SQLite-индексе, при отсутствии результатов — fallback через ripgrep
5. **Парсинг** — результаты обрабатываются парсерами (api_parser, macro_parser, cint_parser)
6. **Формирование ответа** — структурированный JSON с полями `ok`, `result`, `meta`
7. **Логирование завершения** — статус, время выполнения

### Безопасность

- **Read-only**: сервер только читает файлы SDK, никогда не пишет
- **Sandbox**: все пути проходят через `PathGuard.validate()`
- **Subprocess whitelist**: разрешена только команда `rg` (ripgrep)
- **Path traversal**: блокируются `..`, симлинки наружу, абсолютные пути вне SDK_ROOT

---

## 8. Технологический стек

| Компонент | Технология | Назначение |
|-----------|-----------|------------|
| Язык | Python 3.13+ | Основной язык |
| MCP протокол | `mcp` ≥1.0.0 | MCP Python SDK |
| Валидация | `pydantic` ≥2.0 | Схемы данных |
| Конфигурация | `pydantic-settings` ≥2.0 | Загрузка из env |
| Логирование | `structlog` ≥23.0 | Структурированное логирование |
| Нечёткий поиск | `rapidfuzz` ≥3.5 | Поиск по частичному совпадению |
| JSON | `orjson` ≥3.9 | Быстрая сериализация |
| БД | `sqlite3` (встроенный) | Лёгкий индекс SDK |
| Поиск | `ripgrep` (системный) | Быстрый текстовый поиск |
| Пакетный менеджер | `uv` | Управление зависимостями |
| Тестирование | `pytest` ≥8.0 | Unit + E2E тесты |

---

## 9. Переменные окружения

| Переменная | Обязательность | Дефолт | Описание |
|------------|---------------|--------|----------|
| `OPENBCM_SDK_PATH` | Да | — | Путь к корню SDK |
| `OPENBCM_MCP_LOG_LEVEL` | Нет | INFO | Уровень лога |
| `OPENBCM_MCP_CACHE_DIR` | Нет | ./cache | Директория кэша |

---

## 10. Структура проекта

```
src/
├── __main__.py              # Точка входа
├── __init__.py
├── config.py                 # Конфигурация из env (pydantic-settings)
├── server/
│   ├── __init__.py
│   ├── mcp_server.py         # MCP сервер (stdio) + регистрация 7 tools
│   └── logger.py             # structlog
├── tools/                    # 7 инструментов
│   ├── __init__.py
│   ├── ping.py               # Health-check
│   ├── get_sdk_info.py       # Информация о SDK
│   ├── find_bcm_api.py       # Поиск декларации API
│   ├── find_api_examples.py  # Поиск примеров использования
│   ├── trace_implementation.py # Трассировка цепочки реализации
│   ├── get_chip_info.py      # Информация о ASIC
│   └── find_cint_scripts.py  # Поиск CINT скриптов
├── search/                   # Поисковые утилиты
│   ├── __init__.py
│   ├── rg_search.py          # Обёртка над ripgrep
│   ├── api_parser.py         # Парсинг C-деклараций
│   ├── macro_parser.py       # Парсинг #define / #ifdef
│   └── cint_parser.py        # Парсинг CINT скриптов
├── indexer/                  # Индексация SDK
│   ├── __init__.py
│   ├── sdk_indexer.py        # Индексация в SQLite
│   ├── chip_map.py           # Маппинг чипов из JSON
│   └── schema.sql            # SQLite схема
├── security/
│   ├── __init__.py
│   └── path_guard.py         # Sandbox
└── models/
    ├── __init__.py
    └── schemas.py            # Pydantic модели