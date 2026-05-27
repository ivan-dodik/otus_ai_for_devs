# OpenBCM Helper MCP Server (MVP)

---

## 1. Название проекта

`openbcm-helper-mcp`

## 2. Назначение

MCP-сервер для навигации по OpenBCM SDK. Помогает AI-ассистентам находить API, искать примеры использования (включая CINT скрипты), трассировать цепочки реализации и получать информацию о доступности функций на разных ASIC.

## 3. Структура проекта

```
openbcm-helper-mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # Точка входа: python -m src
│   │
│   ├── server/
│   │   ├── __init__.py
│   │   ├── mcp_server.py        # MCP сервер (stdio), регистрация tools
│   │   └── logger.py            # Настройка логирования
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── find_bcm_api.py      # TOOL 1: поиск API
│   │   ├── find_api_examples.py # TOOL 2: поиск примеров (C + CINT)
│   │   ├── trace_implementation.py # TOOL 3: трассировка реализации
│   │   ├── get_chip_info.py     # TOOL 4: информация о чипе
│   │   └── find_cint_scripts.py # TOOL 5 (бонус): поиск CINT скриптов
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   ├── rg_search.py         # Обёртка над ripgrep
│   │   ├── api_parser.py        # Парсинг деклараций C-функций
│   │   ├── macro_parser.py      # Парсинг #define / #ifdef
│   │   └── cint_parser.py       # Парсинг заголовков CINT скриптов
│   │
│   ├── indexer/
│   │   ├── __init__.py
│   │   ├── sdk_indexer.py       # Индексация SDK в SQLite
│   │   ├── schema.sql           # SQLite схема
│   │   └── chip_map.py          # Маппинг чип → макросы
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   └── path_guard.py        # Sandbox: только SDK_PATH
│   │
│   └── models/
│       ├── __init__.py
│       └── schemas.py           # Pydantic модели для I/O
│
├── config/
│   └── chip_map.json            # Маппинг имён чипов → макросы
│
├── cache/
│   └── index.db                 # SQLite индекс
│
├── tests/
│   ├── test_find_bcm_api.py
│   ├── test_find_api_examples.py
│   ├── test_trace_implementation.py
│   ├── test_security.py
│   └── fixtures/                # Фрагменты SDK для тестов
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
└── docs/
    ├── CONTRACT.md               # Описание контрактов инструментов
    └── SETUP.md                  # Инструкция по подключению к IDE
```

## 4. Технологический стек

| Компонент | Библиотека | Назначение |
|-----------|-----------|------------|
| MCP протокол | `mcp` (≥1.0.0) | MCP Python SDK |
| Валидация | `pydantic` (≥2.0) | Схемы данных |
| Поиск | `ripgrep` (через subprocess) | Быстрый текстовый поиск |
| JSON | `orjson` (≥3.9) | Быстрая сериализация |
| БД | `sqlite3` (встроенный) | Лёгкий индекс |
| Логи | `structlog` (≥23.0) | Структурированное логирование |
| Fuzzy match | `rapidfuzz` (≥3.5) | Поиск по частичному совпадению |

**Зависимости системы (не Python):** `ripgrep` (входит в whitelist subprocess команд).

## 5. Инструменты (Tools)

### TOOL 1: `find_bcm_api`

**Назначение:** Поиск декларации BCM API в заголовочных файлах SDK.

**Параметры:**

| Параметр | Тип | Обязательность | Описание |
|----------|-----|----------------|----------|
| `api` | string | Да | Имя API (например, `bcm_vlan_create`) |
| `chip` | string | Нет | Фильтр по чипу (`Tomahawk4`, `Trident3`, `all`). По умолчанию `all`. |
| `fuzzy` | boolean | Нет | Включить нечёткий поиск при отсутствии точного совпадения. Default: `false`. |

**Поведение:**
1. Поиск декларации в SQLite индексе (или fallback через rg по `include/bcm/`).
2. Парсинг сигнатуры: возвращаемый тип, имя, параметры.
3. Извлечение Doxygen-комментария (`@brief`, `@param`, `@return`).
4. Поиск `#if defined(BCM_<CHIP>_SUPPORT)` блоков вокруг функции для определения chip availability.
5. Если `fuzzy=true` и точное имя не найдено — rapidfuzz search по всем известным API.

