# План реализации: OpenBCM Helper MCP Server

> **Режим выполнения:** Act Mode (агент Cline)  
> **LLM:** deepseek-v4-flash  
> **Корневая директория:** `/home/ai/00/mcpserver`  
> **Python:** 3.13.7 | **Пакетный менеджер:** `uv`  
> **SDK (реальный):** `/home/ai/00/openbcm/sdk-6.5.27` (из переменной окружения `OPENBCM_SDK_PATH`)  
> **Всего инструментов:** 7 tools  
> **Всего шагов:** ~72  

---

## Структура проекта (итоговая)

```
openbcm-helper-mcp/
├── memory-bank/                  # Memory Bank Cline
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── activeContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   └── progress.md
├── src/
│   ├── __init__.py
│   ├── __main__.py               # Точка входа: python -m src
│   ├── config.py                 # Загрузка конфигурации из env
│   ├── server/
│   │   ├── __init__.py
│   │   ├── mcp_server.py         # MCP сервер (stdio), регистрация tools
│   │   └── logger.py             # Настройка structlog
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── ping.py               # TOOL 1: health-check
│   │   ├── get_sdk_info.py       # TOOL 2: информация о SDK
│   │   ├── find_bcm_api.py       # TOOL 3: поиск API
│   │   ├── find_api_examples.py  # TOOL 4: поиск примеров (C + CINT)
│   │   ├── trace_implementation.py  # TOOL 5: трассировка реализации
│   │   ├── get_chip_info.py      # TOOL 6: информация о чипе
│   │   └── find_cint_scripts.py  # TOOL 7: поиск CINT скриптов
│   ├── search/
│   │   ├── __init__.py
│   │   ├── rg_search.py          # Обёртка над ripgrep
│   │   ├── api_parser.py         # Парсинг деклараций C-функций
│   │   ├── macro_parser.py       # Парсинг #define / #ifdef
│   │   └── cint_parser.py        # Парсинг заголовков CINT скриптов
│   ├── indexer/
│   │   ├── __init__.py
│   │   ├── sdk_indexer.py        # Индексация SDK в SQLite
│   │   ├── schema.sql            # SQLite схема
│   │   └── chip_map.py           # Загрузка chip_map.json
│   ├── security/
│   │   ├── __init__.py
│   │   └── path_guard.py         # Sandbox: только SDK_PATH
│   └── models/
│       ├── __init__.py
│       └── schemas.py            # Pydantic модели для I/O
├── tests/
│   ├── __init__.py
│   ├── test_security.py
│   ├── test_find_bcm_api.py
│   ├── test_find_api_examples.py
│   ├── test_trace_implementation.py
│   ├── test_cint_parser.py
│   ├── test_macro_parser.py
│   ├── test_e2e.py
│   └── fixtures/
│       └── sdk/                  # Фейковый SDK для тестов
│           ├── include/bcm/vlan.h
│           ├── include/bcm/l2.h
│           ├── include/bcm/l3.h
│           ├── include/bcm/mpls.h
│           ├── include/soc/devids.h
│           ├── include/soc/cm.h
│           ├── src/examples/l3/route_basic.c
│           ├── src/examples/l3/route_basic.bcm
│           ├── src/examples/l3/route_basic.log
│           ├── src/examples/vlan/vlan_create.c
│           ├── src/bcm/esw/l2.c
│           ├── src/bcm/esw/l3.c
│           └── src/bcm/esw/tomahawk4/l2.c
├── config/
│   └── chip_map.json             # Маппинг имён чипов → макросы
├── cache/
│   └── .gitkeep                  # Директория для SQLite индекса
├── docs/
│   ├── CONTRACT.md               # Описание контрактов инструментов
│   ├── SETUP.md                  # Инструкция по подключению к IDE
│   ├── INTEGRATION_LOGS.md       # Логи проверочных вызовов
│   ├── continue.json.example     # Пример конфига для Continue
│   └── opencode.json.example     # Пример конфига для OpenCode
├── .vscode/
│   └── mcp.json                  # Конфиг для Cline
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
├── PLAN.md                       # Этот файл
├── PROMPTS.md                    # История промптов
└── CHANGES.md                    # История изменений
```

---

## Фаза 0: Инициализация Memory Bank и документации проекта

### Шаг 0.1 — Инициализировать Memory Bank
**Что сделать:** Создать директорию `memory-bank/` и 6 core-файлов.

1. `memory-bank/projectbrief.md` — foundation-документ:
   - Название проекта: OpenBCM Helper MCP Server
   - Цель: MCP-сервер для навигации по OpenBCM SDK, помогающий AI-ассистентам находить API, примеры, трассировать цепочки реализации
   - Ключевые требования: 7 инструментов, безопасность (sandbox), индексация SDK, CINT парсинг
   - Ссылки: task.md, mcp_requirements.md, PLAN.md

