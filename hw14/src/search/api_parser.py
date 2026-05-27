"""Парсинг деклараций C-функций (BCM API) и Doxygen-комментариев."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FunctionDecl:
    """Декларация C-функции."""

    return_type: str = ""
    """Возвращаемый тип."""
    name: str = ""
    """Имя функции."""
    signature: str = ""
    """Полная сигнатура."""
    parameters: list[dict[str, Any]] = field(default_factory=list)
    """Список параметров [{name, type, description}]."""


@dataclass
class DocComment:
    """Doxygen-комментарий."""

    brief: str = ""
    """@brief описание."""
    params: dict[str, str] = field(default_factory=dict)
    """@param name -> description."""
    returns: str = ""
    """@return описание."""


# Паттерн для декларации BCM функции
# Пример: int bcm_vlan_create(int unit, bcm_vlan_t vlan);
FUNC_PATTERN = re.compile(
    r"^\s*"  # Начало строки
    r"(?P<return_type>\w+(?:\s*\*)?)\s+"  # Возвращаемый тип (int, uint32, void, ...)
    r"(?P<name>bcm_\w+)"  # Имя функции (начинается с bcm_)
    r"\s*\("  # Открывающая скобка
    r"(?P<params>[^)]*)"  # Параметры (всё до закрывающей скобки)
    r"\)\s*;"  # Закрывающая скобка и точка с запятой
)

# Паттерн для отдельного параметра: тип и имя
PARAM_PATTERN = re.compile(
    r"(?P<type>\w+(?:\s*\*)?)\s+(?P<name>\w+)\s*(?:/\*\*\s*<\s*(?P<desc>[^*]+)\s*\*/)?"
)

# Паттерн для Doxygen @brief
BRIEF_PATTERN = re.compile(r"@brief\s+(.+)")
# Паттерн для Doxygen @param
PARAM_DESC_PATTERN = re.compile(r"@param\s+(?:\[in\]|\[out\]|\[in,out\])?\s*(\w+)\s+(.+)")
# Паттерн для Doxygen @return
RETURN_PATTERN = re.compile(r"@return\s+(.+)")

# Паттерн для определения модуля по префиксу bcm_<module>_*
MODULE_PATTERN = re.compile(r"bcm_(\w+)_")


def extract_module(name: str) -> str:
    """Определить модуль по имени функции.

    Например: bcm_vlan_create -> VLAN, bcm_l2_addr_add -> L2.
    """
    m = MODULE_PATTERN.match(name)
    if m:
        module = m.group(1).upper()
        # Исключаем слишком короткие или общие префиксы
        if len(module) >= 2 and module not in ("BCM",):
            return module
    return ""


def parse_function_declaration(text: str) -> FunctionDecl | None:
    """Парсинг декларации C-функции.

    Args:
        text: Строка с декларацией (например, "int bcm_vlan_create(int unit, bcm_vlan_t vlan);").

    Returns:
        FunctionDecl или None, если не удалось распарсить.
    """
    m = FUNC_PATTERN.match(text.strip())
    if not m:
        return None

    return_type = m.group("return_type").strip()
    name = m.group("name").strip()
    params_str = m.group("params").strip()

    # Парсинг параметров
    params = []
    if params_str and params_str != "void":
        for p in PARAM_PATTERN.finditer(params_str):
            param_type = p.group("type").strip()
            param_name = p.group("name").strip()
            param_desc = p.group("desc")
            params.append(
                {
                    "type": param_type,
                    "name": param_name,
                    "description": (param_desc.strip() if param_desc else ""),
                }
            )

    signature = f"{return_type} {name}({params_str})"

    return FunctionDecl(
        return_type=return_type,
        name=name,
        signature=signature,
        parameters=params,
    )


def extract_doxygen_comment(lines: list[str], func_line: int) -> DocComment | None:
    """Извлечение Doxygen-комментария перед функцией.

    Args:
        lines: Все строки файла.
        func_line: Номер строки, где находится функция (0-based).

    Returns:
        DocComment или None, если комментарий не найден.
    """
    # Ищем комментарий непосредственно перед функцией
    comment_lines = []
    i = func_line - 1

    while i >= 0:
        line = lines[i].strip()

        if line.endswith("*/"):
            # Конец многострочного комментария
            comment_lines.append(line)
            i -= 1
            break
        elif line == "" or line.startswith("#"):
            # Пустая строка или препроцессор — прерываем поиск
            break
        else:
            i -= 1

    if not comment_lines:
        return None

    # Собираем все строки комментария
    while i >= 0:
        line = lines[i].strip()
        if line.startswith("/**") or line.startswith("/*"):
            comment_lines.append(line)
            break
        elif line == "":
            break
        else:
            comment_lines.append(line)
            i -= 1

    # Переворачиваем в правильном порядке
    comment_lines.reverse()
    comment_text = "\n".join(comment_lines)

    # Парсинг Doxygen
    doc = DocComment()

    brief_m = BRIEF_PATTERN.search(comment_text)
    if brief_m:
        doc.brief = brief_m.group(1).strip()

    for pm in PARAM_DESC_PATTERN.finditer(comment_text):
        doc.params[pm.group(1)] = pm.group(2).strip()

    return_m = RETURN_PATTERN.search(comment_text)
    if return_m:
        doc.returns = return_m.group(1).strip()

    return doc


def extract_function_name(text: str) -> str | None:
    """Извлечь имя функции из строки декларации.

    Args:
        text: Строка с декларацией.

    Returns:
        Имя функции или None.
    """
    m = FUNC_PATTERN.match(text.strip())
    return m.group("name").strip() if m else None
