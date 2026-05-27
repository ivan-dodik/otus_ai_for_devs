# Настройка OpenBCM Helper MCP Server

## Предварительные требования

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) — пакетный менеджер
- [ripgrep](https://github.com/BurntSushi/ripgrep) — текстовый поиск
- OpenBCM SDK (например, `sdk-6.5.27`)
- VS Code + Cline (или Continue, OpenCode)

## Установка

```bash
# Клонирование репозитория
git clone <repo-url> openbcm-helper-mcp
cd openbcm-helper-mcp

# Создание venv и установка зависимостей
uv venv
uv sync

# Настройка .env
cp .env.example .env
# Отредактируйте .env: укажите путь к SDK
```

## Настройка .env

```env
OPENBCM_SDK_PATH=/home/user/openbcm/sdk-6.5.27
OPENBCM_MCP_LOG_LEVEL=INFO
OPENBCM_MCP_CACHE_DIR=./cache
```

## Подключение к IDE

### VS Code + Cline

1. Откройте `.vscode/mcp.json` или создайте его
2. Скопируйте конфигурацию:

```json
{
  "servers": {
    "openbcm-helper": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "src"],
      "env": {
        "OPENBCM_SDK_PATH": "/path/to/openbcm-sdk-6.5.27",
        "OPENBCM_MCP_LOG_LEVEL": "INFO",
        "OPENBCM_MCP_CACHE_DIR": "./cache"
      }
    }
  }
}
```

3. Перезапустите Cline
4. Проверьте подключение: отправьте "ping"

### Continue

1. Откройте `~/.continue/config.json`
2. Добавьте сервер из `docs/continue.json.example`
3. Перезапустите Continue

### OpenCode

1. Следуйте документации: https://opencode.ai/docs/mcp-servers/
2. Используйте пример из `docs/opencode.json.example`

## Управление проектом

Для удобства предусмотрен скрипт `run.sh`:

```bash
# Запуск сервера
./run.sh

# Остановка сервера
./run.sh stop

# Полная очистка
./run.sh clean

# Перезапуск с очисткой
./run.sh restart
```

## Проверка

```bash
# Прямой запуск сервера (вручную)
OPENBCM_SDK_PATH=/path/to/sdk uv run python -m src

# Или через скрипт
./run.sh

# Ожидаемый вывод при прямом запуске:
# [info     ] Starting OpenBCM Helper MCP Server ...
# [info     ] server_start ...