2. `memory-bank/productContext.md`:
   - Проблема: разработчикам под Broadcom ASIC нужно быстро находить API, примеры, понимать chip-specific код
   - Решение: MCP-сервер с инструментами поиска по SDK
   - UX: агент в IDE вызывает tool → сервер ищет в SDK → возвращает структурированный JSON

3. `memory-bank/activeContext.md`:
   - Текущий фокус: начало реализации, Фаза 0
   - Последние изменения: план утверждён
   - Активные решения: использование uv, structlog, fake SDK для тестов
   - Следующие шаги: создать структуру проекта

4. `memory-bank/systemPatterns.md`:
   - Архитектура: MCP stdio сервер → tools → search/indexer/security слои
   - Паттерны: Tool-ориентированная архитектура, Repository pattern (SQLite), Strategy pattern (парсеры)
   - Компоненты: server → tools → search/indexer/security/models
   - Критические пути: инициализация индекса, path validation, rg search

5. `memory-bank/techContext.md`:
   - Python 3.13.7, uv, MCP SDK, pydantic, structlog, rapidfuzz, orjson, sqlite3
   - Системные: ripgrep (установлен)
   - SDK: реальный по OPENBCM_SDK_PATH, фейковый в tests/fixtures/sdk/
   - IDE: VS Code + Cline (основная), Continue, OpenCode

6. `memory-bank/progress.md`:
   - Что работает: ничего, проект не начат
   - Что осталось: весь проект
   - Статус: Планирование завершено, ожидается реализация
   - Known issues: нет

### Шаг 0.2 — Создать PROMPTS.md (история промптов)
**Что сделать:** Создать файл `PROMPTS.md` с записью всей переписки по планированию.

**Формат записи:**
```markdown
## 2026-05-28 00:00 — Исходный промпт с заданием

**Режим:** Plan

**Промпт:**
[Текст промпта пользователя с task.md и mcp_requirements.md]

**Ответ агента:**
[Вопросы и план]

**Результат:** План согласован, переход к реализации
```

Записать ВСЕ сообщения из этой переписки Plan Mode как отдельные записи в хронологическом порядке.

### Шаг 0.3 — Создать CHANGES.md
**Что сделать:** Создать файл `CHANGES.md` с первой записью.

```markdown
# История изменений

## 2026-05-28 00:00 — Создан план реализации
- PLAN.md: полный пошаговый план
- PROMPTS.md: записана история планирования
```

### Шаг 0.4 — Создать структуру директорий
**Что сделать:** Создать все директории проекта через `mkdir -p`.

```bash
mkdir -p src/server src/tools src/search src/indexer src/security src/models
mkdir -p tests/fixtures/sdk/include/bcm tests/fixtures/sdk/include/soc
mkdir -p tests/fixtures/sdk/src/examples/l3 tests/fixtures/sdk/src/examples/vlan
mkdir -p tests/fixtures/sdk/src/bcm/esw/tomahawk4
mkdir -p config cache docs .vscode memory-bank
touch cache/.gitkeep
```

### Шаг 0.5 — Обновить PROMPTS.md и CHANGES.md
**Что сделать:** Добавить запись о завершении Фазы 0 в оба файла.

---

## Фаза 1: Базовый скелет проекта и зависимости

### Шаг 1.1 — Создать pyproject.toml
**Что сделать:** Создать `pyproject.toml` с зависимостями.

```toml
[project]
name = "openbcm-helper-mcp"
version = "0.1.0"
description = "MCP server for OpenBCM SDK navigation"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "structlog>=23.0",
    "rapidfuzz>=3.5",
    "orjson>=3.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
]

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.setuptools.packages.find]
include = ["src*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
asyncio_mode = "auto"
```

### Шаг 1.2 — Создать requirements.txt
**Что сделать:** Сгенерировать через `uv pip compile`.

```bash
uv pip compile pyproject.toml -o requirements.txt
```

### Шаг 1.3 — Создать .env.example
```env
OPENBCM_SDK_PATH=/home/ai/00/openbcm/sdk-6.5.27
OPENBCM_MCP_LOG_LEVEL=INFO
OPENBCM_MCP_CACHE_DIR=./cache
```

### Шаг 1.4 — Создать .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual environment
.venv/

# Environment
.env

# Cache
cache/
*.db

# IDE
.vscode/settings.json

# OS
.DS_Store
Thumbs.db
```

### Шаг 1.5 — Создать виртуальное окружение и установить зависимости
```bash
uv venv
uv sync
```

### Шаг 1.6 — Создать пустые __init__.py
**Что сделать:** Создать `__init__.py` во всех пакетах:
- `src/__init__.py`
- `src/server/__init__.py`
- `src/tools/__init__.py`
- `src/search/__init__.py`
- `src/indexer/__init__.py`
- `src/security/__init__.py`
- `src/models/__init__.py`
- `tests/__init__.py`

### Шаг 1.7 — Создать src/__main__.py (заглушка)
```python
"""Точка входа: python -m src"""

