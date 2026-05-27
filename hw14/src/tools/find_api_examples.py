"""TOOL 4: find_api_examples — поиск примеров использования API."""

import time
from pathlib import Path

from src.models.schemas import (
    ExampleListResult,
    ExampleResult,
    RelatedFile,
    ToolMeta,
    ToolResult,
)
from src.search.cint_parser import extract_script_header, is_cint_script
from src.search.rg_search import rg_search


async def run_find_api_examples(
    api: str,
    sdk_path: Path,
    source_type: str = "all",
    max_results: int = 10,
    context_lines: int = 3,
    include_full_source: bool = False,
) -> dict[str, object]:
    """Поиск примеров использования API в C-коде и CINT скриптах.

    Args:
        api: Имя API (например, bcm_l3_route_add).
        sdk_path: Путь к SDK.
        source_type: all, c, cint, bcm_config.
        max_results: Максимум результатов (max 50).
        context_lines: Строк контекста (max 10).
        include_full_source: Показать полный исходник CINT скрипта.

    Returns:
        ExampleListResult в формате ToolResult.
    """
    start = time.time()

    # Ограничения
    max_results = min(max_results, 50)
    context_lines = min(context_lines, 10)

    # Поиск через rg
    pattern = f"{api}\\("
    matches = rg_search(
        pattern=pattern,
        path=sdk_path,
        file_pattern="*.c",
        context_lines=context_lines,
        max_results=max_results * 3,  # больше для фильтрации
    )

    # Дополнительно ищем в .h файлах
    h_matches = rg_search(
        pattern=pattern,
        path=sdk_path,
        file_pattern="*.h",
        context_lines=context_lines,
        max_results=max_results,
    )
    matches.extend(h_matches)

    examples: list[ExampleResult] = []
    seen_files = set()

    for match in matches:
        if len(examples) >= max_results:
            break

        file_path = Path(match.file)

        # Фильтр по source_type
        is_cint = is_cint_script(file_path, sdk_path)
        if source_type == "cint" and not is_cint:
            continue
        if source_type == "c" and is_cint:
            continue
        if source_type == "bcm_config":
            continue

        # Dedup по файлу
        file_key = str(file_path)
        if file_key in seen_files:
            continue
        seen_files.add(file_key)

        # Контекст
        snippet = match.text
        if match.context_before:
            snippet = "\n".join(match.context_before) + "\n" + snippet
        if match.context_after:
            snippet += "\n" + "\n".join(match.context_after)

        # Заголовок CINT скрипта
        script_header = None
        if is_cint:
            script_header = extract_script_header(file_path)

        # Полный исходник CINT
        full_source = None
        if include_full_source and is_cint:
            try:
                with open(file_path, errors="replace") as f:
                    full_source = f.read()
            except (FileNotFoundError, PermissionError):
                pass

        # Связанные файлы (.bcm, .log)
        related = []
        if is_cint:
            base = file_path.with_suffix("")
            for ext in [".bcm", ".log"]:
                related_path = base.with_suffix(ext)
                if related_path.exists():
                    related.append(
                        RelatedFile(
                            path=str(related_path),
                            type=ext.lstrip("."),
                            size_bytes=related_path.stat().st_size,
                        )
                    )

        example = ExampleResult(
            file=str(file_path),
            line=match.line,
            snippet=snippet,
            source_type="cint" if is_cint else "c",
            script_header=script_header,
            related_files=related,
        )
        examples.append(example)

    if full_source:
        # Добавляем полный исходник как отдельное поле
        pass

    result = ExampleListResult(
        api=api,
        total_found=len(examples),
        examples=examples,
    )

    return ToolResult(
        ok=True,
        result=result.model_dump(),
        meta=ToolMeta(
            elapsed_ms=int((time.time() - start) * 1000),
            source="ripgrep",
        ),
    ).model_dump()
