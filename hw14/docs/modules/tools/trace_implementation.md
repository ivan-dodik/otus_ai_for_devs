# `trace_implementation.py` — Трассировка цепочки реализации API

## Назначение

Инструмент `trace_api_implementation` — трассировка цепочки реализации от публичного API до chip-specific кода. Показывает, как вызов API проходит через уровни абстракции SDK.

## Параметры

| Параметр | Тип | Обязательный | Дефолт | Описание |
|----------|-----|-------------|--------|----------|
| `api` | string | **Да** | — | Имя API |
| `chip` | string | Нет | — | Фильтр по чипу |
| `max_depth` | integer | Нет | `3` | Глубина трассировки (max 7) |

## Формат результата

```python
class TraceResult(BaseModel):
    api: str                         # Имя API
    entry_point: TraceEntry          # Точка входа (публичное API)
    implementation_chain: list[TraceEntry]  # Цепочка реализации
    chip_specific_branches: list[ChipBranch]  # Chip-specific ветки
```

Каждый `TraceEntry` содержит:
- `level` — уровень вложенности (1 = entry point)
- `function` — имя функции
- `file` — файл
- `line` — номер строки
- `chip_conditions` — условия доступности для чипов (SOC_IS_*)
- `guard_pattern` — паттерн guard

## Пример ответа

```json
{
  "ok": true,
  "result": {
    "api": "bcm_l2_addr_add",
    "entry_point": {
      "level": 1,
      "function": "bcm_esw_l2_addr_add",
      "file": "src/bcm/esw/l2.c",
      "line": 245,
      "chip_conditions": [],
      "guard_pattern": ""
    },
    "implementation_chain": [
      {"level": 1, "function": "bcm_esw_l2_addr_add", "file": "src/bcm/esw/l2.c", "line": 245, "chip_conditions": [], "guard_pattern": ""},
      {"level": 2, "function": "bcm_esw_l2_addr_add_internal", "file": "src/bcm/esw/l2.c", "line": 310, "chip_conditions": ["SOC_IS_TOMAHAWK4(unit)"], "guard_pattern": ""}
    ],
    "chip_specific_branches": [
      {"condition": "SOC_IS_TOMAHAWK4(unit)", "functions": ["bcm_esw_l2_addr_add_internal"], "soc_file": "src/bcm/esw/tomahawk4/l2.c"}
    ]
  },
  "meta": {
    "elapsed_ms": 250,
    "source": "ripgrep",
    "max_depth_reached": 2
  }
}
```

## Реализация

```python
async def run_trace_implementation(api, sdk_path, chip=None, max_depth=3) -> dict
```

1. **Эвристика**: ищет `bcm_esw_<api>` в `src/` (ESW — Ethernet Switching wrapper)
2. **Entry point**: находит реализацию через `rg_search`
3. **Цепочка**: для каждого уровня ищет `_internal` / `_\w+` функции
4. **Chip conditions**: извлекает `SOC_IS_*` условия через `extract_chip_conditions`
5. **Chip-specific branches**: определяет файлы с chip-specific кодом
6. **Ограничение глубины**: `max_depth` (макс 7)