def main():
    print("OpenBCM Helper MCP Server")

if __name__ == "__main__":
    main()
```

### Шаг 1.8 — Проверить, что python -m src работает
```bash
python -m src
# Ожидаемый вывод: OpenBCM Helper MCP Server
```

### Шаг 1.9 — Обновить документацию
- `memory-bank/techContext.md` — подтвердить установку зависимостей
- `memory-bank/activeContext.md` — отметить завершение Фазы 1
- `CHANGES.md` — добавить запись
- `PROMPTS.md` — добавить запись (если был диалог)

---

## Фаза 2: Логирование, конфигурация и модели

### Шаг 2.1 — Реализовать src/server/logger.py
**Что сделать:** Настроить structlog.

```python
import structlog
import logging
import os

def setup_logging():
    """Настройка структурированного логирования."""
    log_level = os.getenv("OPENBCM_MCP_LOG_LEVEL", "INFO").upper()
    
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(level=log_level)
    return structlog.get_logger()
```

### Шаг 2.2 — Реализовать src/config.py
**Что сделать:** Загрузка конфигурации из env через pydantic-settings.

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    openbcm_sdk_path: Path
    openbcm_mcp_log_level: str = "INFO"
    openbcm_mcp_cache_dir: Path = Path("./cache")
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### Шаг 2.3 — Реализовать src/models/schemas.py
**Что сделать:** Pydantic модели для всех I/O контрактов инструментов.

Модели:
- `BaseResult` — ok: bool, error: str | None
- `ApiResult` — name, signature, module, header, line, description, parameters, returns, chip_availability, related_apis
- `ExampleResult` — file, line, snippet, source_type, script_header, related_files
- `ExampleListResult` — api, total_found, examples
- `TraceResult` — entry_point, implementation_chain, chip_specific_branches
- `ChipInfoResult` — chip, dev_ids, feature_macros, modules, soc_directories, api_count_estimate, example_apis, cint_scripts
- `CintScriptResult` — file, header_comment, apis_used, related_files
- `PingResult` — status, sdk_configured, indexed, version
- `SdkInfoResult` — sdk_path, version, indexed, modules_count, apis_count, cache_dir
- Все модели обёрнуты в `ToolResult[T]` с полями ok, result: T, meta

### Шаг 2.4 — Обновить документацию
- `memory-bank/activeContext.md` — Фаза 2 завершена
- `memory-bank/systemPatterns.md` — описать модели
- `CHANGES.md` — добавить запись

---

## Фаза 3: Безопасность (PathGuard)

### Шаг 3.1 — Реализовать src/security/path_guard.py
```python
from pathlib import Path

class SecurityError(Exception):
    """Ошибка безопасности при попытке доступа вне sandbox."""
    pass

class PathGuard:
    """Защита от path traversal. Все пути проверяются на принадлежность SDK_ROOT."""
    
    def __init__(self, sdk_root: Path):
        self.sdk_root = sdk_root.resolve()
    
    def validate(self, path: str) -> Path:
        """Проверить, что path находится внутри sdk_root."""
        resolved = (self.sdk_root / path).resolve()
        if not str(resolved).startswith(str(self.sdk_root)):
            raise SecurityError(f"Path traversal detected: {resolved}")
        if resolved.is_symlink():
            raise SecurityError("Symlinks are not allowed")
        if not resolved.exists():
            raise FileNotFoundError(f"Path does not exist: {resolved}")
        return resolved
    
    def validate_relative(self, path: str) -> Path:
        """Проверить относительный путь (без конкатенации с sdk_root)."""
        # Используется для путей, которые уже внутри sdk_root
        resolved = Path(path).resolve()
        return self.validate(str(resolved.relative_to(self.sdk_root)) if resolved != self.sdk_root else ".")
