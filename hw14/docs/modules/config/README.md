# Модуль конфигурации (`src/config.py`, `src/__main__.py`)

## Назначение

Модуль конфигурации отвечает за загрузку настроек из переменных окружения и .env файла, а также за точку входа в приложение.

## Файлы модуля

| Файл | Назначение |
|------|-----------|
| `config.py` | Настройки приложения (pydantic-settings) |
| `__main__.py` | Точка входа: создание сервера и запуск |

## Диаграмма зависимостей

```mermaid
graph TD
    MAIN["__main__.py"] --> CFG["config.py<br/>Settings"]
    MAIN --> SRV["server/mcp_server.py<br/>OpenBcmMcpServer"]
    MAIN --> LOG["server/logger.py<br/>setup_logger"]
    CFG --> ENV[".env file"]
    CFG --> ENV_VARS["Переменные окружения"]