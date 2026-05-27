# `schemas.py` — Pydantic модели

## Назначение

Файл содержит все Pydantic модели, используемые для I/O контрактов инструментов. Модели обеспечивают валидацию данных и автогенерацию JSON Schema.

## Полный список моделей

### Универсальные

| Модель | Назначение |
|--------|-----------|
| `ToolMeta` | Мета-информация о выполнении (время, источник) |
| `ToolResult[T]` | Универсальная обёртка результата (ok/result/error/meta) |

### Tool 1: ping

| Модель | Поля |
|--------|------|
| `PingResult` | `status`, `sdk_configured`, `indexed`, `version` |

### Tool 2: get_sdk_info

| Модель | Поля |
|--------|------|
| `ModuleInfo` | `name`, `api_count`, `header_file` |
| `SdkInfoResult` | `sdk_path`, `version`, `indexed`, `modules_count`, `apis_count`, `cache_dir`, `modules` |

### Tool 3: find_bcm_api

| Модель | Поля |
|--------|------|
| `ParameterInfo` | `name`, `type`, `description` |
| `ReturnInfo` | `type`, `description` |
| `ApiResult` | `name`, `signature`, `module`, `header`, `line`, `description`, `parameters`, `returns`, `chip_availability`, `related_apis` |

### Tool 4: find_api_examples

| Модель | Поля |
|--------|------|
| `RelatedFile` | `path`, `type`, `size_bytes` |
| `ExampleResult` | `file`, `line`, `snippet`, `source_type`, `script_header`, `related_files` |
| `ExampleListResult` | `api`, `total_found`, `examples` |

### Tool 5: trace_api_implementation

| Модель | Поля |
|--------|------|
| `TraceEntry` | `level`, `function`, `file`, `line`, `chip_conditions`, `guard_pattern` |
| `ChipBranch` | `condition`, `functions`, `soc_file` |
| `TraceResult` | `api`, `entry_point`, `implementation_chain`, `chip_specific_branches` |

### Tool 6: get_chip_info

| Модель | Поля |
|--------|------|
| `ChipCintScript` | `file`, `header`, `apis_used` |
| `ChipInfoResult` | `chip`, `dev_ids`, `feature_macros`, `modules`, `soc_directories`, `api_count_estimate`, `example_apis`, `cint_scripts` |

### Tool 7: find_cint_scripts

| Модель | Поля |
|--------|------|
| `CintScriptResult` | `file`, `header_comment`, `apis_used`, `related_files` |
| `CintScriptListResult` | `query`, `total_found`, `scripts` |

## Пример использования

```python
from src.models.schemas import ToolResult, PingResult, ToolMeta

# Создание результата
result = PingResult(status="ok", sdk_configured=True, indexed=True, version="0.1.0")

# Упаковка в ToolResult
response = ToolResult(
    ok=True,
    result=result.model_dump(),
    meta=ToolMeta(elapsed_ms=0, source="internal"),
).model_dump()

# response готов к отправке через MCP