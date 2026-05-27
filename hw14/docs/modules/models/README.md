# Модуль моделей данных (`src/models/`)

## Назначение

Модуль содержит Pydantic модели для всех I/O контрактов инструментов. Обеспечивает единообразный формат ответа и валидацию данных.

## Файлы модуля

| Файл | Назначение |
|------|-----------|
| `__init__.py` | Пакетный инициализатор |
| `schemas.py` | Pydantic модели: ToolResult, PingResult, SdkInfoResult, ApiResult, ExampleListResult, TraceResult, ChipInfoResult, CintScriptListResult |

## Диаграмма иерархии моделей

```mermaid
classDiagram
    class ToolResult~T~ {
        +bool ok
        +T result
        +str error
        +ToolMeta meta
    }

    class ToolMeta {
        +int elapsed_ms
        +str source
    }

    class PingResult {
        +str status
        +bool sdk_configured
        +bool indexed
        +str version
    }

    class SdkInfoResult {
        +str sdk_path
        +str version
        +bool indexed
        +int modules_count
        +int apis_count
        +str cache_dir
        +list~ModuleInfo~ modules
    }

    class ApiResult {
        +str name
        +str signature
        +str module
        +str header
        +int line
        +str description
        +list~ParameterInfo~ parameters
        +ReturnInfo returns
        +list~str~ chip_availability
        +list~str~ related_apis
    }

    class ExampleListResult {
        +str api
        +int total_found
        +list~ExampleResult~ examples
    }

    class TraceResult {
        +str api
        +TraceEntry entry_point
        +list~TraceEntry~ implementation_chain
        +list~ChipBranch~ chip_specific_branches
    }

    class ChipInfoResult {
        +str chip
        +list~str~ dev_ids
        +list~str~ feature_macros
        +list~str~ modules
        +list~str~ soc_directories
        +int api_count_estimate
        +list~str~ example_apis
        +list~ChipCintScript~ cint_scripts
    }

    class CintScriptListResult {
        +str query
        +int total_found
        +list~CintScriptResult~ scripts
    }

    ToolResult --> ToolMeta
    ToolResult --> PingResult
    ToolResult --> SdkInfoResult
    ToolResult --> ApiResult
    ToolResult --> ExampleListResult
    ToolResult --> TraceResult
    ToolResult --> ChipInfoResult
    ToolResult --> CintScriptListResult
```

## Универсальная обёртка `ToolResult[T]`

Все инструменты возвращают результат в едином формате:

```python
class ToolResult(BaseModel, Generic[T]):
    ok: bool                    # Флаг успешности
    result: T | None            # Данные (зависит от инструмента)
    error: str | None           # Сообщение об ошибке
    meta: ToolMeta              # Мета-информация
```

### `ToolMeta`

```python
class ToolMeta(BaseModel):
    elapsed_ms: int = 0         # Время выполнения в мс
    source: str = ""            # Источник данных (sqlite, ripgrep, config, internal)