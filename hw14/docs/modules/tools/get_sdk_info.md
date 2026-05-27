# `get_sdk_info.py` — Информация о SDK

## Назначение

Инструмент `get_sdk_info` — получение информации о SDK: версия, путь, статус индексации, количество API и модулей.

## Параметры

| Параметр | Тип | Обязательный | Дефолт | Описание |
|----------|-----|-------------|--------|----------|
| `include_modules` | boolean | Нет | `false` | Показать список модулей |

## Формат результата

```python
class SdkInfoResult(BaseModel):
    sdk_path: str              # Путь к корню SDK
    version: str               # Версия SDK
    indexed: bool              # Индекс построен
    modules_count: int         # Количество модулей
    apis_count: int            # Общее количество API
    cache_dir: str             # Директория кэша
    modules: list[ModuleInfo]  # Список модулей (если запрошено)
```

## Пример ответа

```json
{
  "ok": true,
  "result": {
    "sdk_path": "/opt/bcm-sdk",
    "version": "6.5.27",
    "indexed": true,
    "modules_count": 12,
    "apis_count": 1542,
    "cache_dir": "/home/user/project/cache",
    "modules": [
      {"name": "L2", "api_count": 85, "header_file": "include/bcm/l2.h"},
      {"name": "L3", "api_count": 120, "header_file": "include/bcm/l3.h"},
      {"name": "VLAN", "api_count": 45, "header_file": "include/bcm/vlan.h"}
    ]
  },
  "meta": {
    "elapsed_ms": 5,
    "source": "sqlite"
  }
}
```

## Реализация

```python
async def run_get_sdk_info(sdk_path: Path, indexer: SdkIndexer, include_modules: bool = False) -> dict
```

- Получает статистику из `SdkIndexer.get_stats()`
- При `include_modules=True` запрашивает список модулей из SQLite
- Возвращает версию SDK (захардкожена как `"6.5.27"`)