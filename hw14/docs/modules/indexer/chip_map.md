# `chip_map.py` — Маппинг чипов

## Назначение

Загрузка и предоставление маппинга имён чипов на их характеристики (dev ids, feature macros, модули). Данные загружаются из JSON-файла `config/chip_map.json`.

## Класс `ChipMap`

### Конструктор

```python
def __init__(self, config_path: Path) -> None
```

Загружает маппинг из JSON-файла.

**Параметры:**
- `config_path` — путь к `config/chip_map.json`

### Методы

| Метод | Описание |
|-------|----------|
| `get_chip(name)` | Получить информацию о чипе по имени |
| `list_chips()` | Список всех известных чипов |
| `get_feature_macros(chip)` | Получить feature macros для чипа |

### `get_chip()`

```python
def get_chip(self, name: str) -> dict | None
```

Поиск чипа по имени:
1. Точное совпадение
2. Частичное совпадение (case-insensitive)

**Возвращает:** словарь с данными чипа или `None`.

### `list_chips()`

```python
def list_chips() -> list[str]
```

Возвращает список всех известных имён чипов.

## Формат JSON

```json
{
  "Tomahawk4": {
    "dev_ids": ["0xb964", "0xb965"],
    "feature_macros": ["BCM_TOMAHAWK4_SUPPORT", "BCM_56996_B0"],
    "modules": ["L2", "L3", "VLAN", "MPLS", "OAM"],
    "soc_dirs": ["src/bcm/esw/tomahawk4"],
    "example_apis": ["bcm_vlan_create", "bcm_l2_addr_add"]
  },
  "Trident3": {
    "dev_ids": ["0xb870"],
    "feature_macros": ["BCM_TRIDENT3_SUPPORT"],
    "modules": ["L2", "L3", "VLAN"],
    "soc_dirs": ["src/bcm/esw/trident3"],
    "example_apis": ["bcm_vlan_create", "bcm_l2_addr_add"]
  }
}
```

## Использование в проекте

- **OpenBcmMcpServer** — загружает `ChipMap` при инициализации
- **SdkIndexer** — использует для ассоциации макросов с чипами
- **get_chip_info.py** — основной потребитель для получения информации о чипе