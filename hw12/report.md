# Отчёт о проекте: Agent-based Anime Recommendation System

## 1. Описание проекта

Рекомендательная система аниме на основе LangChain-агента с локальной LLM. Агент использует Kitsu API для поиска и рекомендаций аниме, обрабатывает запросы на русском и английском языках, отслеживает предпочтения пользователя в рамках сессии.

## 2. LLM и API

### LLM: Ollama
- **Модель по умолчанию:** llama3.1:8b (8B параметров, Q4_K_M квантование, ~5 GB)
- **Альтернатива:** qwen3.5:9b-q4_K_M (9.7B параметров, Q4_K_M, ~6.5 GB)
- **URL:** http://localhost:11434
- **Функция вызова (function calling):** Поддерживается через LangChain ChatOllama
- **Русский язык:** Хорошая поддержка (llama3.1:8b и qwen3.5:9b-q4_K_M)

### LLM параметры (конфигурируемые)
| Параметр | llama3.1:8b | qwen3.5:9b-q4_K_M | Описание |
|----------|-------------|-------------------|----------|
| temperature | 0.3 | 0.4 | Случайность генерации |
| num_predict | 2048 | 2048 | Макс. токенов в ответе |
| top_p | 0.9 | 0.85 | Nucleus sampling |
| top_k | 40 | 50 | Топ-K sampling |

### API: Kitsu
- **Базовый URL:** https://kitsu.io/api/edge
- **Тип:** Публичное REST API, не требует аутентификации
- **Документация:** https://kitsu.docs.apiary.io

| Эндпоинт | Метод | Описание |
|-----------|-------|----------|
| /anime?filter[text]=... | GET | Поиск по названию |
| /anime/{id} | GET | Детали аниме по ID |
| /anime?filter[genres]=... | GET | Поиск по жанру |
| /trending/anime | GET | Тренды |
| /genres | GET | Список жанров |
| /anime/{id}/categories | GET | Жанры аниме по ID |

## 3. Инструменты агента

| # | Инструмент | Описание | Строки кода |
|---|-----------|----------|-------------|
| 1 | `search_anime(query)` | Поиск аниме по названию/ключевым словам | L463-L490 |
| 2 | `get_anime_details(anime_id)` | Детали аниме по ID | L493-L529 |
| 3 | `get_anime_by_genre(genre)` | Поиск по жанру с авто-разрешением | L532-L581 |
| 4 | `get_trending_anime()` | Тренды | L584-L611 |
| 5 | `get_anime_info(name)` | Поиск + детали в одном вызове | L614-L683 |
| 6 | `get_tags()` | Список доступных жанров | L686-L727 |
| 7 | `find_similar_anime(name)` | Похожие, исключая франшизы | L730-L857 |
| 8 | `recommend_anime(...)` | Персональные рекомендации | L861-L1087 |
| 9 | `search_anime_by_filter(...)` | Универсальный поиск (жанр, категория, человек, студия) | L1273-L1434 |

## 4. Тестовые запросы и результаты

### Запрос 1: "Найди аниме Cowboy Bebop"
- **Инструмент:** `search_anime`
- **Результат:** ✅ Найден Cowboy Bebop с рейтингом 87%, 26 серий
- **Язык:** Русский (агент перевёл synopsis)

### Запрос 2: "Покажи топ популярных аниме"
- **Инструмент:** `get_trending_anime`
- **Результат:** ✅ Cowboy Bebop, Samurai Champloo с рейтингами

### Запрос 3: "Подбери аниме в жанре комедия"
- **Инструмент:** `get_anime_by_genre`
- **Результат:** ✅ Space Dandy, Trigun с рейтингами

### Запрос 4: "Я смотрел Cowboy Bebop, мне понравилось. Подбери что-то похожее"
- **Цепочка вызовов:** `find_similar_anime("Cowboy Bebop")`
  1. Поиск жанров Cowboy Bebop (space, sci-fi, action)
  2. Поиск аниме по жанрам
  3. Исключение франшизы "Cowboy Bebop"
  4. Возврат Space Dandy как похожего
