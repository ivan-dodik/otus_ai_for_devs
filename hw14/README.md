# OpenBCM Helper MCP Server

MCP-сервер для навигации по OpenBCM SDK. Помогает AI-ассистентам (Cline, Continue, OpenCode) находить API, примеры использования, трассировать цепочки реализации, получать информацию о ASIC.

## Принципы MCP

**Как IDE/агент подключается к MCP-серверу.**  
IDE (Cline, Continue, OpenCode) запускает MCP-сервер как дочерний процесс через стандартный ввод/вывод (stdio). При старте сервер и клиент обмениваются инициализационными сообщениями: клиент запрашивает список инструментов через `list_tools`, сервер возвращает описание каждого инструмента (имя, описание, JSON Schema входных параметров). При вызове инструмента клиент отправляет `call_tool` с именем и аргументами, сервер выполняет логику и возвращает структурированный результат. Подключение настраивается через JSON-конфиг в IDE (например, `.vscode/mcp.json` или `~/.continue/config.json`), где указывается команда запуска и переменные окружения.

**Что считается «tool» в нашем сервере.**  
Каждый инструмент (tool) — это атомарная операция для работы с OpenBCM SDK: поиск API по имени, получение примеров использования, трассировка цепочки реализации, информация о чипе и т.д. Все инструменты принимают именованные параметры (строгая схема через JSON Schema) и возвращают структурированный JSON-ответ с полем `ok` (успех/ошибка), полем `result` (данные) и `meta` (время выполнения, источник). Инструменты реализуют **Project helper** и **Doc/Code context** подходы: они читают и анализируют локальные файлы SDK с ограничением доступа через PathGuard, а не выполняют произвольные команды.

## Архитектура

```
┌──────────────┐     stdio      ┌──────────────────────┐
│   IDE Agent  │◄──────────────►│   MCP Server          │
│  (Cline/     │                │   (src/server/)       │
│   Continue)  │                │                        │
└──────────────┘                └──────────┬───────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
               ┌────▼────┐          ┌──────▼──────┐        ┌─────▼─────┐
               │  Tools  │          │   Search     │        │  Indexer  │
               │(7 tools)│          │  (rg/parsers)│        │ (SQLite)  │
               └─────────┘          └─────────────┘        └───────────┘
```

## Инструменты (7)

| Tool | Описание | Ключевые параметры |
|------|----------|-------------------|
| `ping` | Health-check сервера | — |
| `get_sdk_info` | Информация о SDK | `include_modules` |
| `find_bcm_api` | Поиск декларации API | `api`, `chip`, `fuzzy` |
| `find_api_examples` | Поиск примеров использования | `api`, `source_type`, `max_results` |
| `trace_api_implementation` | Трассировка цепочки реализации | `api`, `chip`, `max_depth` |
| `get_chip_info` | Информация о ASIC | `chip`, `include_apis`, `include_cint_scripts` |
| `find_cint_scripts` | Поиск CINT скриптов | `query`, `chip`, `include_logs` |

## Быстрый старт

