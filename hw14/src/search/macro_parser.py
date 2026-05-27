"""Парсинг C-макросов (#define, #ifdef, #if defined)."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class MacroDef:
    """Декларация макроса."""

    name: str = ""
    """Имя макроса."""
    value: str = ""
    """Значение макроса."""
    file: str = ""
    """Файл."""
    line: int = 0
    """Номер строки."""


# Паттерн для #define
DEFINE_PATTERN = re.compile(r"#define\s+(\w+)(?:\s+(.+))?")

# Паттерн для #if defined(BCM_...) или #ifdef BCM_...
CHIP_GUARD_PATTERN = re.compile(r"#\s*if\s+(?:defined\s*\(\s*)?(BCM_\w+_SUPPORT)\s*(?:\s*\))?")

# Паттерн для SOC_IS_* условий
SOC_IS_PATTERN = re.compile(r"SOC_IS_(\w+)\s*\(")

# Паттерн для #elif defined(BCM_...)
ELIF_GUARD_PATTERN = re.compile(r"#\s*elif\s+(?:defined\s*\(\s*)?(BCM_\w+_SUPPORT)\s*(?:\s*\))?")


def extract_macros(lines: list[str]) -> list[MacroDef]:
    """Извлечение #define макросов из строк.

    Args:
        lines: Строки файла.

    Returns:
        Список MacroDef.
    """
    macros = []
    for i, line in enumerate(lines):
        m = DEFINE_PATTERN.match(line.strip())
        if m:
            macros.append(
                MacroDef(
                    name=m.group(1),
                    value=(m.group(2) or "").strip(),
                    line=i + 1,
                )
            )
    return macros


def extract_chip_guards(lines: list[str], func_line: int) -> list[str]:
    """Извлечение chip guard условий (#if defined BCM_*_SUPPORT) вокруг функции.

    Args:
        lines: Строки файла.
        func_line: Номер строки функции (0-based).

    Returns:
        Список имён макросов (например, ["BCM_TOMAHAWK4_SUPPORT"]).
    """
    guards = set()

    # Ищем #if defined(BCM_*) перед функцией
    for i in range(max(0, func_line - 20), func_line):
        line = lines[i].strip()
        m = CHIP_GUARD_PATTERN.match(line)
        if m:
            guards.add(m.group(1))

    # Ищем #elif defined(BCM_*) после функции
    for i in range(func_line, min(len(lines), func_line + 20)):
        line = lines[i].strip()
        m = ELIF_GUARD_PATTERN.match(line)
        if m:
            guards.add(m.group(1))

    return list(guards)


def extract_chip_conditions(lines: list[str], func_line: int) -> list[str]:
    """Извлечение SOC_IS_* условий в окрестности функции.

    Args:
        lines: Строки файла.
        func_line: Номер строки функции (0-based).

    Returns:
        Список условий (например, ["SOC_IS_TOMAHAWK4(unit)"]).
    """
    conditions = set()
    start = max(0, func_line - 5)
    end = min(len(lines), func_line + 30)

    for i in range(start, end):
        line = lines[i]
        for m in SOC_IS_PATTERN.finditer(line):
            # Ищем полное выражение SOC_IS_*(...)
            rest = line[m.start() :]
            paren_match = re.match(r"SOC_IS_\w+\s*\([^)]*\)", rest)
            if paren_match:
                conditions.add(paren_match.group(0))

    return list(conditions)
