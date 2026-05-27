# `ping.py` — Health-check сервера

## Назначение

Инструмент `ping` — проверка, что сервер работает и SDK сконфигурирован. Самый простой инструмент, не требующий параметров.

## Параметры

Нет.

## Формат результата

```python
class PingResult(BaseModel):
    status: str          # "ok"
    sdk_configured: bool # SDK path сконфигурирован и доступен
    indexed: bool        # Индекс SDK построен
    version: str         # Версия сервера ("0.1.0")
```

## Пример ответа

```json
{
  "ok": true,
  "result": {
    "status": "ok",
    "sdk_configured": true,
    "indexed": true,
    "version": "0.1.0"
  },
  "meta": {
    "elapsed_ms": 0,
    "source": "internal"
  }
}
```

## Реализация

```python
async def run_ping(sdk_path: Path | None, index_ready: bool) -> dict:
    sdk_configured = sdk_path is not None and sdk_path.exists()
    result = PingResult(status="ok", sdk_configured=sdk_configured, indexed=index_ready, version="0.1.0")
    return ToolResult(ok=True, result=result.model_dump(), meta=ToolMeta(elapsed_ms=0, source="internal")).model_dump()
```

- Проверяет существование `sdk_path`
- Проверяет флаг `index_ready` (ленивая индексация)
- Возвращает версию сервера