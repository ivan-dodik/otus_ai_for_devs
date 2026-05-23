# Active Context: LangChain Anime Recommendation Agent

## Current Focus
Добавление универсального инструмента поиска по фильтрам (person, studio, genre, category).

## Recent Changes
- **Универсальный инструмент search_anime_by_filter (2026-05-24 00:30):**
  - **Проблема:** Агент не мог найти аниме по композитору (например, "Найди аниме с музыкой Yoko Kanno") и начинал галлюцинировать
  - **Решение:** Добавлен универсальный инструмент `search_anime_by_filter(filter_type, filter_value, sort, limit)`
  - **Поддерживаемые фильтры:**
    - `person` — поиск по человеку (композитор, режиссёр, сэйю)
    - `studio` — поиск по студии-производителю
    - `genre` — поиск по жанру
    - `category` — поиск по категории/тегу
  - **Изменения:**
    - `tools/kitsu_tools.py` — добавлены `_search_person_by_name()`, `_search_studio_by_name()`, `search_anime_by_filter`
    - `agent/prompts.py` — добавлены сценарии использования нового инструмента
    - `tests/test_kitsu_tools.py` — добавлено 14 новых тестов
  - **Результат:** 47 тестов проходят ✅, агент теперь может искать аниме по композиторам, студиям и т.д.

- **Исправление бага: одинаковые рекомендации (2026-05-24 00:00):**
  - **Проблема:** При запросе "Найди аниме похожее на..." для разных аниме возвращался **одинаковый** список рекомендаций
  - **Корневая причина:** Kitsu API игнорирует `filter[genres]=bounty-hunter` и другие category slugs, возвращая дефолтный список популярных аниме. Эти slugs являются категориями/тегами, а не жанрами.
  - **Исправление:** В `tools/kitsu_tools.py` изменено `filter[genres]={slug}` → `filter[categories]={slug}` в функции `find_similar_anime`
  - **Усиление промпта:** Добавлены "КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА РАБОТЫ С ИНСТРУМЕНТАМИ" в `agent/prompts.py`
  - **Результат:** Теперь рекомендации различаются:
    - Cowboy Bebop → Steel Ball Run, Hellsing Ultimate, Baccano!, Trigun...
    - Sailor Moon → Chainsaw Man: Reze-hen, Sousou no Frieren, Tongari Boushi no Atelier...
    - Naruto → Jujutsu Kaisen, Attack on Titan, Hunter x Hunter, One Piece...

- **Исправление обрезки ответов (2026-05-23 23:30):**
  - Найдена причина: `_format_anime_detail()` обрезала synopsis до 500 символов
  - Исправлено: теперь передается полный synopsis из Kitsu API
  - Оптимизированы параметры LLM: temperature=0.1, num_predict=4096, request_timeout=300
  - Добавлен `request_timeout` в `ChatOllama`

- **Масштабный рефакторинг (2026-05-23 22:30):**
  - `config.py` — добавлены OLLAMA_TEMPERATURE, OLLAMA_NUM_PREDICT, OLLAMA_TOP_P, OLLAMA_TOP_K, MODEL_PRESETS, effective_* свойства, setup_logging()
  - `agent/prompts.py` — переписан системный промпт с scenario-based guidance (4 сценария)
  - `agent/agent.py` — singleton pattern для переиспользования агента, reset_agent() для тестов
  - `tools/kitsu_tools.py` — добавлен recommend_anime (композитный инструмент), API кэширование, genre resolution, franchise detection
  - `web/session_store.py` — PreferenceProfile с genre scoring
  - `web/templates/index.html` — marked.js для Markdown, typing indicator, quick action buttons
  - `tests/` — 73 unit-теста + 6 E2E-тестов, все проходят ✅
  - `.github/workflows/tests.yml` — CI workflow

## Next Steps
1. Все задачи завершены
2. Тестирование пройдено: 47 тестов в test_kitsu_tools.py ✅
3. Документация обновлена: CHANGES.md

## Completed
| # | Task | Status |
|---|------|--------|
| 1 | Параметризация LLM (config.py) | ✅ |
| 2 | Улучшение системного промпта (agent/prompts.py) | ✅ |
| 3 | Singleton pattern для агента (agent/agent.py) | ✅ |
| 4 | Композитный recommend_anime инструмент | ✅ |
| 5 | API кэширование с TTL=5 мин | ✅ |
| 6 | PreferenceProfile для сессий | ✅ |
| 7 | Unit-тесты (47 тестов в test_kitsu_tools.py) | ✅ |
| 8 | E2E-тесты + CI | ✅ |
| 9 | Markdown-рендеринг в UI | ✅ |
| 10 | Обновление документации | ✅ |
| 11 | Универсальный search_anime_by_filter | ✅ |

## Active Decisions
- **Model presets:** llama3.1:8b (temp=0.3) и qwen3.5:9b-q4_K_M (temp=0.4) — автоматический выбор по имени модели
- **Scenario-based prompts:** 4 сценария вместо одного длинного правила
- **Composite tools:** recommend_anime и find_similar_anime выполняют полный пайплайн внутри одного инструмента (LLM не нужно вызывать несколько инструментов)
- **API caching:** TTL=5 минут для снижения нагрузки на Kitsu API
- **Preference tracking:** Genre scoring в PreferenceProfile для персонализации
- **Singleton agent:** Переиспользование агента между запросами для экономии ресурсов Ollama

## Important Patterns
- Все инструменты возвращают JSON с контрактом: Status/Action/Data/Errors
- `_cached_make_request()` с TTL=5 мин для всех API вызовов
- `_resolve_genre_slug()` с alias map (RU, EN, JP) для мультиязычности
- `_extract_franchise_words()` + `_is_same_franchise()` для исключения одноимённых тайтлов
- `PreferenceProfile.add_like()` автоматически извлекает жанры и обновляет scoring

## Learnings
- `logging.basicConfig(force=True)` (Python 3.8+) — единственный надёжный способ изменить уровень логирования после инициализации
- `responses.RequestsMock` как context manager проверяет все зарегистрированные mocks — используйте per-test fixtures вместо shared
- `setup_method` с `@responses.activate` имеет wrong signature в pytest — используйте fixture вместо этого
- LLM лучше работает с композитными инструментами, чем с цепочками вызовов нескольких инструментов