```

### Шаг 3.2 — Написать tests/test_security.py
**Что сделать:** Тесты PathGuard с фейковым SDK.

Тест-кейсы:
- Успешная валидация пути внутри SDK
- Path traversal (..) — ожидается SecurityError
- Абсолютный путь вне SDK — ожидается SecurityError
- Симлинк — ожидается SecurityError
- Несуществующий путь — ожидается FileNotFoundError

### Шаг 3.3 — Запустить тесты
```bash
uv run pytest tests/test_security.py -v
```

### Шаг 3.4 — Обновить документацию
- `memory-bank/activeContext.md` — Фаза 3 завершена
- `memory-bank/systemPatterns.md` — описать security слой
- `CHANGES.md`, `PROMPTS.md`

---

## Фаза 4: Поисковые утилиты (search/)

### Шаг 4.1 — Реализовать src/search/rg_search.py
**Что сделать:** Обёртка над ripgrep (subprocess).

Функции:
- `rg_search(pattern: str, path: Path, file_pattern: str = None, context_lines: int = 0, max_results: int = 50) -> list[RgMatch]`
- `rg_count(pattern: str, path: Path, file_pattern: str = None) -> int`
- `rg_files(pattern: str, path: Path, file_pattern: str = None) -> list[Path]`

Каждый `RgMatch`: file, line, column, text, context_before, context_after.

Использовать `subprocess.run` с `["rg", "--json", ...]` для structured output.
Whitelist: только команда `rg`, никакие другие subprocess не разрешены.

### Шаг 4.2 — Реализовать src/search/api_parser.py
**Что сделать:** Парсинг C-деклараций функций.

Функции:
- `parse_function_declaration(text: str) -> FunctionDecl | None`
- `parse_function_definition(text: str) -> FunctionDef | None`
- `extract_doxygen_comment(lines: list[str], func_line: int) -> DocComment | None`

Использовать regex для извлечения:
- Возвращаемый тип
- Имя функции
- Параметры (тип, имя)
- Doxygen: @brief, @param, @return

### Шаг 4.3 — Реализовать src/search/macro_parser.py
**Что сделать:** Парсинг #define / #ifdef.

Функции:
- `extract_macros(lines: list[str]) -> list[MacroDef]`
- `extract_guards(lines: list[str], func_line: int) -> list[str]` — извлечение #if defined(BCM_...) вокруг функции
- `extract_chip_conditions(lines: list[str], func_line: int) -> list[str]` — поиск SOC_IS_* условий

### Шаг 4.4 — Реализовать src/search/cint_parser.py
**Что сделать:** Парсинг заголовков CINT скриптов.

Функции:
- `is_cint_script(file_path: Path) -> bool` — проверка по расположению в директориях examples/cint/diag или по характерным комментариям
- `extract_script_header(file_path: Path) -> str | None` — извлечение многострочного комментария в начале файла (первые 5-20 строк)
- `parse_header_comment(comment: str) -> dict` — извлечение чипа, портов, описания, тестов из заголовка

### Шаг 4.5 — Написать тесты для search/
- `tests/test_cint_parser.py` — с фейковыми CINT скриптами
- `tests/test_macro_parser.py` — с фейковыми макросами

### Шаг 4.6 — Запустить тесты
```bash
uv run pytest tests/test_cint_parser.py tests/test_macro_parser.py -v
```

### Шаг 4.7 — Обновить документацию

---

## Фаза 5: Создание фейкового SDK для тестов

### Шаг 5.1 — Создать tests/fixtures/sdk/include/bcm/vlan.h
**Что сделать:** Файл с декларациями VLAN API.

```c
/**
 * @brief Create a new VLAN
 * @param unit Device unit number
 * @param vlan VLAN ID
 * @return BCM_E_NONE on success, error code otherwise
 */
int bcm_vlan_create(int unit, bcm_vlan_t vlan);

int bcm_vlan_destroy(int unit, bcm_vlan_t vlan);
int bcm_vlan_get(int unit, bcm_vlan_t vlan, bcm_vlan_t *result);
```

### Шаг 5.2 — Создать tests/fixtures/sdk/include/bcm/l2.h
```c
/**
 * @brief Add L2 address entry
 * @param unit Device unit number
 * @param addr L2 address structure
 * @return BCM_E_NONE on success, error code otherwise
 */
int bcm_l2_addr_add(int unit, bcm_l2_addr_t *addr);
int bcm_l2_addr_delete(int unit, bcm_l2_addr_t *addr);
int bcm_l2_addr_get(int unit, bcm_l2_addr_t *addr);
```

### Шаг 5.3 — Создать tests/fixtures/sdk/include/bcm/l3.h
```c
/**
 * @brief Add L3 route entry
 * @param unit Device unit number
 * @param route Route structure
 * @return BCM_E_NONE on success, error code otherwise
 */
int bcm_l3_route_add(int unit, bcm_l3_route_t *route);
int bcm_l3_route_get(int unit, bcm_l3_route_t *route);
int bcm_l3_route_delete(int unit, bcm_l3_route_t *route);
```

### Шаг 5.4 — Создать tests/fixtures/sdk/include/soc/devids.h
```c
#define BCM56980_DEVICE_ID 0x56980
#define BCM56980_A0 0x01
#define BCM56980_B0 0x02
```

### Шаг 5.5 — Создать CINT скрипты
**tests/fixtures/sdk/src/examples/l3/route_basic.c:**
```c
/*
 * L3 Route Basic Example
 * Tested on: Tomahawk4 (BCM56980)
 * Ports: 0-31
 * Tests: IPv4 unicast route add/get/delete
 */

#include <bcm/l3.h>

