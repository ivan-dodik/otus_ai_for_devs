"""TOOL 3: find_bcm_api — поиск декларации BCM API."""

import time

from src.indexer.sdk_indexer import SdkIndexer
from src.models.schemas import (
    ApiResult,
    ParameterInfo,
    ReturnInfo,
    ToolMeta,
    ToolResult,
)


async def run_find_bcm_api(
    api: str,
    indexer: SdkIndexer,
    chip: str = "all",
    fuzzy: bool = False,
) -> dict[str, object]:
    """Поиск декларации BCM API в заголовочных файлах SDK.

    Args:
        api: Имя API (например, bcm_vlan_create).
        indexer: Индексатор SDK.
        chip: Фильтр по чипу (Tomahawk4, Trident3, all).
        fuzzy: Включить нечёткий поиск при отсутствии точного совпадения.

    Returns:
        ApiResult в формате ToolResult.
    """
    start = time.time()

    # Поиск в индексе
    results = indexer.search_api(name=api, chip=chip if chip != "all" else None, fuzzy=fuzzy)

    if not results and not fuzzy:
        # Пробуем fuzzy если точный поиск не дал результатов
        results = indexer.search_api(name=api, fuzzy=True)

    if not results:
        return ToolResult(
            ok=False,
            error=f"API '{api}' not found",
            meta=ToolMeta(elapsed_ms=int((time.time() - start) * 1000), source="sqlite"),
        ).model_dump()

    # Берём первый результат
    r = results[0]

    # Парсим параметры
    params = r.get("params_str", "")
    parameters = []
    if params:
        for p_str in params.split("|"):
            if ":" in p_str:
                parts = p_str.split(":")
                parameters.append(
                    ParameterInfo(
                        name=parts[0] if len(parts) > 0 else "",
                        type=parts[1] if len(parts) > 1 else "",
                        description=parts[2] if len(parts) > 2 else "",
                    )
                )

    # Определяем related_apis (похожие API из того же модуля)
    related = []
    if r.get("module"):
        module_results = indexer.search_api(api, chip=chip if chip != "all" else None)
        for mr in module_results[:5]:
            if mr.get("name") != api:
                related.append(mr.get("name", ""))

    result = ApiResult(
        name=r.get("name", api),
        signature=r.get("signature", ""),
        module=r.get("module", ""),
        header=r.get("file_path", ""),
        line=r.get("line", 0),
        description=r.get("description", ""),
        parameters=parameters,
        returns=ReturnInfo(type="int", description="BCM_E_NONE on success"),
        chip_availability=[],
        related_apis=related,
    )

    return ToolResult(
        ok=True,
        result=result.model_dump(),
        meta=ToolMeta(
            elapsed_ms=int((time.time() - start) * 1000),
            source="sqlite",
        ),
    ).model_dump()
