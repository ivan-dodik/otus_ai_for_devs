"""Обёртка над ripgrep (rg) для быстрого текстового поиска.

Использует subprocess для вызова rg с JSON-выходом.
Whitelist: только команда rg.
"""

from __future__ import annotations

import contextlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


class RgSearchError(Exception):
    """Ошибка при выполнении ripgrep."""

    pass


@dataclass
class RgMatch:
    """Результат одного совпадения ripgrep."""

    file: str = ""
    """Путь к файлу."""

    line: int = 0
    """Номер строки."""

    column: int = 0
    """Номер колонки."""

    text: str = ""
    """Текст строки с совпадением."""

    context_before: list[str] = field(default_factory=list)
    """Строки контекста до совпадения."""

    context_after: list[str] = field(default_factory=list)
    """Строки контекста после совпадения."""


def _parse_rg_json_output(output: str, context_lines: int = 0) -> list[RgMatch]:
    """Парсинг JSON-вывода ripgrep.

    Args:
        output: stdout от rg --json.
        context_lines: количество строк контекста.

    Returns:
        Список RgMatch.
    """
    matches: list[RgMatch] = []
    current_before: list[str] = []
    current_after: list[str] = []
    collecting_after = False
    after_count = 0

    for line in output.strip().split("\n"):
        if not line.strip():
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        obj_type = obj.get("type")

        if obj_type == "match":
            data = obj.get("data", {})
            path = data.get("path", {}).get("text", "")
            line_number = data.get("line_number", 0)
            lines_map = data.get("lines", {})
            text = lines_map.get("text", "")

            match = RgMatch(
                file=path,
                line=line_number,
                text=text.rstrip("\n"),
                context_before=list(current_before),
                context_after=list(current_after),
            )
            matches.append(match)
            current_before = []
            current_after = []
            collecting_after = False
            after_count = 0

        elif obj_type == "context":
            data = obj.get("data", {})
            lines_map = data.get("lines", {})
            text = lines_map.get("text", "").rstrip("\n")

            if collecting_after and after_count < context_lines:
                current_after.append(text)
                after_count += 1
            else:
                current_before.append(text)
                # keep only last context_lines before
                if len(current_before) > context_lines:
                    current_before = current_before[-context_lines:]

        elif obj_type == "begin":
            # Начало нового файла — сброс контекста
            current_before = []
            current_after = []
            collecting_after = False
            after_count = 0

    return matches


def rg_search(
    pattern: str,
    path: Path,
    file_pattern: str | None = None,
    context_lines: int = 0,
    max_results: int = 50,
) -> list[RgMatch]:
    """Поиск по паттерну в файлах через ripgrep.

    Args:
        pattern: Регулярное выражение для поиска.
        path: Директория для поиска.
        file_pattern: Глоб-паттерн для фильтрации файлов (например, "*.h").
        context_lines: Количество строк контекста вокруг совпадения.
        max_results: Максимальное количество результатов.

    Returns:
        Список найденных совпадений.

    Raises:
        RgSearchError: Если rg не найден или вернул ошибку.
    """
    cmd = ["rg", "--json", "--no-heading"]

    if context_lines > 0:
        cmd.extend(["-C", str(context_lines)])

    if file_pattern:
        cmd.extend(["-g", file_pattern])

    cmd.extend([pattern, str(path)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError as err:
        raise RgSearchError(
            "ripgrep (rg) not found. Install it first: apt install ripgrep"
        ) from err
    except subprocess.TimeoutExpired as err:
        raise RgSearchError("ripgrep search timed out after 30 seconds") from err

    if result.returncode not in (0, 1):  # 1 = no matches
        raise RgSearchError(f"ripgrep error (code {result.returncode}): {result.stderr[:200]}")

    matches = _parse_rg_json_output(result.stdout, context_lines)

    return matches[:max_results]


def rg_count(
    pattern: str,
    path: Path,
    file_pattern: str | None = None,
) -> int:
    """Подсчёт количества совпадений.

    Args:
        pattern: Регулярное выражение.
        path: Директория для поиска.
        file_pattern: Глоб-паттерн для фильтрации файлов.

    Returns:
        Количество совпадений.
    """
    cmd = ["rg", "--count-matches", "--no-heading"]

    if file_pattern:
        cmd.extend(["-g", file_pattern])

    cmd.extend([pattern, str(path)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 0

    if result.returncode not in (0, 1):
        return 0

    # Парсим вывод --count-matches
    total = 0
    for line in result.stdout.strip().split("\n"):
        if ":" in line:
            with contextlib.suppress(ValueError, IndexError):
                total += int(line.split(":")[-1])

    return total


def rg_files(
    pattern: str,
    path: Path,
    file_pattern: str | None = None,
) -> list[Path]:
    """Поиск файлов, содержащих совпадение.

    Args:
        pattern: Регулярное выражение.
        path: Директория для поиска.
        file_pattern: Глоб-паттерн для фильтрации файлов.

    Returns:
        Список путей к файлам.
    """
    cmd = ["rg", "--files-with-matches", "--no-heading"]

    if file_pattern:
        cmd.extend(["-g", file_pattern])

    cmd.extend([pattern, str(path)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    if result.returncode not in (0, 1):
        return []

    return [Path(p) for p in result.stdout.strip().split("\n") if p.strip()]