int test_route_add(int unit) {
    bcm_l3_route_t route;
    bcm_l3_route_t_init(&route);
    BCM_IF_ERROR_RETURN(bcm_l3_route_add(unit, &route));
    return 0;
}
```

**tests/fixtures/sdk/src/examples/vlan/vlan_create.c:**
```c
/*
 * VLAN Create Example
 * Tested on: Trident3 (BCM56870)
 * Ports: 0-15
 * Tests: VLAN create/destroy
 */

#include <bcm/vlan.h>

int test_vlan_create(int unit) {
    int rv = bcm_vlan_create(unit, 100);
    return rv;
}
```

### Шаг 5.6 — Создать файлы реализации
**tests/fixtures/sdk/src/bcm/esw/l2.c:**
```c
#include <bcm/l2.h>

int bcm_esw_l2_addr_add(int unit, bcm_l2_addr_t *addr) {
    return _bcm_esw_l2_addr_add_internal(unit, addr);
}

static int _bcm_esw_l2_addr_add_internal(int unit, bcm_l2_addr_t *addr) {
    if (SOC_IS_TOMAHAWK4(unit)) {
        return th4_l2_entry_insert(unit, addr);
    }
    return BCM_E_UNAVAIL;
}

#if defined(BCM_TOMAHAWK4_SUPPORT)
static int th4_l2_entry_insert(int unit, bcm_l2_addr_t *addr) {
    /* Tomahawk4 specific implementation */
    return BCM_E_NONE;
}
#endif
```

**tests/fixtures/sdk/src/bcm/esw/tomahawk4/l2.c:**
```c
#if defined(BCM_TOMAHAWK4_SUPPORT)

int th4_l2_entry_insert(int unit, bcm_l2_addr_t *addr) {
    /* Tomahawk4 L2 entry insert */
    return BCM_E_NONE;
}

#endif /* BCM_TOMAHAWK4_SUPPORT */
```

**tests/fixtures/sdk/src/bcm/esw/l3.c:**
```c
#include <bcm/l3.h>

int bcm_esw_l3_route_add(int unit, bcm_l3_route_t *route) {
    return BCM_E_NONE;
}
```

### Шаг 5.7 — Создать сопутствующие файлы
- `tests/fixtures/sdk/src/examples/l3/route_basic.bcm` — конфигурация портов
- `tests/fixtures/sdk/src/examples/l3/route_basic.log` — лог вывода

### Шаг 5.8 — Обновить документацию

---

## Фаза 6: Индексация SDK

### Шаг 6.1 — Создать config/chip_map.json
```json
{
  "Tomahawk4": {
    "dev_ids": ["BCM56980_DEVICE_ID"],
    "feature_macros": ["BCM_TOMAHAWK4_SUPPORT", "INCLUDE_L3", "INCLUDE_MPLS"],
    "soc_dirs": ["src/bcm/esw/tomahawk4/"],
    "modules": ["L2", "L3", "VLAN"],
    "example_apis": ["bcm_l2_addr_add", "bcm_vlan_create", "bcm_l3_route_add"]
  },
  "Trident3": {
    "dev_ids": ["BCM56870_DEVICE_ID"],
    "feature_macros": ["BCM_TRIDENT3_SUPPORT", "INCLUDE_L3"],
    "soc_dirs": ["src/bcm/esw/trident3/"],
    "modules": ["L2", "L3", "VLAN"],
    "example_apis": ["bcm_vlan_create"]
  }
}
```

### Шаг 6.2 — Создать src/indexer/schema.sql
```sql
CREATE TABLE IF NOT EXISTS functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    signature TEXT,
    return_type TEXT,
    file_path TEXT NOT NULL,
    line INTEGER NOT NULL,
    line_end INTEGER,
    module TEXT,
    description TEXT,
    doc_comment TEXT,
    chip_macros TEXT,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, file_path)
);

CREATE TABLE IF NOT EXISTS function_params (
    function_id INTEGER NOT NULL,
    param_index INTEGER NOT NULL,
    name TEXT,
    param_type TEXT,
    description TEXT,
    FOREIGN KEY(function_id) REFERENCES functions(id)
);

CREATE TABLE IF NOT EXISTS macros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    definition_file TEXT,
    definition_line INTEGER,
    definition_value TEXT,
    chip_association TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS api_macros (
    api_name TEXT NOT NULL,
    macro_name TEXT NOT NULL,
    PRIMARY KEY(api_name, macro_name)
);
```

### Шаг 6.3 — Создать src/indexer/chip_map.py
```python
import json
from pathlib import Path

class ChipMap:
    """Загрузка и предоставление маппинга чипов."""
    
    def __init__(self, config_path: Path):
        with open(config_path) as f:
            self._data = json.load(f)
    
    def get_chip(self, name: str) -> dict | None:
        return self._data.get(name)
    
    def list_chips(self) -> list[str]:
        return list(self._data.keys())