### Предварительные требования

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) — пакетный менеджер
- [ripgrep](https://github.com/BurntSushi/ripgrep) — текстовый поиск
- OpenBCM SDK

### Установка

```bash
# Клонирование
git clone <repo-url> openbcm-helper-mcp
cd openbcm-helper-mcp

# Установка зависимостей
uv venv
uv sync

# Настройка SDK
cp .env.example .env
# Отредактируйте .env: OPENBCM_SDK_PATH=/path/to/sdk
```

### Запуск и проверка

```bash
# Запуск сервера (сервер ждёт входящих сообщений по stdio)
OPENBCM_SDK_PATH=/path/to/sdk uv run python -m src

# В другом терминале — проверка через MCP Inspector:
npx @modelcontextprotocol/inspector uv run python -m src
```

После подключения к IDE отправьте запрос `ping` — сервер должен ответить статусом `ok`.

## Безопасность

- **Read-only:** сервер только читает файлы SDK
- **Sandbox:** все пути проходят через PathGuard.validate()
- **Subprocess whitelist:** разрешена только команда `rg`
- **Path traversal:** блокируются `..`, симлинки наружу, абсолютные пути вне SDK_ROOT

## Переменные окружения

| Переменная | Обязательность | Дефолт | Описание |
|------------|---------------|--------|----------|
| `OPENBCM_SDK_PATH` | Да | — | Путь к корню SDK |
| `OPENBCM_MCP_LOG_LEVEL` | Нет | INFO | Уровень лога |
| `OPENBCM_MCP_CACHE_DIR` | Нет | ./cache | Директория кэша |

## Структура проекта

```
src/
├── __main__.py           # Точка входа
├── config.py              # Конфигурация из env
├── server/
│   ├── mcp_server.py      # MCP сервер (stdio) + регистрация 7 tools
│   └── logger.py          # structlog
├── tools/                 # 7 инструментов
│   ├── ping.py
│   ├── get_sdk_info.py
│   ├── find_bcm_api.py
│   ├── find_api_examples.py
│   ├── trace_implementation.py
│   ├── get_chip_info.py
│   └── find_cint_scripts.py
├── search/                # Поисковые утилиты
│   ├── rg_search.py
│   ├── api_parser.py
│   ├── macro_parser.py
│   └── cint_parser.py
├── indexer/               # Индексация SDK
│   ├── sdk_indexer.py
│   ├── schema.sql
│   └── chip_map.py
├── security/
│   └── path_guard.py      # Sandbox
└── models/
    └── schemas.py          # Pydantic модели
```

## Подтверждения (ДЗ)

### 1. Реализован MCP-сервер
- **Файл:** `src/server/mcp_server.py`
  - Объявление 7 инструментов (интерфейс): `L37-L198`
  - Регистрация хендлеров `list_tools` / `call_tool`: `L225-L281`
  - Поднятие сервера через stdio транспорт: `L364-L377`
  - Логирование каждого вызова: `L238-L269` (имя, параметры, статус, время)

### 2. Реализованы инструменты
- `src/tools/ping.py:L1-L30` — health-check (30 строк)
- `src/tools/get_sdk_info.py:L1-L58` — информация о SDK (58 строк)
- `src/tools/find_bcm_api.py:L1-L96` — поиск API (96 строк)
- `src/tools/find_api_examples.py:L1-L149` — поиск примеров (149 строк)
- `src/tools/trace_implementation.py:L1-L153` — трассировка (153 строки)
- `src/tools/get_chip_info.py:L1-L108` — информация о чипе (108 строк)
- `src/tools/find_cint_scripts.py:L1-L145` — поиск CINT скриптов (145 строк)

Логирование каждого вызова: `src/server/mcp_server.py:L238-L269`
- L238-L245: лог вызова инструмента (имя + параметры)
- L251-L256: лог успешного выполнения
- L263-L269: лог ошибки выполнения
- Пример: `[info     ] tool_call tool=find_bcm_api params={"api": "bcm_vlan_create", "chip": "all"}`

### 3. Агент корректно вызывает нужный tool
- Фактическое подтверждение: `docs/INTEGRATION_LOGS.md` — 5 проверочных запросов, из которых **все 5 вызывают MCP-tool** (требуется минимум 3)
- Пример запроса: "Найди API bcm_vlan_create" → ожидаемый tool `find_bcm_api` → фактически вызван и вернул сигнатуру `int bcm_vlan_create(int unit, bcm_vlan_t vid)` (подробнее в `docs/INTEGRATION_LOGS.md`)

### 4. Контракты результатов
- `docs/CONTRACT.md` — описание единого формата ответа:
  ```json
  {
    "ok": true/false,
    "result": { ... },
    "error": "сообщение об ошибке (если ok=false)",
    "meta": { "elapsed_ms": 45, "source": "sqlite|ripgrep|config|internal" }
  }
  ```
  Детальные контракты для каждого из 7 инструментов — в `docs/CONTRACT.md`

### 5. Интеграция с IDE
- Cline: `.vscode/mcp.json`
- Continue: `docs/continue.json.example`
- OpenCode: `docs/opencode.json.example`
- Инструкция: `docs/SETUP.md`

## Управление проектом

Скрипт `run.sh` позволяет управлять проектом одной командой:

| Команда | Описание |
|---------|----------|
| `./run.sh` или `./run.sh start` | Запуск MCP-сервера |
| `./run.sh stop` | Остановка сервера |
| `./run.sh clean` | Полная очистка (venv, кэш, артефакты сборки) |
| `./run.sh restart` | Остановка → очистка → запуск |

Примеры:
```bash
# Запуск сервера
./run.sh

# Перезапуск с полной очисткой
./run.sh restart
```

При запуске скрипт проверяет наличие `.env` и переменной `OPENBCM_SDK_PATH`.

## Тестирование

```bash
uv run pytest tests/ -v
```

23 теста: security (8), cint_parser (7), macro_parser (3), e2e (5).

## Инструменты разработчика

| Инструмент | Команда | Описание |
|-----------|---------|----------|
| ruff | `make lint` | Линтер и форматтер |
| mypy | `make typecheck` | Проверка типов |
| pytest-cov | `make coverage` | Покрытие кода |
| hatchling | — | Build backend |

```bash
# Установка зависимостей разработчика
uv sync --group dev

# Быстрые команды
make lint      # ruff check
make format    # ruff format
make typecheck # mypy
make test      # pytest
make coverage  # pytest с отчётом о покрытии
make clean     # очистка venv, кэша, *.db, __pycache__
```

## SDK archive

Архив SDK на котором проверялась работа приложен в многотомном ZIP-архиве: [sdk-6.5.27.zip](./sdk-6.5.27.zip).

## Лицензия

GPLv3