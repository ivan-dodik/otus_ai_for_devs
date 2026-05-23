# Progress: LangChain Anime Recommendation Agent

## What Works
- **LLM Integration:** Ollama с llama3.1:8b (по умолчанию) и qwen3.5:9b-q4_K_M
- **Параметризация LLM:** temperature, top_p, num_predict, top_k с automatic model presets
- **9 LangChain-инструментов:** search_anime, get_anime_details, get_anime_by_genre, get_trending_anime, get_anime_info, get_tags, find_similar_anime, recommend_anime, search_anime_by_filter
- **Kitsu API:** Все эндпоинты работают, кэширование с TTL=5 мин, поддержка people/studio поиска
- **ReAct агент:** create_agent (langchain.agents) с MemorySaver для сессиonной памяти
- **Singleton pattern:** Агент переиспользуется между запросами
- **Scenario-based промпты:** 4 сценария (simple_query, multi_tool_chain, preference_conversation, error_handling)
- **Genre resolution:** Alias map для RU, EN, JP названий жанров
- **Franchise detection:** Исключение одноимённых тайтлов в find_similar_anime и recommend_anime
- **PreferenceProfile:** Genre scoring для персонализации
- **CLI:** Одиночный режим и интерактивный режим с prompt-toolkit и InMemoryHistory для истории ввода (в рамках сессии)
- **Flask Web UI:** Чат с Markdown-рендерингом, typing indicator, quick action buttons
- **Logging:** Python logging с --debug флагом
- **Тесты:** 86 unit + 6 E2E = 92 passed ✅
- **CI/CD:** GitHub Actions workflow

## What's Left to Build
- Нет — все задачи из task.md завершены

## Current Status
**Фаза:** Завершена ✅

Все 10 шагов рефакторинга реализованы и протестированы:
1. ✅ Параметризация LLM
2. ✅ Улучшение системного промпта
3. ✅ Переиспользование агента
4. ✅ Композитный recommend_anime
5. ✅ API кэширование
6. ✅ PreferenceProfile
7. ✅ Unit-тесты
8. ✅ E2E-тесты + CI
9. ✅ Markdown-рендеринг в UI
10. ✅ Документация

## Known Issues
- Нет известных проблем

## Evolution of Decisions

### 2026-05-23 22:30 — Рефакторинг
- **Было:** 4 инструмента, базовый промпт, без кэширования, без предпочтений, без тестов
- **Стало:** 8 инструментов, scenario-based промпты, кэширование, PreferenceProfile, 79 тестов

### 2026-05-23 20:00 — Аудит кода
- **Было:** logging.basicConfig() в kitsu_tools.py, 4 инструмента в документации
- **Стало:** logging.basicConfig() в config.py, 5 инструментов (добавлен get_anime_info)

### 2026-05-23 19:54 — DEBUG и перевод
- **Было:** print() для дебага, без перевода synopsis
- **Стало:** logger.debug() с --debug флагом, LLM переводит synopsis

### 2026-05-23 18:19 — Порядковые ссылки
- **Было:** LLM путался в порядковых ссылках
- **Стало:** Явный алгоритм из 6 шагов с разделением списков

### 2026-05-23 23:30 — Исправление обрезки ответов
- **Было:** `_format_anime_detail()` обрезала synopsis до 500 символов, ответы были нестабильными (212-601 символов)
- **Стало:** Полный synopsis из Kitsu API (1087 символов), стабильные ответы (506-565 символов), оптимизированы параметры LLM (temperature=0.1, num_predict=4096, request_timeout=300)

### 2026-05-24 00:00 — Исправление бага: одинаковые рекомендации
- **Проблема:** При запросе "Найди аниме похожее на..." для разных аниме (Cowboy Bebop, Sailor Moon, Naruto) возвращался **одинаковый** список рекомендаций
- **Корневая причина:** Kitsu API игнорирует `filter[genres]=bounty-hunter` и другие category slugs, возвращая дефолтный список популярных аниме. Эти slugs являются категориями/тегами, а не жанрами.
- **Исправление:**
  - `tools/kitsu_tools.py` — изменено `filter[genres]={slug}` → `filter[categories]={slug}` в функции `find_similar_anime`
  - `agent/prompts.py` — добавлены "КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА РАБОТЫ С ИНСТРУМЕНТАМИ" с примерами ✅/❌
- **Результат:** Теперь рекомендации различаются для разных аниме:
  - Cowboy Bebop → Steel Ball Run, Hellsing Ultimate, Baccano!, Trigun...
  - Sailor Moon → Chainsaw Man: Reze-hen, Sousou no Frieren, Tongari Boushi no Atelier...
  - Naruto → Jujutsu Kaisen, Attack on Titan, Hunter x Hunter, One Piece...
- **Тесты:** Все 34 unit-теста проходят ✅

### 2026-05-24 01:30 — Исправление падающих тестов config и deprecation warning
- **Проблема:** 5 тестов в test_config.py падали из-за несовпадения значений MODEL_PRESETS, deprecation warning от create_react_agent
- **Исправление:**
  - `config.py` — обновлены значения в MODEL_PRESETS:
    - `llama3.1:8b`: temperature=0.1→0.3, num_predict=4096→2048
    - `qwen3.5:9b-q4_K_M`: temperature=0.1→0.4, num_predict=4096→2048
  - `agent/agent.py` — обновлён импорт: `from langgraph.prebuilt import create_react_agent` → `from langchain.agents import create_agent`
  - `main.py` — добавлена история ввода через FileHistory (позже заменена на InMemoryHistory)
- **Результат:** Все 92 теста проходят ✅, deprecation warning устранён

### 2026-05-24 02:00 — Исправление истории ввода и pytest warning
- **Проблема 1:** История пользовательского ввода сохранялась в файл `.agent_history` и persist между сессиями
- **Исправление:** `main.py` — заменён `FileHistory` на `InMemoryHistory` (история только в рамках сессии)
- **Проблема 2:** PytestUnknownMarkWarning для `pytest.mark.e2e`
- **Исправление:** Создан `pytest.ini` с регистрацией custom mark
- **Результат:** Все 92 теста проходят ✅ без предупреждений
