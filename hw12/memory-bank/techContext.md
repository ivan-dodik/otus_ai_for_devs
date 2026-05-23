# Tech Context: LangChain Anime Recommendation Agent

## Technologies

### Backend
- **Python 3.10+** с type hints
- **LangChain >= 0.3.0** — фреймворк для работы с LLM
- **LangGraph >= 0.2.0** — create_react_agent для ReAct-агента
- **Flask >= 3.0.0** — веб-фреймворк для API и UI
- **python-dotenv >= 1.0.0** — загрузка .env файлов
- **requests >= 2.31.0** — HTTP клиент для Kitsu API
- **prompt-toolkit >= 3.0.0** — интерактивный CLI с history и editing

### LLM
- **Ollama** — локальный сервер для LLM
- **llama3.1:8b** — модель по умолчанию (8B params, Q4_K_M, ~5 GB)
- **qwen3.5:9b-q4_K_M** — альтернатива (9.7B params, Q4_K_M, ~6.5 GB)

### API
- **Kitsu API** — публичное REST API для данных об аниме
- **Base URL:** https://kitsu.io/api/edge
- **Аутентификация:** не требуется
- **Rate limiting:** in-memory кэш с TTL=5 минут

### Тестирование
- **pytest >= 8.0.0** — фреймворк для тестов
- **pytest-asyncio >= 0.24.0** — поддержка async тестов
- **responses >= 0.24.0** — HTTP mocking для тестов
- **ruff >= 0.8.0** — линтер и форматтер

### CI/CD
- **GitHub Actions** — автоматический запуск тестов и линтинга
- **Python 3.12, 3.13** — целевые версии

## Development Setup

### Установка
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Запуск Ollama
```bash
# Модель по умолчанию
ollama pull llama3.1:8b

# Альтернативная модель
ollama pull qwen3.5:9b-q4_K_M
```

### Запуск приложения
```bash
# CLI режим
python main.py "запрос"

# Интерактивный режим
python main.py --interactive

# С дебаг-выводом
python main.py --interactive --debug

# Flask Web UI
export FLASK_APP=web/app.py
flask run
```

### Запуск тестов
```bash
# Все тесты
python -m pytest tests/ -v

# Только unit-тесты
python -m pytest tests/test_session_store.py tests/test_kitsu_tools.py tests/test_config.py -v

# Только E2E-тесты (требует запущенный Ollama)
python -m pytest tests/test_e2e.py -v

# Только линтинг
ruff check .
```

## Configuration

### Environment Variables (.env)
| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| OLLAMA_BASE_URL | http://localhost:11434 | URL Ollama сервера |
| OLLAMA_MODEL | llama3.1:8b | Модель LLM |
| OLLAMA_TEMPERATURE | (auto from preset) | Temperature для генерации |
| OLLAMA_NUM_PREDICT | (auto from preset) | Макс. токенов в ответе |
| OLLAMA_TOP_P | (auto from preset) | Nucleus sampling |
| OLLAMA_TOP_K | (auto from preset) | Top-K sampling |
| FLASK_PORT | 5000 | Порт Flask сервера |
| FLASK_DEBUG | false | Debug режим Flask |
| DEBUG | false | Debug режим логирования |

### Model Presets
| Модель | temperature | num_predict | top_p | top_k |
|--------|-------------|-------------|-------|-------|
| llama3.1:8b | 0.3 | 2048 | 0.9 | 40 |
| qwen3.5:9b-q4_K_M | 0.4 | 2048 | 0.85 | 50 |

## Project Structure

```
langchain/
├── config.py                  # Конфигурация и logging setup
├── main.py                    # CLI entry point
├── requirements.txt           # Зависимости
├── .env.example              # Пример конфигурации
├── .env                      # Локальная конфигурация (gitignored)
├── agent/
│   ├── __init__.py
│   ├── agent.py              # Singleton agent, process_query
│   └── prompts.py            # System prompt с scenario-based guidance
├── tools/
│   ├── __init__.py
│   └── kitsu_tools.py        # 8 инструментов + вспомогательные функции
├── web/
│   ├── __init__.py
│   ├── app.py                # Flask factory
│   ├── routes.py             # API endpoints
│   ├── session_store.py      # SessionStore + PreferenceProfile
│   └── templates/
│       └── index.html        # Web UI с marked.js
├── tests/
│   ├── conftest.py           # Shared mock fixtures
│   ├── test_session_store.py # PreferenceProfile tests
│   ├── test_kitsu_tools.py   # Tools tests
│   ├── test_config.py        # Config tests
│   └── test_e2e.py           # E2E integration tests
├── .github/
│   └── workflows/
│       └── tests.yml         # CI workflow
├── memory-bank/              # Memory Bank для Cline
│   ├── activeContext.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── progress.md
│   ├── projectbrief.md
│   ├── api.md
│   └── testing.md
├── .clinerules/              # Инструкции для Cline
│   ├── coding-standards.md
│   └── decision-log.md
├── CHANGES.md                # История изменений
├── PROMPTS.md                # История промптов
├── report.md                 # Отчёт о проекте
├── README.md                 # Документация
└── agent-prompts.md          # Синхронизированный системный промпт
```

## Dependencies Graph

```
main.py / web/routes.py
    └── agent/agent.py
            └── langchain_ollama.ChatOllama
            └── langgraph.create_react_agent
            └── agent/prompts.py
            └── tools/kitsu_tools.py
                    └── requests
                    └── langchain_core.tools.tool
    └── web/session_store.py
    └── config.py
            └── python-dotenv.load_dotenv
            └── logging
```

## Key External Services

### Kitsu API
- **Docs:** https://kitsu.docs.apiary.io
- **Endpoints используемые:**
  - GET /anime?filter[text]=...
  - GET /anime/{id}
  - GET /anime?filter[genres]=...
  - GET /trending/anime
  - GET /genres
  - GET /anime/{id}/categories

### Ollama API
- **Docs:** https://ollama.ai/docs
- **Endpoints используемые:**
  - POST /api/chat — чат с LLM
  - GET /api/tags — список моделей