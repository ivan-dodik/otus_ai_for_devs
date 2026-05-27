# `find_api_examples.py` — Поиск примеров использования API

## Назначение

Инструмент `find_api_examples` — поиск примеров использования API в C-коде и CINT скриптах. Возвращает фрагменты кода с контекстом, заголовки CINT скриптов и связанные файлы.

## Параметры

| Параметр | Тип | Обязательный | Дефолт | Описание |
|----------|-----|-------------|--------|----------|
| `api` | string | **Да** | — | Имя API (например, `bcm_l3_route_add`) |
| `source_type` | string | Нет | `"all"` | Фильтр: `all`, `c`, `cint`, `bcm_config` |
| `max_results` | integer | Нет | `10` | Максимум результатов (max 50) |
| `context_lines` | integer | Нет | `3` | Строк контекста (max 10) |
| `include_full_source` | boolean | Нет | `false` | Показать полный исходник CINT скрипта |

## Формат результата

```python
class ExampleListResult(BaseModel):
    api: str                     # Имя API
    total_found: int             # Общее количество найденных примеров
    examples: list[ExampleResult]  # Список примеров
```

Каждый `ExampleResult` содержит:
- `file` — путь к файлу
- `line` — номер строки
- `snippet` — фрагмент кода с контекстом
- `source_type` — тип источника (`c`, `cint`)
- `script_header` — заголовок CINT скрипта (если есть)
- `related_files` — связанные файлы (`.bcm`, `.log`)

## Пример ответа

```json
{
  "ok": true,
  "result": {
    "api": "bcm_l3_route_add",
    "total_found": 3,
    "examples": [
      {
        "file": "src/examples/l3/route_basic.c",
        "line": 45,
        "snippet": "    rv = bcm_l3_route_add(unit, &route);\n    if (rv != BCM_E_NONE) {\n        printf(\"Error: %s\\n\", bcm_errmsg(rv));\n    }",
        "source_type": "cint",
        "script_header": "/*\n * Tested on: Tomahawk4\n * Tests: L3 route add / delete\n */",
        "related_files": [
          {"path": "src/examples/l3/route_basic.bcm", "type": "config", "size_bytes": 128}
        ]
      }
    ]
  },
  "meta": {
    "elapsed_ms": 120,
    "source": "ripgrep"
  }
}
```

## Реализация

```python
async def run_find_api_examples(api, sdk_path, source_type="all", max_results=10, context_lines=3, include_full_source=False) -> dict
```

1. Поиск через `rg_search` с паттерном `{api}\\(` в `.c` и `.h` файлах
2. Фильтрация по `source_type` (cint/c/bcm_config)
3. Дедупликация по файлу
4. Для CINT скриптов — извлечение заголовка и связанных файлов
5. При `include_full_source=True` — чтение полного исходника