"""TOOL 2: get_sdk_info — информация о SDK."""

from pathlib import Path

from src.indexer.sdk_indexer import SdkIndexer
from src.models.schemas import ModuleInfo, SdkInfoResult, ToolMeta, ToolResult


async def run_get_sdk_info(
    sdk_path: Path,
    indexer: SdkIndexer,
    include_modules: bool = False,
) -> dict[str, object]:
    """Информация о SDK: версия, путь, статус индексации, количество API.

    Args:
        sdk_path: Путь к SDK.
        indexer: Индексатор SDK.
        include_modules: Показать список модулей.

    Returns:
        SdkInfoResult в формате ToolResult.
    """
    stats = indexer.get_stats()
    modules = []

    if include_modules and stats.modules_count > 0:
        conn = indexer._get_connection()
        cur = conn.execute(
            """SELECT module, COUNT(*) as api_count,
                      MIN(file_path) as header_file
               FROM functions
               WHERE module != ''
               GROUP BY module
               ORDER BY module"""
        )
        for row in cur.fetchall():
            modules.append(
                ModuleInfo(
                    name=row[0],
                    api_count=row[1],
                    header_file=row[2],
                )
            )

    result = SdkInfoResult(
        sdk_path=str(sdk_path),
        version="6.5.27",
        indexed=stats.functions_count > 0,
        modules_count=stats.modules_count,
        apis_count=stats.functions_count,
        cache_dir=str(indexer.cache_dir),
        modules=modules,
    )

    return ToolResult(
        ok=True,
        result=result.model_dump(),
        meta=ToolMeta(elapsed_ms=0, source="sqlite"),
    ).model_dump()
