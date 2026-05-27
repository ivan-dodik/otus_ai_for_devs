# `cint_parser.py` — Парсинг CINT скриптов

## Назначение

Парсинг заголовков CINT скриптов — C-подобных скриптов для тестирования Broadcom ASIC. CINT скрипты содержат многострочные комментарии в начале файла с описанием, чипом, портами и тестами.

## Константы

```python
CINT_DIRECTORIES = {"src/examples", "cint", "diag"}
```

Директории, в которых обычно находятся CINT скрипты.

## Функции

### `is_cint_script()`

```python
def is_cint_script(file_path: Path, sdk_root: Path | None = None) -> bool
```

Проверка, является ли файл CINT скриптом.

**Критерии:**
1. Файл находится в директориях `src/examples/`, `cint/`, `diag/`
2. ИЛИ файл имеет расширение `.c` и характерный заголовочный комментарий (`"Tested on"` или `"Tests:"`)

### `extract_script_header()`

```python
def extract_script_header(file_path: Path) -> str | None
```

Извлечение многострочного комментария из начала файла (первые 5-30 строк).

**Возвращает:** текст заголовочного комментария или `None`.

### `parse_header_comment()`

```python
def parse_header_comment(comment: str) -> dict
```

Парсинг заголовочного комментария CINT скрипта.

**Возвращает:**
```python
{
    "chip": "Tomahawk4",       # Чип из "Tested on:"
    "ports": "1, 2, 3",        # Порты из "Ports:"
    "description": "...",      # Первая непустая строка
    "tests": ["create", "delete"]  # Тесты из "Tests:"
}
```

### `extract_used_apis()`

```python
def extract_used_apis(file_path: Path, max_lines: int = 200) -> list[str]
```

Извлечение имён BCM API, используемых в скрипте (первые `max_lines` строк).

**Паттерн:** `bcm_\w+\(`

**Пример:** `["bcm_vlan_create", "bcm_vlan_destroy", "bcm_vlan_get"]`

## Пример CINT скрипта

```c
/*
 * VLAN create/destroy example
 * Tested on: Tomahawk4
 * Ports: 1, 2, 3
 * Tests: create / delete / get
 */
int test_vlan() {
    int rv;
    rv = bcm_vlan_create(unit, 100);
    /* ... */
}
```

## Использование в проекте

- **find_api_examples.py** — определение CINT скриптов, извлечение заголовков и API
- **get_chip_info.py** — поиск CINT скриптов для конкретного чипа
- **find_cint_scripts.py** — основной инструмент поиска CINT скриптов