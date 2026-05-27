"""TOOL 7: find_cint_scripts — поиск CINT скриптов."""

import time
from pathlib import Path

from src.models.schemas import (
    CintScriptListResult,
    CintScriptResult,
    RelatedFile,
    ToolMeta,
    ToolResult,
)
from src.search.cint_parser import extract_script_header, extract_used_apis, is_cint_script
from src.search.rg_search import rg_search


async def run_find_cint_scripts(
    query: str,
    sdk_path: Path,
    chip: str | None = None,
    include_logs: bool = False,
    include_configs: bool = False,
    include_full_source: bool = False,  # noqa: ARG001
) -> dict[str, object]:
    """Поиск CINT скриптов по функционалу, чипу или параметрам.

    Args:
        query: Поисковый запрос (функционал, чип, имя файла).
        sdk_path: Путь к SDK.
        chip: Фильтр по чипу.
        include_logs: Включить логи вывода.
        include_configs: Включить .bcm конфиги.
        include_full_source: Показать полный исходник.

    Returns:
        CintScriptListResult в формате ToolResult.
    """
    start = time.time()

    # Директории с CINT скриптами
    search_dirs = [
        sdk_path / "src" / "examples",
        sdk_path / "cint",
        sdk_path / "diag",
    ]

    all_matches = []
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        # Поиск по содержимому
        matches = rg_search(
            pattern=query,
            path=search_dir,
            file_pattern="*.c",
            context_lines=0,
            max_results=30,
        )
        all_matches.extend(matches)

        # Поиск по имени файла
        file_matches = rg_search(
            pattern=query,
            path=search_dir,
            file_pattern="*.c",
            max_results=10,
        )
        all_matches.extend(file_matches)

    # Дедупликация по файлу
    seen_files = set()
    scripts = []

    for match in all_matches:
        file_path = Path(match.file)
        file_key = str(file_path.resolve())

        if file_key in seen_files:
            continue
        seen_files.add(file_key)

        # Проверка, что это CINT скрипт
        if not is_cint_script(file_path, sdk_path):
            continue

        # Фильтр по чипу
        if chip:
            header = extract_script_header(file_path)
            if header and chip.lower() not in header.lower():
                continue

        # Заголовок
        header_comment = extract_script_header(file_path)

        # API used
        apis = extract_used_apis(file_path)

        # Связанные файлы
        related = []
        base = file_path.with_suffix("")

        if include_logs:
            log_path = base.with_suffix(".log")
            if log_path.exists():
                related.append(
                    RelatedFile(
                        path=str(log_path),
                        type="log",
                        size_bytes=log_path.stat().st_size,
                    )
                )

        if include_configs:
            config_path = base.with_suffix(".bcm")
            if config_path.exists():
                related.append(
                    RelatedFile(
                        path=str(config_path),
                        type="config",
                        size_bytes=config_path.stat().st_size,
                    )
                )

        script = CintScriptResult(
            file=str(file_path),
            header_comment=header_comment,
            apis_used=apis,
            related_files=related,
        )
        scripts.append(script)

        if len(scripts) >= 20:
            break

    result = CintScriptListResult(
        query=query,
        total_found=len(scripts),
        scripts=scripts,
    )

    return ToolResult(
        ok=True,
        result=result.model_dump(),
        meta=ToolMeta(
            elapsed_ms=int((time.time() - start) * 1000),
            source="ripgrep",
        ),
    ).model_dump()
