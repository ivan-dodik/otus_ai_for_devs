# `config.py` — Настройки приложения

## Назначение

Конфигурация приложения из переменных окружения и `.env` файла. Использует `pydantic-settings` для автоматической загрузки и валидации.

## Класс `Settings`

```python
class Settings(BaseSettings):
    openbcm_sdk_path: Path | None = None
    openbcm_mcp_log_level: str = "INFO"
    openbcm_mcp_cache_dir: Path = Path("./cache")
```

### Поля

| Поле | Тип | Дефолт | Переменная окружения | Описание |
|------|-----|--------|---------------------|----------|
| `openbcm_sdk_path` | `Path \| None` | `None` | `OPENBCM_SDK_PATH` | Путь к корню SDK |
| `openbcm_mcp_log_level` | `str` | `"INFO"` | `OPENBCM_MCP_LOG_LEVEL` | Уровень логирования |
| `openbcm_mcp_cache_dir` | `Path` | `"./cache"` | `OPENBCM_MCP_CACHE_DIR` | Директория кэша |

### Свойства

#### `resolved_cache_dir`

```python
@property
def resolved_cache_dir(self) -> Path
```

Возвращает абсолютный путь к кэшу. Если путь относительный — резолвит относительно `PROJECT_ROOT`.

#### `resolved_config_dir`

```python
@property
def resolved_config_dir(self) -> Path
```

Возвращает абсолютный путь к `config/` директории проекта.

### Конфигурация

```python
model_config = {
    "env_file": ".env",
    "env_file_encoding": "utf-8",
    "extra": "ignore",
}
```

- Загружает значения из `.env` файла
- Приоритет: переменные окружения > `.env` файл > дефолтные значения
- `extra="ignore"` — игнорирует неизвестные переменные

## Константа `PROJECT_ROOT`

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
```

Корень проекта — директория, где находится `src/`.

## Функция `get_settings()`

```python
def get_settings() -> Settings
```

Создаёт и возвращает настройки. Используется вместо синглтона для поддержки тестов.