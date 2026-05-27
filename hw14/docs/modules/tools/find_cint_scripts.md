# `find_cint_scripts.py` — Поиск CINT скриптов

## Назначение

Инструмент `find_cint_scripts` — поиск CINT скриптов по функционалу, чипу или параметрам. CINT скрипты — это C-подобные скрипты для тестирования Broadcom ASIC.

## Параметры

| Параметр | Тип | Обязательный | Дефолт | Описание |
|----------|-----|-------------|--------|----------|
| `query` | string | **Да** | — | Поисковый запрос (функционал, чип, имя файла) |
| `chip` | string | Нет | — | Фильтр по чипу |
| `include_logs` | boolean | Нет | `false` | Включить логи вывода |
| `include_configs` | boolean | Нет | `false` | Включить .bcm конфиги |
| `include_full_source` | boolean | Нет | `false` | Показать полный исходник |

## Формат результата

```python
class CintScriptListResult(BaseModel):
    query: str                   # Поисковый запрос
    total_found: int             # Количество найденных скриптов
    scripts: list[CintScriptResult]  # Список скриптов
```

Каждый `CintScriptResult` содержит:
- `file` — путь к скрипту
- `header_comment` — заголовочный комментарий
- `apis_used` — API, используемые в скрипте
- `related_files` — связанные файлы (логи, конфиги)

## Пример ответа

```json
{
  "ok": true,
  "result": {
    "query": "vlan",
    "total_found": 2,
    "scripts": [
      {
        "file": "src/examples/vlan/vlan_create.c",
        "header_comment": "/*\n * Tested on: Tomahawk4\n * Tests: VLAN create / delete\n */",
        "apis_used": ["bcm_vlan_create", "bcm_vlan_destroy", "bcm_vlan_get"],
        "related_files": [
          {"path": "src/examples/vlan/vlan_create.bcm", "type": "config", "size_bytes": 256}
        ]
      }
    ]
  },
  "meta": {
    "elapsed_ms": 95,
    "source": "ripgrep"
  }
}
```

## Реализация

```python
async def run_find_cint_scripts(query, sdk_path, chip=None, include_logs=False, include_configs=False, include_full_source=False) -> dict
```

1. Поиск в директориях `src/examples/`, `cint/`, `diag/`
2. Поиск по содержимому и по имени файла через `rg_search`
3. Дедупликация по файлу
4. Проверка, что файл является CINT скриптом (`is_cint_script`)
5. Фильтр по чипу (проверка заголовка скрипта)
6. Извлечение заголовка и используемых API
7. При `include_logs`/`include_configs` — поиск связанных файлов