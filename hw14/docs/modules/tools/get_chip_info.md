# `get_chip_info.py` — Информация о ASIC

## Назначение

Инструмент `get_chip_info` — получение сводки по ASIC: идентификаторы устройств, feature macros, поддерживаемые модули, примеры API и CINT скрипты.

## Параметры

| Параметр | Тип | Обязательный | Дефолт | Описание |
|----------|-----|-------------|--------|----------|
| `chip` | string | **Да** | — | Имя чипа (Tomahawk4, Trident3, Jericho2) |
| `include_apis` | boolean | Нет | `false` | Показать примеры API |
| `include_cint_scripts` | boolean | Нет | `false` | Показать CINT скрипты для этого чипа |

## Формат результата

```python
class ChipInfoResult(BaseModel):
    chip: str                    # Имя чипа
    dev_ids: list[str]           # Идентификаторы устройств
    feature_macros: list[str]    # Feature macros
    modules: list[str]           # Поддерживаемые модули
    soc_directories: list[str]   # Директории с SOC-специфичным кодом
    api_count_estimate: int      # Оценочное количество API
    example_apis: list[str]      # Примеры API
    cint_scripts: list[ChipCintScript]  # CINT скрипты для этого чипа
```

## Пример ответа

```json
{
  "ok": true,
  "result": {
    "chip": "Tomahawk4",
    "dev_ids": ["0xb964", "0xb965"],
    "feature_macros": ["BCM_TOMAHAWK4_SUPPORT", "BCM_56996_B0"],
    "modules": ["L2", "L3", "VLAN", "MPLS", "OAM"],
    "soc_directories": ["src/bcm/esw/tomahawk4"],
    "api_count_estimate": 45,
    "example_apis": ["bcm_vlan_create", "bcm_l2_addr_add", "bcm_l3_route_add"],
    "cint_scripts": [
      {"file": "src/examples/l3/route_basic.c", "header": "/* Tested on: Tomahawk4 */", "apis_used": ["bcm_l3_route_add"]}
    ]
  },
  "meta": {
    "elapsed_ms": 80,
    "source": "config"
  }
}
```

## Реализация

```python
async def run_get_chip_info(chip, chip_map, sdk_path, include_apis=False, include_cint_scripts=False) -> dict
```

1. Поиск чипа в `ChipMap` (JSON-конфиг)
2. Если чип не найден — возвращает список доступных чипов
3. При `include_apis=True` — поиск API через feature macros в заголовочных файлах
4. При `include_cint_scripts=True` — поиск CINT скриптов, содержащих имя чипа