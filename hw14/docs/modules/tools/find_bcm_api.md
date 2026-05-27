# `find_bcm_api.py` — Поиск декларации BCM API

## Назначение

Инструмент `find_bcm_api` — поиск декларации BCM API в заголовочных файлах SDK. Возвращает сигнатуру функции, параметры, модуль, файл и связанные API.

## Параметры

| Параметр | Тип | Обязательный | Дефолт | Описание |
|----------|-----|-------------|--------|----------|
| `api` | string | **Да** | — | Имя API (например, `bcm_vlan_create`) |
| `chip` | string | Нет | `"all"` | Фильтр по чипу (Tomahawk4, Trident3, all) |
| `fuzzy` | boolean | Нет | `false` | Включить нечёткий поиск при отсутствии точного совпадения |

## Формат результата

```python
class ApiResult(BaseModel):
    name: str                    # Имя API
    signature: str               # Полная сигнатура функции
    module: str                  # Модуль (VLAN, L2, L3)
    header: str                  # Путь к заголовочному файлу
    line: int                    # Номер строки
    description: str             # Описание API
    parameters: list[ParameterInfo]  # Список параметров
    returns: ReturnInfo          # Информация о возвращаемом значении
    chip_availability: list[str] # Список чипов, где доступно API
    related_apis: list[str]      # Связанные API
```

## Пример ответа

```json
{
  "ok": true,
  "result": {
    "name": "bcm_vlan_create",
    "signature": "int bcm_vlan_create(int unit, bcm_vlan_t vlan)",
    "module": "VLAN",
    "header": "include/bcm/vlan.h",
    "line": 142,
    "description": "Create a VLAN",
    "parameters": [
      {"name": "unit", "type": "int", "description": "Unit number"},
      {"name": "vlan", "type": "bcm_vlan_t", "description": "VLAN ID"}
    ],
    "returns": {"type": "int", "description": "BCM_E_NONE on success"},
    "chip_availability": ["Tomahawk4", "Trident3"],
    "related_apis": ["bcm_vlan_destroy", "bcm_vlan_get", "bcm_vlan_list"]
  },
  "meta": {
    "elapsed_ms": 15,
    "source": "sqlite"
  }
}
```

## Реализация

```python
async def run_find_bcm_api(api: str, indexer: SdkIndexer, chip: str = "all", fuzzy: bool = False) -> dict
```

1. Поиск в SQLite-индексе через `indexer.search_api(name, chip, fuzzy)`
2. Если не найдено — fallback с `fuzzy=True`
3. Если всё ещё не найдено — возвращает ошибку
4. Парсит параметры из строки `params_str`
5. Определяет связанные API из того же модуля