**Выходной формат:**
```json
{
  "ok": true,
  "result": {
    "name": "bcm_vlan_create",
    "signature": "int bcm_vlan_create(int unit, bcm_vlan_t vlan)",
    "module": "VLAN",
    "header": "include/bcm/vlan.h",
    "line": 156,
    "description": "Create a new VLAN",
    "parameters": [
      {"name": "unit", "type": "int", "description": "Device unit number"},
      {"name": "vlan", "type": "bcm_vlan_t", "description": "VLAN ID"}
    ],
    "returns": {"type": "int", "description": "BCM_E_NONE on success, error code otherwise"},
    "chip_availability": ["Tomahawk4", "Trident3"],
    "related_apis": ["bcm_vlan_destroy", "bcm_vlan_get"]
  },
  "meta": {"elapsed_ms": 45, "source": "sqlite"}
}
```

---

### TOOL 2: `find_api_examples`

**Назначение:** Поиск примеров использования API в C-коде и CINT скриптах.

**Параметры:**

| Параметр | Тип | Обязательность | Описание |
|----------|-----|----------------|----------|
| `api` | string | Да | Имя API |
| `source_type` | string | Нет | `all` (по умолчанию), `c`, `cint`, `bcm_config` |
| `max_results` | integer | Нет | Максимум результатов. Default: 10, max: 50. |
| `context_lines` | integer | Нет | Строк контекста вокруг вызова. Default: 3, max: 10. |

**Поведение:**
1. rg поиск `api(` по всем `.c` и `.h` файлам в SDK.
2. **Определение CINT скрипта:** файл считается CINT, если он лежит в директориях `src/examples/`, `cint/`, `diag/` или содержит в начале характерные комментарии (описание функционала, параметры коммутатора, порты).
3. Если `source_type=cint` — ищем только в `src/examples/`, `cint/`, `diag/`.
4. Если `source_type=bcm_config` — ищем `.bcm` файлы рядом с найденными CINT скриптами.
5. Извлечение сниппета с контекстом.
6. Классификация: `c` (C source), `cint` (CINT script), `bcm_config` (конфигурация чипа).
7. **Дополнительно:** для CINT скриптов извлекаем заголовочный комментарий (первые 5-20 строк, если это многострочный комментарий) — он часто содержит описание тестируемого функционала.

**Выходной формат:**
```json
{
  "ok": true,
  "result": {
    "api": "bcm_l3_route_add",
    "total_found": 12,
    "examples": [
      {
        "file": "src/examples/l3/route_basic.c",
        "line": 88,
        "snippet": "    bcm_l3_route_t route;\n    bcm_l3_route_t_init(&route);\n    BCM_IF_ERROR_RETURN(bcm_l3_route_add(unit, &route));",
        "source_type": "cint",
        "script_header": "/*\n * L3 Route Basic Example\n * Tested on: Tomahawk4 (BCM56980)\n * Ports: 0-31\n * Tests: IPv4 unicast route add/get/delete\n */",
        "related_files": [
          {"path": "src/examples/l3/route_basic.log", "type": "log"},
          {"path": "src/examples/l3/route_basic.bcm", "type": "config"}
        ]
      },
      {
        "file": "src/bcm/esw/l3.c",
        "line": 4567,
        "snippet": "    rv = bcm_l3_route_add(unit, &route);",
        "source_type": "c"
      }
    ]
  },
  "meta": {"elapsed_ms": 187, "source": "ripgrep"}
}
```

---

### TOOL 3: `trace_api_implementation`

**Назначение:** Показать цепочку реализации от public API до chip-specific кода.

**Параметры:**

| Параметр | Тип | Обязательность | Описание |
|----------|-----|----------------|----------|
| `api` | string | Да | Имя API |
| `chip` | string | Нет | Фильтр по чипу |
| `max_depth` | integer | Нет | Глубина трассировки. Default: 3, max: 7. |

