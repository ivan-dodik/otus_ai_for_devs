# `sdk_indexer.py` — Индексатор SDK

## Назначение

Главный класс индексации SDK — `SdkIndexer`. Сканирует заголовочные файлы SDK, парсит декларации BCM API, извлекает макросы и сохраняет всё в SQLite для быстрого поиска.

## Класс `SdkIndexer`

### Конструктор

```python
def __init__(self, sdk_path: Path, cache_dir: Path, chip_map: ChipMap) -> None
```

**Параметры:**
- `sdk_path` — путь к корню SDK
- `cache_dir` — директория для кэша (SQLite БД)
- `chip_map` — маппинг чипов для ассоциации макросов

### Класс `IndexStats`

```python
@dataclass
class IndexStats:
    functions_count: int  # Количество проиндексированных функций
    macros_count: int     # Количество макросов
    modules_count: int    # Количество модулей
    elapsed_ms: int       # Время индексации в миллисекундах
```

### Методы

| Метод | Описание |
|-------|----------|
| `index()` | Полная индексация SDK. Возвращает `IndexStats` |
| `search_api(name, chip, fuzzy)` | Поиск API в индексе |
| `get_stats()` | Получить статистику индекса |
| `ensure_indexed()` | Проверить, есть ли индекс. Если нет — запустить индексацию |
| `needs_reindex()` | Проверить, изменился ли SDK после последней индексации |

### `index()` — процесс индексации

```python
def index(self) -> IndexStats
```

1. Очищает старые данные из таблиц (`functions`, `function_params`, `macros`, `api_macros`)
2. Вызывает `_index_functions()` — сканирование `include/bcm/*.h`
3. Вызывает `_index_macros()` — сканирование всех `.h` файлов
4. Возвращает статистику

### `_index_functions()`

```python
def _index_functions(self) -> None
```

1. Ищет файлы с `bcm_` функциями через `rg_files()` в `include/bcm/`
2. Для каждого `.h` файла:
   - Читает содержимое
   - Удаляет C-комментарии
   - Ищет декларации по паттерну `(extern) return_type bcm_name(params);`
   - Извлекает модуль из префикса (`bcm_vlan_create` → `VLAN`)
   - Сохраняет в таблицу `functions`

### `_index_macros()`

```python
def _index_macros(self) -> None
```

1. Сканирует все `.h` файлы в `include/`
2. Извлекает `#define` макросы через `extract_macros()`
3. Для макросов вида `BCM_*_SUPPORT` пытается определить ассоциацию с чипом через `ChipMap`
4. Сохраняет в таблицу `macros`

### `search_api()`

```python
def search_api(self, name: str, chip: str | None = None, fuzzy: bool = False) -> list[dict]
```

1. **Точный поиск** — SQLite запрос по имени функции
2. **Фильтр по чипу** — если указан, фильтрует по chip_macros
3. **Fuzzy поиск** — если точный поиск не дал результатов и `fuzzy=True`, использует `rapidfuzz` для нечёткого поиска (порог 60%)

### `get_stats()`

```python
def get_stats(self) -> IndexStats
```

Возвращает количество функций, макросов и модулей из SQLite.

### `needs_reindex()`

```python
def needs_reindex(self) -> bool
```

Проверяет, изменились ли `.h` файлы после последней индексации, сравнивая время модификации.

## SQLite настройки

```python
conn.execute("PRAGMA journal_mode=WAL")   # WAL режим для конкурентного доступа
conn.execute("PRAGMA synchronous=OFF")     # Отключение синхронизации для скорости