```

### Шаг 6.4 — Реализовать src/indexer/sdk_indexer.py
**Что сделать:** Индексация SDK в SQLite.

Методы:
- `__init__(sdk_path: Path, cache_dir: Path, chip_map: ChipMap)`
- `ensure_indexed() -> bool` — проверяет наличие индекса, если нет — запускает индексацию
- `needs_reindex() -> bool` — проверяет, изменился ли SDK
- `index() -> IndexStats` — полная индексация
- `search_api(name: str, chip: str = None, fuzzy: bool = False) -> list[dict]`
- `get_stats() -> IndexStats`

Процесс индексации:
1. rg поиск `^ *(int|uint32|shr_error_t|bcm_error_t|void) *bcm_\w+\(` по `include/bcm/*.h`
2. Парсинг каждой декларации через api_parser
3. Извлечение chip guards через macro_parser
4. Сохранение в SQLite
5. rg поиск `#define\s+(\w+)` по всем `.h` файлам
6. Сохранение макросов

### Шаг 6.5 — Обновить документацию

---

## Фаза 7: Реализация инструментов (7 tools)

### Шаг 7.1 — TOOL 1: ping (src/tools/ping.py)
```python
@server.tool()
async def ping() -> dict:
    """Health check — проверка, что сервер работает и SDK сконфигурирован."""
    # Проверка SDK_PATH, индекса
    # Возврат статуса
```

**Параметры:** нет  
**Возврат:** `{"status": "ok", "sdk_configured": true, "indexed": true, "version": "0.1.0"}`

### Шаг 7.2 — TOOL 2: get_sdk_info (src/tools/get_sdk_info.py)
```python
@server.tool()
async def get_sdk_info(include_modules: bool = False) -> dict:
    """Информация о SDK: версия, путь, статус индексации, количество API."""
```

**Параметры:** `include_modules` (bool, default false)  
**Возврат:** `SdkInfoResult`

### Шаг 7.3 — TOOL 3: find_bcm_api (src/tools/find_bcm_api.py)
```python
@server.tool()
async def find_bcm_api(
    api: str,
    chip: str = "all",
    fuzzy: bool = False
) -> dict:
    """Поиск декларации BCM API в заголовочных файлах SDK."""
```

**Логика:** Поиск в индексе → если не найдено и fuzzy=true → rapidfuzz → если не найдено → rg fallback

### Шаг 7.4 — TOOL 4: find_api_examples (src/tools/find_api_examples.py)
```python
@server.tool()
async def find_api_examples(
    api: str,
    source_type: str = "all",
    max_results: int = 10,
    context_lines: int = 3,
    include_full_source: bool = False
) -> dict:
    """Поиск примеров использования API в C-коде и CINT скриптах."""
```

**Логика:** rg поиск `api(` по SDK → классификация c/cint/bcm_config → извлечение контекста

### Шаг 7.5 — TOOL 5: trace_api_implementation (src/tools/trace_implementation.py)
```python
@server.tool()
async def trace_api_implementation(
    api: str,
    chip: str = None,
    max_depth: int = 3
) -> dict:
    """Показать цепочку реализации от public API до chip-specific кода."""
```

**Логика:** Поиск `bcm_esw_<api>` → rg рекурсивный поиск вызовов → анализ chip conditions

### Шаг 7.6 — TOOL 6: get_chip_info (src/tools/get_chip_info.py)
```python
@server.tool()
async def get_chip_info(
    chip: str,
    include_apis: bool = False,
    include_cint_scripts: bool = False
) -> dict:
    """Получить сводку по ASIC."""
```

**Логика:** chip_map.json → rg поиск feature macros → rg поиск CINT скриптов для чипа

### Шаг 7.7 — TOOL 7: find_cint_scripts (src/tools/find_cint_scripts.py)
```python
@server.tool()
async def find_cint_scripts(
    query: str,
    chip: str = None,
    include_logs: bool = False,
    include_configs: bool = False,
    include_full_source: bool = False
) -> dict:
    """Поиск CINT скриптов по функционалу, чипу или параметрам."""
```

**Логика:** rg поиск по src/examples/, cint/, diag/ — по имени файла, заголовку, вызовам API

### Шаг 7.8 — Обновить документацию

---

## Фаза 8: MCP сервер

### Шаг 8.1 — Реализовать src/server/mcp_server.py
**Что сделать:** Главный файл сервера.

```python
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

class OpenBcmMcpServer:
    """MCP сервер для OpenBCM SDK."""
    
    def __init__(self, settings: Settings, logger):
        self.settings = settings
        self.logger = logger
        self.server = Server("openbcm-helper")
        self.path_guard = PathGuard(settings.openbcm_sdk_path)
        self.chip_map = ChipMap(Path("config/chip_map.json"))
        self.indexer = SdkIndexer(
            settings.openbcm_sdk_path,
            settings.openbcm_mcp_cache_dir,
            self.chip_map
        )
        self._register_tools()
    
    def _register_tools(self):
        """Регистрация всех инструментов."""
        # Каждый tool логирует: имя, параметры, статус, время выполнения
        # ...
    
    async def run(self):
        """Запуск сервера через stdio транспорт."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())
```

**Логирование каждого вызова:**
```python
self.logger.info("tool_call", 
    tool=tool_name, 
    params=sanitized_params,
    status="success", 
    elapsed_ms=elapsed
)
```

### Шаг 8.2 — Обновить src/__main__.py
```python
"""Точка входа: python -m src"""

from src.server.mcp_server import OpenBcmMcpServer
from src.server.logger import setup_logging
from src.config import settings

def main():
    logger = setup_logging()
    logger.info("Starting OpenBCM Helper MCP Server", sdk_path=str(settings.openbcm_sdk_path))
    
    server = OpenBcmMcpServer(settings, logger)
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
```

### Шаг 8.3 — Запустить сервер с фейковым SDK
```bash
OPENBCM_SDK_PATH=tests/fixtures/sdk python -m src
```

### Шаг 8.4 — Проверить через MCP Inspector
```bash
# Установка MCP Inspector (если нужно)
npx @modelcontextprotocol/inspector python -m src
# Или прямой тест через скрипт
```

### Шаг 8.5 — Обновить документацию

---

## Фаза 9: Тестирование

### Шаг 9.1 — Написать tests/test_find_bcm_api.py
Тест-кейсы:
- Поиск существующего API (`bcm_vlan_create`) — возвращает результат
- Поиск несуществующего API — возвращает error
- Поиск с fuzzy=true и частичным именем
- Поиск с фильтром по чипу
- Поиск с нечётким совпадением

### Шаг 9.2 — Написать tests/test_find_api_examples.py
Тест-кейсы:
- Поиск примеров для существующего API
- Фильтр по source_type=cint
- Фильтр по source_type=c
- include_full_source=true
- max_results limit

### Шаг 9.3 — Написать tests/test_trace_implementation.py
Тест-кейсы:
- Трассировка bcm_l2_addr_add (с chip-specific веткой)
- Трассировка c ограничением глубины
- Трассировка несуществующего API

### Шаг 9.4 — Написать tests/test_e2e.py
**Что сделать:** E2E тест: запуск сервера, вызов tool через MCP протокол.

```python
# Использовать mcp.client.stdio для подключения к серверу
# Вызвать ping tool
# Проверить результат
```

### Шаг 9.5 — Запустить все тесты
```bash
uv run pytest tests/ -v --tb=short
```

### Шаг 9.6 — Исправить ошибки, если тесты не проходят
Итеративно: читать ошибки → фиксить → перезапускать тесты.

### Шаг 9.7 — Обновить документацию
- `memory-bank/progress.md` — отметить какие тесты работают
- `CHANGES.md`

---

## Фаза 10: Документация и конфиги IDE

### Шаг 10.1 — docs/CONTRACT.md
Описание контрактов всех 7 инструментов:
- Имя, описание, параметры (тип, обязательность, дефолт)
- Выходной формат (JSON схема)
- Примеры запросов и ответов
- Коды ошибок

### Шаг 10.2 — docs/SETUP.md
Инструкция по подключению к IDE:
- Предварительные требования (Python 3.10+, uv, ripgrep)
- Клонирование репозитория
- Установка зависимостей
- Настройка .env
- Конфигурация для Cline (.vscode/mcp.json)
- Конфигурация для Continue (docs/continue.json.example)
- Конфигурация для OpenCode (docs/opencode.json.example)
- Проверка подключения (ping)

### Шаг 10.3 — .vscode/mcp.json (конфиг для Cline)
```json
{
  "servers": {
    "openbcm-helper": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src"],
      "env": {
        "OPENBCM_SDK_PATH": "/home/ai/00/openbcm/sdk-6.5.27",
        "OPENBCM_MCP_LOG_LEVEL": "INFO",
        "OPENBCM_MCP_CACHE_DIR": "./cache"
      }
    }
  }
}
```

### Шаг 10.4 — docs/continue.json.example
```json
{
  "experimental": {
    "tools": true
  },
  "mcpServers": {
    "openbcm-helper": {
      "command": "python",
      "args": ["-m", "src"],
      "env": {
        "OPENBCM_SDK_PATH": "/path/to/openbcm-sdk-6.5.27",
        "OPENBCM_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Шаг 10.5 — docs/opencode.json.example
Конфиг согласно документации OpenCode (https://opencode.ai/docs/mcp-servers/).

```json
{
  "mcpServers": {
    "openbcm-helper": {
      "command": "python",
      "args": ["-m", "src"],
      "env": {
        "OPENBCM_SDK_PATH": "/path/to/openbcm-sdk-6.5.27",
        "OPENBCM_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Шаг 10.6 — README.md
Полное описание проекта:
- Назначение
- Архитектура (диаграмма ascii)
- 7 инструментов (кратко)
- Быстрый старт
- Безопасность (sandbox, whitelist, path traversal)
- Переменные окружения
- Структура проекта
- Ссылки на код (с диапазонами строк)
- Примеры вызовов
- Требования к формату результатов (ссылка на CONTRACT.md)

### Шаг 10.7 — docs/INTEGRATION_LOGS.md
Шаблон для записи логов интеграции (заполняется в Фазе 11).

### Шаг 10.8 — Обновить документацию

---

## Фаза 11: Интеграция с IDE и проверочные запросы

### Шаг 11.1 — Подключить сервер к Cline
1. Убедиться, что .vscode/mcp.json создан
2. Перезапустить Cline (или VS Code)
3. Проверить, что сервер отображается в списке MCP серверов

### Шаг 11.2 — Выполнить проверочные запросы (минимум 5)

**Запрос 1:** "ping"  
- Ожидаемый tool: `ping`  
- Ожидаемый результат: `{"status": "ok", "sdk_configured": true, ...}`

**Запрос 2:** "Найди API bcm_vlan_create"  
- Ожидаемый tool: `find_bcm_api`  
- Ожидаемый результат: сигнатура, параметры, chip_availability

**Запрос 3:** "Покажи примеры использования bcm_l3_route_add"  
- Ожидаемый tool: `find_api_examples`  
- Ожидаемый результат: CINT скрипт route_basic.c

**Запрос 4:** "Расскажи о чипе Tomahawk4"  
- Ожидаемый tool: `get_chip_info`  
- Ожидаемый результат: dev_ids, feature_macros, модули

**Запрос 5:** "Покажи цепочку реализации bcm_l2_addr_add"  
- Ожидаемый tool: `trace_api_implementation`  
- Ожидаемый результат: entry_point → implementation chain → chip_specific_branches

### Шаг 11.3 — Зафиксировать результаты
1. Записать каждый запрос, ожидаемый tool и фактический результат в `docs/INTEGRATION_LOGS.md`
2. Приложить логи сервера (из stdout/stderr)
3. Сделать скриншоты (опционально)

### Шаг 11.4 — Обновить документацию
- `memory-bank/activeContext.md`
- `memory-bank/progress.md`
- `CHANGES.md`
- `PROMPTS.md`

---

## Фаза 12: Финальная проверка по чеклисту ДЗ

### Шаг 12.1 — Проверить критерии оценки ДЗ
- [ ] MCP-сервер запускается по инструкции из репозитория
- [ ] Реализованы минимум 2 инструмента (факт: 7)
- [ ] Интеграция с агентом в IDE показана и воспроизводима по шагам
- [ ] Есть минимум 5 проверочных запросов; минимум 3 приводят к вызову MCP-tool
- [ ] Добавлены логи/отладочный вывод на стороне сервера
- [ ] Секреты не закоммичены

### Шаг 12.2 — Проверить требования к подтверждениям ссылками на код
- [ ] Реализован MCP-сервер — указан файл и строки (src/server/mcp_server.py)
- [ ] Для каждого tool: файл, строки реализации, строки логов, пример вывода
- [ ] Пример запроса с указанием ожидаемого tool и фактического подтверждения
- [ ] Формат результатов tool — ссылка на docs/CONTRACT.md

### Шаг 12.3 — Проверить .gitignore и секреты
```bash
git status
# Проверить, что .env не в индексе, cache/* не в индексе
```

### Шаг 12.4 — Финальное обновление Memory Bank
- `memory-bank/progress.md` — all done
- `memory-bank/activeContext.md` — проект завершён

### Шаг 12.5 — Финальные записи в CHANGES.md и PROMPTS.md
- CHANGES.md: последняя запись о завершении проекта
- PROMPTS.md: запись о финальной проверке

---

## Приложение: Шаблон для каждого шага

При выполнении каждого шага агент должен:

1. **Выполнить** действия (создать/изменить файлы, запустить команды)
2. **Проверить** результат (тесты, валидация)
3. **Обновить** `memory-bank/activeContext.md` — отметить текущий шаг
4. **Записать** в `CHANGES.md` — что сделано, какие файлы изменены
5. **Если был диалог** с пользователем — записать в `PROMPTS.md`

Формат записи в CHANGES.md:
```
## YYYY-MM-DD HH:MM — Название шага
- Что сделано: [описание]
- Файлы: [список файлов]
```

Формат записи в PROMPTS.md:
```
## YYYY-MM-DD HH:MM — Контекст запроса

**Режим:** Act/Plan

**Промпт:**
[текст]

**Ответ агента:**
[текст]

**Результат:**
[описание результата]
```

---

*План составлен 2026-05-28. Версия 1.0.*