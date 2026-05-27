"""Парсинг заголовков CINT скриптов.

CINT скрипты — это C-подобные скрипты для тестирования Broadcom ASIC.
Они содержат многострочные комментарии в начале файла с описанием,
чипом, портами и тестами.
"""

from __future__ import annotations

import re
from pathlib import Path

# Директории, в которых обычно находятся CINT скрипты
CINT_DIRECTORIES = {"src/examples", "cint", "diag"}

# Паттерн для поиска упоминания чипа в заголовке
CHIP_PATTERN = re.compile(r"(Tomahawk[0-9]|Trident[0-9]|Jericho[0-9]|BCM[0-9]{5})")

# Паттерн для извлечения имен API из CINT скрипта
API_CALL_PATTERN = re.compile(r"bcm_\w+\s*\(")


def is_cint_script(file_path: Path, sdk_root: Path | None = None) -> bool:
    """Проверить, является ли файл CINT скриптом.

    Критерии:
    1. Файл находится в директориях src/examples/, cint/, diag/
    2. ИЛИ файл имеет характерный заголовочный комментарий CINT

    Args:
        file_path: Путь к файлу.
        sdk_root: Корень SDK (для проверки относительного пути).

    Returns:
        True если файл считается CINT скриптом.
    """
    # Проверка по расположению
    if sdk_root:
        try:
            rel = file_path.relative_to(sdk_root)
            for cint_dir in CINT_DIRECTORIES:
                if str(rel).startswith(cint_dir):
                    return True
        except ValueError:
            pass

    # Проверка по расширению .c (CINT скрипты обычно .c)
    if file_path.suffix != ".c":
        return False

    # Fallback: проверка заголовочного комментария
    header = extract_script_header(file_path)
    return bool(header and ("Tested on" in header or "Tests:" in header))


def extract_script_header(file_path: Path) -> str | None:
    """Извлечение многострочного комментария из начала файла (первые 5-20 строк).

    Args:
        file_path: Путь к файлу.

    Returns:
        Текст заголовочного комментария или None.
    """
    try:
        with open(file_path, errors="replace") as f:
            lines = f.readlines()
    except (FileNotFoundError, PermissionError):
        return None

    if not lines:
        return None

    # Ищем начало многострочного комментария
    comment_start = -1
    for i, line in enumerate(lines[:30]):
        stripped = line.strip()
        if stripped.startswith("/*"):
            comment_start = i
            break

    if comment_start == -1:
        return None

    # Ищем конец комментария
    comment_lines = []
    for i in range(comment_start, min(len(lines), comment_start + 30)):
        comment_lines.append(lines[i].rstrip("\n"))
        if "*/" in lines[i]:
            break

    if not comment_lines:
        return None

    return "\n".join(comment_lines)


def parse_header_comment(comment: str) -> dict[str, str | list[str]]:
    """Парсинг заголовочного комментария CINT скрипта.

    Args:
        comment: Текст заголовочного комментария.

    Returns:
        Словарь с полями: chip, ports, description, tests.
    """
    result: dict[str, str | list[str]] = {
        "chip": "",
        "ports": "",
        "description": "",
        "tests": [],
    }

    # Удаляем /* и */, разбиваем на строки
    text = comment.replace("/*", "").replace("*/", "").strip()
    lines = [line.strip().lstrip("*").strip() for line in text.split("\n")]

    for line in lines:
        if "Tested on:" in line:
            # Извлекаем имя чипа
            chip_match = CHIP_PATTERN.search(line)
            if chip_match:
                result["chip"] = chip_match.group(1)

        elif line.startswith("Ports:"):
            result["ports"] = line.replace("Ports:", "").strip()

        elif line.startswith("Tests:"):
            tests_str = line.replace("Tests:", "").strip()
            result["tests"] = [t.strip() for t in tests_str.split("/")]

        elif line and not result["description"]:
            # Первая непустая строка — описание
            if not any(skip in line for skip in ["Tested on", "Ports:", "Tests:", "/*", "*/", "*"]):
                result["description"] = line

    return result


def extract_used_apis(file_path: Path, max_lines: int = 200) -> list[str]:
    """Извлечение имён BCM API, используемых в скрипте.

    Args:
        file_path: Путь к файлу.
        max_lines: Максимальное количество строк для поиска.

    Returns:
        Список имён API.
    """
    try:
        with open(file_path, errors="replace") as f:
            content = "".join(f.readlines()[:max_lines])
    except (FileNotFoundError, PermissionError):
        return []

    apis = set()
    for m in API_CALL_PATTERN.finditer(content):
        # Убираем открывающую скобку
        api_name = m.group(0).rstrip("(").strip()
        apis.add(api_name)

    return sorted(apis)
