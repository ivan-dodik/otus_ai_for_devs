# `rg_search.py` — Обёртка над ripgrep

## Назначение

Обёртка над системной утилитой `ripgrep` (rg) для быстрого текстового поиска. Использует subprocess для вызова rg с JSON-выходом. Единственная разрешённая subprocess команда (whitelist).

## Классы

### `RgMatch`

```python
@dataclass
class RgMatch:
    file: str              # Путь к файлу
    line: int              # Номер строки
    column: int            # Номер колонки
    text: str              # Текст строки с совпадением
    context_before: list[str]  # Строки контекста до совпадения
    context_after: list[str]   # Строки контекста после совпадения
```

### `RgSearchError`

Исключение при ошибке выполнения ripgrep (rg не найден, таймаут, ошибка выполнения).

## Функции

### `rg_search()`

```python
def rg_search(pattern: str, path: Path, file_pattern: str | None = None,
              context_lines: int = 0, max_results: int = 50) -> list[RgMatch]
```

Основная функция поиска. Выполняет `rg --json --no-heading` с указанными параметрами.

**Параметры:**
- `pattern` — регулярное выражение
- `path` — директория для поиска
- `file_pattern` — глоб-паттерн (например, `"*.h"`)
- `context_lines` — количество строк контекста
- `max_results` — максимальное количество результатов

**Возвращает:** список `RgMatch`

### `rg_count()`

```python
def rg_count(pattern: str, path: Path, file_pattern: str | None = None) -> int
```

Подсчёт количества совпадений. Использует `rg --count-matches`.

### `rg_files()`

```python
def rg_files(pattern: str, path: Path, file_pattern: str | None = None) -> list[Path]
```

Поиск файлов, содержащих совпадение. Использует `rg --files-with-matches`.

## Парсинг JSON-вывода

```python
def _parse_rg_json_output(output: str, context_lines: int = 0) -> list[RgMatch]
```

Парсит JSON-вывод ripgrep. Обрабатывает типы:
- `match` — совпадение
- `context` — строка контекста
- `begin` — начало нового файла (сброс контекста)

## Безопасность

- Единственная разрешённая subprocess команда
- Таймаут 30 секунд
- Проверка return code (0 = найдено, 1 = не найдено, остальное = ошибка)
- Ограничение `max_results` (дефолт 50)