**Поведение:**
1. Поиск реализации по паттерну `bcm_esw_<имя>` или `bcm_<chip>_<имя>`.
2. Рекурсивный rg-поиск вызовов внутри реализации (до max_depth).
3. Анализ chip-специфичных веток через паттерны:
   - `#if defined(BCM_<CHIP>_SUPPORT)`
   - `if (SOC_IS_TOMAHAWK4(unit)) { ... }`
4. Эвристическое определение dispatch-таблиц (массивы `mbcm_driver`, `*drv_t`).

**Выходной формат:**
```json
{
  "ok": true,
  "result": {
    "api": "bcm_l2_addr_add",
    "entry_point": {
      "function": "bcm_l2_addr_add",
      "file": "include/bcm/l2.h",
      "line": 89
    },
    "implementation_chain": [
      {
        "level": 1,
        "function": "bcm_esw_l2_addr_add",
        "file": "src/bcm/esw/l2.c",
        "line": 456,
        "chip_conditions": ["always"]
      },
      {
        "level": 2,
        "function": "_bcm_esw_l2_addr_add_internal",
        "file": "src/bcm/esw/l2.c",
        "line": 1234,
        "chip_conditions": ["always"]
      },
      {
        "level": 3,
        "function": "th4_l2_entry_insert",
        "file": "src/bcm/esw/tomahawk4/l2.c",
        "line": 67,
        "chip_conditions": ["Tomahawk4"],
        "guard_pattern": "if (SOC_IS_TOMAHAWK4(unit))"
      }
    ],
    "chip_specific_branches": [
      {
        "condition": "SOC_IS_TOMAHAWK4(unit)",
        "functions": ["th4_l2_entry_insert"],
        "soc_file": "src/bcm/esw/tomahawk4/l2.c"
      }
    ]
  },
  "meta": {"elapsed_ms": 345, "max_depth_reached": 3}
}
```

---

### TOOL 4: `get_chip_info`

**Назначение:** Получить сводку по ASIC: поддерживаемые модули, feature macros, dev ids, CINT скрипты.

**Параметры:**

| Параметр | Тип | Обязательность | Описание |
|----------|-----|----------------|----------|
| `chip` | string | Да | Имя чипа (`Tomahawk4`, `Trident3`, `Jericho2`, и т.д.) |
| `include_apis` | boolean | Нет | Показать примеры API. Default: `false`. |
| `include_cint_scripts` | boolean | Нет | Показать CINT скрипты для этого чипа. Default: `false`. |

**Поведение:**
1. Поиск dev id в `include/soc/devids.h` (через rg).
2. Маппинг имени чипа к feature macros из `config/chip_map.json`.
3. rg поиск feature macros по SDK: какие модули/API они включают.
4. Вывод директорий с SOC-специфичным кодом.
5. Если `include_cint_scripts=true` — rg поиск CINT скриптов, в заголовке которых упоминается данный чип.

**Файл `config/chip_map.json`:**
```json
{
  "Tomahawk4": {
    "dev_ids": ["BCM56980_DEVICE_ID"],
    "feature_macros": ["BCM_TOMAHAWK4_SUPPORT", "INCLUDE_L3", "INCLUDE_MPLS"],
    "soc_dirs": ["src/bcm/esw/tomahawk4/", "soc/tomahawk4/"],
    "modules": ["L2", "L3", "VLAN", "MPLS", "QOS", "MIRROR"]
  },
  "Trident3": { ... },
  "Jericho2": { ... }
}
```

**Выходной формат:**
```json
{
  "ok": true,
  "result": {
    "chip": "Tomahawk4",
    "dev_ids": ["BCM56980_A0", "BCM56980_B0"],
    "feature_macros": ["BCM_TOMAHAWK4_SUPPORT", "INCLUDE_L3", "INCLUDE_MPLS"],
    "modules": ["L2", "L3", "VLAN", "MPLS", "QOS", "MIRROR", "FIELD"],
    "soc_directories": ["src/bcm/esw/tomahawk4/", "soc/esw/tomahawk3/"],
    "api_count_estimate": 1847,
    "example_apis": ["bcm_l2_addr_add", "bcm_vlan_create", "bcm_l3_route_add"],
    "cint_scripts": [
      {
        "file": "src/examples/l3/route_basic.c",
        "header": "L3 Route Basic Example",
        "apis_used": ["bcm_l3_route_add", "bcm_l3_route_get"]
      }
    ]
  },
  "meta": {"elapsed_ms": 120}
}
```

