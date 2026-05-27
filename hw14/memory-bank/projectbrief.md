# Project Brief: OpenBCM Helper MCP Server

## Название проекта
`openbcm-helper-mcp`

## Цель
MCP-сервер для навигации по OpenBCM SDK. Помогает AI-ассистентам находить API, искать примеры использования (включая CINT скрипты), трассировать цепочки реализации и получать информацию о доступности функций на разных ASIC.

## Ключевые требования
1. MCP-сервер работает через stdio транспорт
2. Минимум 2-4 инструмента (реализовано 7)
3. Каждый инструмент имеет имя, описание, JSON Schema параметров
4. Результат — структурированный JSON
5. Безопасность: sandbox, read-only, path traversal protection, subprocess whitelist
6. Логирование каждого вызова
7. Интеграция с IDE: VS Code + Cline (основная), Continue, OpenCode

## Инструменты (7)
1. `ping` — health-check сервера
2. `get_sdk_info` — информация о SDK
3. `find_bcm_api` — поиск декларации API
4. `find_api_examples` — поиск примеров использования
5. `trace_api_implementation` — трассировка цепочки реализации
6. `get_chip_info` — информация о ASIC
7. `find_cint_scripts` — поиск CINT скриптов

## Ссылки
- task.md — домашнее задание
- mcp_requirements.md — детальные требования к MVP
- PLAN.md — пошаговый план реализации
- `docs/ARCHITECTURE.md` — архитектура проекта с Mermaid-диаграммами
- `docs/modules/` — детальная документация по каждому модулю и файлу
- `docs/SETUP.md` — инструкция по подключению к IDE
