# Tech Context: OpenBCM Helper MCP Server

## Технологический стек

| Компонент | Технология | Версия | Назначение |
|-----------|-----------|--------|------------|
| Язык | Python | 3.13.7 | Основной язык |
| MCP протокол | `mcp` | ≥1.0.0 | MCP Python SDK |
| Валидация | `pydantic` | ≥2.0 | Схемы данных |
| Конфигурация | `pydantic-settings` | ≥2.0 | Загрузка из env |
| Логирование | `structlog` | ≥23.0 | Структурированное логирование |
| Нечёткий поиск | `rapidfuzz` | ≥3.5 | Поиск по частичному совпадению |
| JSON | `orjson` | ≥3.9 | Быстрая сериализация |
| БД | `sqlite3` | встроенный | Лёгкий индекс SDK |
| Поиск | `ripgrep` | системный | Быстрый текстовый поиск |
| Пакетный менеджер | `uv` | системный | Управление зависимостями |
| Тестирование | `pytest` | ≥8.0 | Unit + E2E тесты |

## Разработка и сборка

```bash
# Создание venv и установка зависимостей
uv venv
uv sync

# Запуск сервера
OPENBCM_SDK_PATH=/path/to/sdk python -m src

# Запуск тестов
uv run pytest tests/ -v

# Компиляция requirements.txt
uv pip compile pyproject.toml -o requirements.txt
```

## Технические ограничения

1. **stdio транспорт** — сервер работает через stdin/stdout (MCP stdio protocol)
2. **Read-only** — сервер только читает файлы SDK, никогда не пишет
3. **Subprocess whitelist** — разрешена только команда `rg`
4. **SDK доступен локально** — по пути из OPENBCM_SDK_PATH
5. **Python >= 3.10** — из-за синтаксиса type hints

## Зависимости (Python)

### Основные
- `mcp>=1.0.0` — MCP SDK
- `pydantic>=2.0` — валидация
- `pydantic-settings>=2.0` — env конфиг
- `structlog>=23.0` — логирование
- `rapidfuzz>=3.5` — нечёткий поиск
- `orjson>=3.9` — быстрый JSON

### Dev
- `pytest>=8.0` — тесты
- `pytest-asyncio>=0.24` — асинхронные тесты

## Зависимости системы
- `ripgrep` — установлен в системе (проверено через `rg --version`)

## Переменные окружения

| Переменная | Обязательность | Дефолт | Описание |
|------------|---------------|--------|----------|
| `OPENBCM_SDK_PATH` | Да | — | Путь к корню SDK |
| `OPENBCM_MCP_LOG_LEVEL` | Нет | INFO | Уровень лога |
| `OPENBCM_MCP_CACHE_DIR` | Нет | ./cache | Директория кэша |

## IDE интеграция

### Cline (VS Code)
- Конфиг: `.vscode/mcp.json`
- Транспорт: stdio
- Команда: `python -m src`

### Continue
- Конфиг: `~/.continue/config.json` или `docs/continue.json.example`
- Транспорт: stdio
- Команда: `python -m src`

### OpenCode
- Конфиг: согласно документации https://opencode.ai/docs/mcp-servers/
- Пример: `docs/opencode.json.example`

## Ссылки на документацию
- `docs/ARCHITECTURE.md` — технологический стек, переменные окружения, структура проекта
- `docs/modules/config/config.md` — детальная конфигурация Settings
- `docs/modules/server/logger.md` — настройка structlog
- `docs/modules/search/rg_search.md` — ripgrep обёртка