---

### TOOL 5 (бонусный): `find_cint_scripts`

**Назначение:** Поиск CINT скриптов по функционалу, чипу или параметрам.

**Параметры:**

| Параметр | Тип | Обязательность | Описание |
|----------|-----|----------------|----------|
| `query` | string | Да | Поисковый запрос (функционал, чип, имя файла) |
| `chip` | string | Нет | Фильтр по чипу |
| `include_logs` | boolean | Нет | Включить логи вывода. Default: `false`. |
| `include_configs` | boolean | Нет | Включить `.bcm` конфиги. Default: `false`. |

**Поведение:**
1. rg поиск по `src/examples/`, `cint/`, `diag/`:
   - По имени файла
   - По содержимому заголовочных комментариев (описание функционала, параметры)
   - По вызовам API внутри скрипта
2. Если `chip` указан — фильтр по упоминанию чипа в заголовке.
3. Если `include_logs=true` — ищем `.log` файлы рядом со скриптами.
4. Если `include_configs=true` — ищем `.bcm` файлы рядом со скриптами.

**Выходной формат:**
```json
{
  "ok": true,
  "result": {
    "query": "L3 route Tomahawk4",
    "total_found": 3,
    "scripts": [
      {
        "file": "src/examples/l3/route_basic.c",
        "header_comment": "/*\n * L3 Route Basic Example\n * Tested on: Tomahawk4 (BCM56980)\n * Ports: 0-31\n * Tests: IPv4 unicast route add/get/delete\n */",
        "apis_used": ["bcm_l3_route_add", "bcm_l3_route_get", "bcm_l3_route_delete"],
        "related_files": [
          {"path": "src/examples/l3/route_basic.log", "type": "log", "size_bytes": 12450},
          {"path": "src/examples/l3/route_basic.bcm", "type": "config", "size_bytes": 340}
        ]
      }
    ]
  },
  "meta": {"elapsed_ms": 250}
}
```

---

## 6. Индексация SDK

### SQLite схема (`src/indexer/schema.sql`)

```sql
-- Таблица функций
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
    chip_macros TEXT, -- JSON: ["BCM_TOMAHAWK4_SUPPORT"]
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, file_path)
);

-- Таблица параметров
CREATE TABLE IF NOT EXISTS function_params (
    function_id INTEGER NOT NULL,
    param_index INTEGER NOT NULL,
    name TEXT,
    param_type TEXT,
    description TEXT,
    FOREIGN KEY(function_id) REFERENCES functions(id)
);

-- Таблица макросов
CREATE TABLE IF NOT EXISTS macros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    definition_file TEXT,
    definition_line INTEGER,
    definition_value TEXT,
    chip_association TEXT,
    description TEXT
);

-- Таблица маппинга API → макросы
CREATE TABLE IF NOT EXISTS api_macros (
    api_name TEXT NOT NULL,
    macro_name TEXT NOT NULL,
    PRIMARY KEY(api_name, macro_name)
);
```

### Процесс индексации

1. **Функции:** rg `^ *(int|uint32|shr_error_t|bcm_error_t) *bcm_\w+\(` по `include/bcm/*.h`
2. **Макросы:** rg `^#define\s+(\w+)` по всем `.h` файлам
3. **Chip guards:** rg `#if\s+defined\(BCM_\w+\)` рядом с функциями
4. **Модуль:** определяется по префиксу `bcm_<module>_*`

**Время индексации:** < 1 минуты (только заголовочные файлы, ~200 `include/bcm/` файлов).

---

## 7. Безопасность

