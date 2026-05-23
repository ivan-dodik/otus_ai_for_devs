# System Patterns: LangChain Anime Recommendation Agent

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Пользователь                           │
│  (CLI: python main.py --interactive / Flask Web UI)         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    main.py / web/routes.py                  │
│              CLI entry point / Flask API endpoints          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   agent/agent.py                            │
│         create_react_agent(llm, tools, prompt)              │
│         process_query() / clear_session()                   │
│         get_agent() [singleton] / reset_agent()             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              tools/kitsu_tools.py                           │
│  ┌──────────┬────────────┬──────────────┬────────────────┐  │
│  │search    │get_details │get_by_genre  │get_trending    │  │
│  │_anime    │_anime      │_anime       │_anime          │  │
│  └──────────┴────────────┴──────────────┴────────────────┘  │
│  ┌──────────┬────────────┬──────────────┬────────────────┐  │
│  │get_info  │get_tags   │find_similar  │recommend       │  │
│  │_anime    │          │_anime       │_anime           │  │
│  └──────────┴────────────┴──────────────┴────────────────┘  │
│                                                             │
│  Вспомогательные функции:                                   │
│  - _cached_make_request() [TTL=5min]                       │
│  - _resolve_genre_slug() [alias map]                       │
│  - _get_anime_genres(), _search_anime_by_name()            │
│  - _extract_franchise_words(), _is_same_franchise()        │
│  - _format_anime_list(), _format_anime_detail()            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Ollama (localhost:11434)                       │
│         llama3.1:8b / qwen3.5:9b-q4_K_M                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Kitsu API (https://kitsu.io/api/edge)          │
│         Публичное API без аутентификации                    │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Singleton Agent Pattern
**Файл:** `agent/agent.py`

Агент создаётся один раз и переиспользуется между запросами. Это экономит ресурсы Ollama и сохраняет контекст беседы.

```python
_agent_instance: tuple | None = None

def get_agent(session_id: str | None = None):
    global _agent_instance
    if _agent_instance is None:
        llm = ChatOllama(...)
        tools = [...]
        prompt = ...
        agent = create_react_agent(llm, tools, prompt)
        _agent_instance = agent
    return _agent_instance

def reset_agent():
    global _agent_instance
    _agent_instance = None
```

### 2. Composite Tool Pattern
**Файл:** `tools/kitsu_tools.py`

Композитные инструменты выполняют полный пайплайн внутри одной функции, избегая проблем с каскадными вызовами LLM.

```python
@tool
def recommend_anime(liked_anime: str, ...):
    # 1. Извлечение жанров из liked_anime
    # 2. Поиск аниме по жанрам
    # 3. Фильтрация франшиз
    # 4. Агрегация и ранжирование
    # 5. Возврат JSON
```

### 3. API Caching Pattern
**Файл:** `tools/kitsu_tools.py`

In-memory кэш с TTL=5 минут для снижения нагрузки на Kitsu API.

```python
_api_cache: Dict[str, tuple[float, Dict]] = {}

def _cached_make_request(url: str):
    if url in cache and now - timestamp < TTL:
        return cache[url][1]
    data = _make_request(url)
    cache[url] = (now, data)
    return data
```

### 4. Genre Resolution Pattern
**Файл:** `tools/kitsu_tools.py`

Мультиязычное разрешение жанров через alias map и API.

```python
GENRE_ALIAS_MAP = {
    "романтика": "romance",
    "экшн": "action",
    "magical girl": "mahou-shoujo",
    ...
}

def _resolve_genre_slug(genre: str):
    # 1. Alias map
    # 2. Exact match on name
    # 3. Exact match on slug
    # 4. Substring match on name
    # 5. Substring match on slug
```

### 5. Franchise Detection Pattern
**Файл:** `tools/kitsu_tools.py`

Исключение одноимённых тайтлов для рекомендаций.

```python
def _extract_franchise_words(title: str) -> List[str]:
    # Удаление скобок, фильтрация коротких слов, топ-2 значимых

def _is_same_franchise(title: str, franchise_words: List[str]) -> bool:
    return any(word.lower() in title.lower() for word in franchise_words)
```

### 6. Preference Profile Pattern
**Файл:** `web/session_store.py`

Отслеживание предпочтений пользователя с genre scoring.

```python
class PreferenceProfile:
    liked: Dict[str, Dict]  # title -> {genres, ...}
    disliked: Set[str]
    viewed: Set[str]
    genre_scores: Dict[str, int]

    def add_like(title, genres):
        # Добавление аниме и обновление genre_scores
```

### 7. Response Contract Pattern
**Файл:** `tools/kitsu_tools.py`

Все инструменты возвращают JSON с единым контрактом.

```json
{
  "status": "success" | "error",
  "action": "Описание действия",
  "data": "Данные или null",
  "errors": "Ошибки или null"
}
```

## Configuration Flow

```
.env / .env.example
    │
    ▼
config.py (load_dotenv → Config class)
    │
    ├─→ OLLAMA_BASE_URL, OLLAMA_MODEL
    ├─→ OLLAMA_TEMPERATURE, OLLAMA_NUM_PREDICT
    ├─→ OLLAMA_TOP_P, OLLAMA_TOP_K
    ├─→ MODEL_PRESETS (llama3.1:8b, qwen3.5:9b-q4_K_M)
    ├─→ effective_* properties (automatic preset selection)
    ├─→ FLASK_PORT, FLASK_DEBUG
    └─→ DEBUG
    │
    ▼
setup_logging(debug) — force=True для перезаписи basicConfig
```

## Test Architecture

```
tests/
├── conftest.py              — Shared mock fixtures (mock_api, genre_mock_api)
├── test_session_store.py    — PreferenceProfile (22 tests)
├── test_kitsu_tools.py      — Genre resolution, formatting, caching (28 tests)
├── test_config.py           — Config, presets, effective params (23 tests)
└── test_e2e.py              — Full pipeline with mocked API (6 tests)
```

**Ключевые паттерны тестирования:**
- Per-test fixtures вместо shared fixture с множеством mocks
- `clean_env` fixture для isolation environment variables
- Module reload для тестирования изменений env vars
- `responses.RequestsMock` для HTTP mocking