- **Результат:** ✅ Space Dandy найден как похожее аниме

### Запрос 5: "Расскажи про аниме Naruto"
- **Инструмент:** `get_anime_info` (search_anime → get_anime_details)
- **Результат:** ✅ Naruto: 220 серий, рейтинг 76%, synopsis переведён

### Запрос 6: "Рекомендация" (после предпочтений)
- **Инструмент:** `recommend_anime`
- **Контекст:** Пользователь сказал "мне понравилось Cowboy Bebop"
- **Результат:** ✅ Персонализированные рекомендации с учётом жанров

## 5. Контракт ответа

```json
{
  "status": "success" | "error",
  "action": "Описание выполненного действия",
  "data": "Отформатированные данные или null",
  "errors": "Описание ошибок или null"
}
```

**Пример успешного ответа:**
```json
{
  "status": "success",
  "action": "Поиск аниме по запросу: Cowboy Bebop",
  "data": "- [1] Cowboy Bebop (рейтинг: 87, серий: 26, статус: finished_airing)\n  Space western adventure...",
  "errors": null
}
```

**Пример ошибки:**
```json
{
  "status": "error",
  "action": "Поиск аниме по запросу: NonExistent",
  "data": null,
  "errors": "Аниме с названием 'NonExistent' не найдено"
}
```

## 6. Соответствие критериям оценки

| Критерий | Требование | Реализация | Строки |
|----------|-----------|------------|--------|
| 1. LLM с function calling | Ollama + ChatOllama | llama3.1:8b через ChatOllama | `agent/agent.py:65-71` |
| 2. 4+ инструмента | 4 инструмента | 9 инструментов | `tools/kitsu_tools.py` |
| 3. LangChain агент | ReAct/Graph agent | ReAct через create_agent | `agent/agent.py:65` |
| 4. Контракт ответа | JSON с Status/Action/Data/Errors | JSON через json.dumps | `tools/kitsu_tools.py:L470-L478` |
| 5. Цепочка вызовов | 2+ последовательно | find_similar_anime: genres→search→filter | `tools/kitsu_tools.py:L730-L857` |
| 6. Русский язык | Ответы на русском | System prompt + LLM translation | `agent/prompts.py:L9-L216` |
| 7. Тесты | Проверка работы | CLI + Flask + E2E тесты | `main.py`, `web/`, `tests/` |

## 7. Архитектура

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

## 8. Тестирование

### Unit-тесты (97 тестов)
| Файл | Тестов | Покрытие |
|------|--------|----------|
| `tests/test_session_store.py` | 22 | PreferenceProfile, SessionStore |
| `tests/test_kitsu_tools.py` | 28 | Genre resolution, franchise detection, formatting, caching |
| `tests/test_config.py` | 23 | Config, model presets, effective parameters, logging |
| `tests/test_e2e.py` | 6 | E2E тесты агента |
| Другие тесты | 18 | Вспомогательные тесты |

### E2E-тесты (6 тестов)
| Класс | Тест | Описание |
|-------|------|----------|
| TestE2ETrending | test_trending_query_russian | "что сейчас популярно?" |
| TestE2ETrending | test_what_to_watch_english | "what should I watch?" |
| TestE2EGenreSearch | test_genre_query_russian | "найди топ аниме жанра романтика" |
| TestE2EGenreSearch | test_genre_query_english | "find action anime" |
| TestE2EAnimeInfo | test_anime_info_query | "расскажи про Cowboy Bebop" |
| TestE2ESimilar | test_similar_anime_query | "найди похожее на Cowboy Bebop" |

### Результат
```
Unit-тесты: 97 passed ✅
E2E-тесты: 6 passed ✅ (с llama3.1:8b)
```

### CI/CD
- **GitHub Actions:** `.github/workflows/tests.yml`
- **Этапы:** linting (ruff), unit tests, E2E tests (conditional)
- **Python версии:** 3.12, 3.13