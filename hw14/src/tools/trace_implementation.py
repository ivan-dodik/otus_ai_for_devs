"""TOOL 5: trace_api_implementation — трассировка цепочки реализации API."""

import time
from pathlib import Path

from src.models.schemas import (
    ChipBranch,
    ToolMeta,
    ToolResult,
    TraceEntry,
    TraceResult,
)
from src.search.macro_parser import extract_chip_conditions
from src.search.rg_search import rg_search


async def run_trace_implementation(
    api: str,
    sdk_path: Path,
    chip: str | None = None,  # noqa: ARG001
    max_depth: int = 3,
) -> dict[str, object]:
    """Показать цепочку реализации от public API до chip-specific кода.

    Args:
        api: Имя API.
        sdk_path: Путь к SDK.
        chip: Фильтр по чипу.
        max_depth: Глубина трассировки (max 7).

    Returns:
        TraceResult в формате ToolResult.
    """
    start = time.time()
    max_depth = min(max_depth, 7)

    # Эвристика: ищем реализацию bcm_esw_<api>
    esw_name = f"bcm_esw_{api[len('bcm_') :]}" if api.startswith("bcm_") else api

    # Поиск entry point
    entry_matches = rg_search(
        pattern=f"^{esw_name}\\(",
        path=sdk_path / "src",
        file_pattern="*.c",
        context_lines=2,
        max_results=5,
    )

    if not entry_matches:
        # Fallback: ищем любую реализацию
        entry_matches = rg_search(
            pattern=f"{api}\\(",
            path=sdk_path / "src",
            file_pattern="*.c",
            context_lines=2,
            max_results=10,
        )

    if not entry_matches:
        return ToolResult(
            ok=False,
            error=f"Implementation for '{api}' not found in src/",
            meta=ToolMeta(elapsed_ms=int((time.time() - start) * 1000), source="ripgrep"),
        ).model_dump()

    # Строим цепочку
    chain: list[TraceEntry] = []
    branches: list[ChipBranch] = []
    visited_functions: set[str] = set()

    for depth in range(max_depth):
        current_matches = entry_matches if depth == 0 else []
        if not current_matches and depth > 0 and chain:
            # Ищем следующий уровень по вызовам функций
            last_func = chain[-1].function
            next_matches = rg_search(
                pattern=f"(?:\b{last_func[:-1]}_internal|{last_func[:-1]}_\\w+)\\(",
                path=sdk_path / "src",
                file_pattern="*.c",
                context_lines=2,
                max_results=10,
            )
            current_matches = next_matches

        for match in current_matches[:3]:  # макс 3 на уровень
            func_name = _extract_function_name(match.text)
            if not func_name or func_name in visited_functions:
                continue
            visited_functions.add(func_name)

            # Читаем chip conditions
            conditions = []
            try:
                with open(match.file, errors="replace") as f:
                    lines = f.readlines()
                conditions = extract_chip_conditions(lines, match.line - 1)
            except (FileNotFoundError, PermissionError):
                pass

            entry = TraceEntry(
                level=depth + 1,
                function=func_name,
                file=match.file,
                line=match.line,
                chip_conditions=conditions,
                guard_pattern="",
            )
            chain.append(entry)

            # Определяем chip-specific branches
            if conditions:
                branch_name = conditions[0]
                if not any(b.condition == branch_name for b in branches):
                    soc_match = rg_search(
                        pattern=func_name,
                        path=sdk_path / "src",
                        file_pattern="*.c",
                        max_results=5,
                    )
                    soc_files = list(set(m.file for m in soc_match[:3]))
                    branches.append(
                        ChipBranch(
                            condition=branch_name,
                            functions=[func_name],
                            soc_file=soc_files[0] if soc_files else "",
                        )
                    )

    # Entry point
    entry_point = chain[0] if chain else TraceEntry()

    result = TraceResult(
        api=api,
        entry_point=entry_point,
        implementation_chain=chain,
        chip_specific_branches=branches,
    )

    return ToolResult(
        ok=True,
        result=result.model_dump(),
        meta=ToolMeta(
            elapsed_ms=int((time.time() - start) * 1000),
            source="ripgrep",
            max_depth_reached=min(len(chain), max_depth),
        ),
    ).model_dump()


def _extract_function_name(text: str) -> str | None:
    """Извлечь имя функции из строки."""
    import re

    m = re.match(r"^\s*(?:\w+\s+\*?)?(\w+)\s*\(", text)
    return m.group(1) if m else None
