"""TOOL 6: get_chip_info — информация о ASIC."""

import time
from pathlib import Path

from src.indexer.chip_map import ChipMap
from src.models.schemas import (
    ChipCintScript,
    ChipInfoResult,
    ToolMeta,
    ToolResult,
)
from src.search.cint_parser import extract_script_header, extract_used_apis
from src.search.rg_search import rg_search


async def run_get_chip_info(
    chip: str,
    chip_map: ChipMap,
    sdk_path: Path,
    include_apis: bool = False,
    include_cint_scripts: bool = False,
) -> dict[str, object]:
    """Получить сводку по ASIC.

    Args:
        chip: Имя чипа.
        chip_map: Маппинг чипов.
        sdk_path: Путь к SDK.
        include_apis: Показать примеры API.
        include_cint_scripts: Показать CINT скрипты для этого чипа.

    Returns:
        ChipInfoResult в формате ToolResult.
    """
    start = time.time()
    chip_data = chip_map.get_chip(chip)

    if not chip_data:
        available = chip_map.list_chips()
        return ToolResult(
            ok=False,
            error=f"Chip '{chip}' not found. Available: {', '.join(available)}",
            meta=ToolMeta(elapsed_ms=int((time.time() - start) * 1000), source="config"),
        ).model_dump()

    # Примеры API
    example_apis = chip_data.get("example_apis", [])
    if include_apis:
        # Ищем больше API через rg
        for macro in chip_data.get("feature_macros", []):
            results = rg_search(
                pattern=macro,
                path=sdk_path / "include" / "bcm",
                file_pattern="*.h",
                max_results=20,
            )
            for r in results[:10]:
                api_name = _extract_api_name(r.text)
                if api_name and api_name not in example_apis:
                    example_apis.append(api_name)

    # CINT скрипты
    cint_scripts = []
    if include_cint_scripts:
        chip_name_lower = chip.lower()
        cint_results = rg_search(
            pattern=chip_name_lower,
            path=sdk_path / "src" / "examples",
            file_pattern="*.c",
            max_results=20,
        )
        for r in cint_results[:10]:
            file_path = Path(r.file)
            header = extract_script_header(file_path)
            apis = extract_used_apis(file_path)
            cint_scripts.append(
                ChipCintScript(
                    file=str(file_path),
                    header=header or "",
                    apis_used=apis,
                )
            )

    result = ChipInfoResult(
        chip=chip,
        dev_ids=chip_data.get("dev_ids", []),
        feature_macros=chip_data.get("feature_macros", []),
        modules=chip_data.get("modules", []),
        soc_directories=chip_data.get("soc_dirs", []),
        api_count_estimate=len(example_apis),
        example_apis=example_apis[:10],
        cint_scripts=cint_scripts,
    )

    return ToolResult(
        ok=True,
        result=result.model_dump(),
        meta=ToolMeta(
            elapsed_ms=int((time.time() - start) * 1000),
            source="config",
        ),
    ).model_dump()


def _extract_api_name(text: str) -> str | None:
    """Извлечь имя API из строки."""
    import re

    m = re.search(r"(bcm_\w+)\s*\(", text)
    return m.group(1) if m else None
