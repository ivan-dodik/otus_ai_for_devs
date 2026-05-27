"""TOOL 1: ping — health-check сервера."""

from pathlib import Path

from src.models.schemas import PingResult, ToolMeta, ToolResult


async def run_ping(
    sdk_path: Path | None,
    index_ready: bool,
) -> dict[str, object]:
    """Health-check: проверка, что сервер работает и SDK сконфигурирован.

    Returns:
        PingResult в формате ToolResult.
    """
    sdk_configured = sdk_path is not None and sdk_path.exists()

    result = PingResult(
        status="ok",
        sdk_configured=sdk_configured,
        indexed=index_ready,
        version="0.1.0",
    )

    return ToolResult(
        ok=True,
        result=result.model_dump(),
        meta=ToolMeta(elapsed_ms=0, source="internal"),
    ).model_dump()
