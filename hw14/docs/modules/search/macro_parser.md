# `macro_parser.py` — Парсинг C-макросов

## Назначение

Парсинг C-макросов (`#define`, `#ifdef`, `#if defined`) и chip guard условий. Используется индексатором SDK и инструментом трассировки для определения доступности API на разных чипах.

## Классы

### `MacroDef`

```python
@dataclass
class MacroDef:
    name: str       # Имя макроса (BCM_TOMAHAWK4_SUPPORT)
    value: str      # Значение макроса (1, 0, или пусто)
    file: str       # Файл
    line: int       # Номер строки
```

## Функции

### `extract_macros()`

```python
def extract_macros(lines: list[str]) -> list[MacroDef]
```

Извлечение всех `#define` макросов из строк файла.

**Паттерн:** `#define NAME value`

### `extract_chip_guards()`

```python
def extract_chip_guards(lines: list[str], func_line: int) -> list[str]
```

Извлечение chip guard условий (`#if defined BCM_*_SUPPORT`) вокруг функции.

**Поиск:**
- До 20 строк перед функцией: `#if defined(BCM_*_SUPPORT)`
- До 20 строк после функции: `#elif defined(BCM_*_SUPPORT)`

**Пример:** `["BCM_TOMAHAWK4_SUPPORT", "BCM_TRIDENT3_SUPPORT"]`

### `extract_chip_conditions()`

```python
def extract_chip_conditions(lines: list[str], func_line: int) -> list[str]
```

Извлечение `SOC_IS_*` условий в окрестности функции (до 5 строк до, до 30 после).

**Пример:** `["SOC_IS_TOMAHAWK4(unit)"]`

## Регулярные выражения

| Паттерн | Назначение |
|---------|-----------|
| `DEFINE_PATTERN` | `#define NAME value` |
| `CHIP_GUARD_PATTERN` | `#if defined(BCM_*_SUPPORT)` |
| `SOC_IS_PATTERN` | `SOC_IS_*(...)` |
| `ELIF_GUARD_PATTERN` | `#elif defined(BCM_*_SUPPORT)` |

## Использование в проекте

- **SdkIndexer._index_macros()** — индексация всех макросов из `.h` файлов
- **trace_implementation.py** — извлечение chip conditions для каждого уровня цепочки