- **Read-only:** сервер только читает файлы SDK.
- **Sandbox:** все пути проходят через `PathGuard.validate()`.
- **Subprocess whitelist:** разрешена только команда `rg` с параметрами.
- **Path traversal:** блокируются `..`, симлинки наружу, абсолютные пути вне SDK_ROOT.

```python
# Ключевой код безопасности (src/security/path_guard.py)
class PathGuard:
    def validate(self, path: str) -> Path:
        resolved = (self.sdk_root / path).resolve()
        if not str(resolved).startswith(str(self.sdk_root)):
            raise SecurityError(f"Path traversal: {resolved}")
        if resolved.is_symlink():
            raise SecurityError("Symlinks not allowed")
        return resolved
```

---

## 8. Логирование

- Каждый вызов tool логируется: имя, параметры (без секретов), статус, время выполнения.
- Формат: `{time} | {level} | {tool} | params={...} | status={success|error} | elapsed={ms}`.
- Уровень лога настраивается через `OPENBCM_MCP_LOG_LEVEL` (default: INFO).

---

## 9. Конфигурация

**Переменные окружения:**

| Переменная | Обязательность | Дефолт | Описание |
|------------|---------------|--------|----------|
| `OPENBCM_SDK_PATH` | Да | — | Путь к корню SDK |
| `OPENBCM_MCP_LOG_LEVEL` | Нет | INFO | Уровень лога |
| `OPENBCM_MCP_CACHE_DIR` | Нет | ./cache | Директория кэша |

**`.env.example`:**
```env
OPENBCM_SDK_PATH=/path/to/openbcm-sdk-6.5.27
OPENBCM_MCP_LOG_LEVEL=DEBUG
OPENBCM_MCP_CACHE_DIR=./cache
```

---

## 10. План реализации (по дням)

| День | Задачи | Результат |
|------|--------|-----------|
| **День 1** | Скелет проекта, MCP сервер (stdio), логирование, security (path guard) | Сервер запускается, логи пишутся |
| **День 2** | Индексация SDK (SQLite), `find_bcm_api` tool | Работает поиск API |
| **День 3** | `find_api_examples` (rg + CINT), `trace_implementation` (эвристики) | Работают 2 инструмента |
| **День 4** | `get_chip_info` (chip_map.json + rg), `find_cint_scripts` (бонус) | Работают 5 инструментов |
| **День 5** | Тесты (unit, security, интеграционные), README, документация, .env.example | Тесты проходят |
| **День 6** | Конфиг для IDE (mcp.json), отладка интеграции, запись логов вызовов | Интеграция работает |
| **День 7** | Buffer/доработки, финальная проверка по чеклисту ДЗ, сдача | Готово |

---

## 11. Чеклист соответствия ДЗ

- [x] MCP сервер запускается: `python -m src` → stdio transport
- [x] Минимум 2-4 инструмента: 4 основных + 1 бонусный
- [x] У каждого инструмента: имя, описание, JSON Schema параметров
- [x] Результат — структурированный JSON, не просто текст
- [x] Безопасность: sandbox, read-only, path traversal, subprocess whitelist
- [x] Логи вызовов: имя tool, параметры, статус, время
- [x] Интеграция с IDE: VS Code (CLine/Continue/OpenCode) через mcp.json
- [x] Пример конфигурации подключения: `README.md` + `docs/SETUP.md`
- [x] 5 проверочных запросов, 3+ приводят к вызову MCP tool
- [x] Секреты не закоммичены (в .gitignore, .env.example)
- [x] **CINT скрипты:** корректно определяются по расположению и заголовочным комментариям
- [x] **Связанные файлы:** `.log` и `.bcm` файлы отображаются рядом с CINT скриптами

---

## 12. Конфигурация подключения к IDE

Для VS Code + CLine/Continue (`.vscode/mcp.json` или `~/.config/Code/User/globalStorage/...`):

```json
{
  "servers": {
    "openbcm-helper": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src"],
      "env": {
        "OPENBCM_SDK_PATH": "/path/to/openbcm-sdk/sdk-6.5.27",
        "OPENBCM_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```
