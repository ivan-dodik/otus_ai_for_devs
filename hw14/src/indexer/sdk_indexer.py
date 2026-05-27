"""Индексация SDK в SQLite.

Сканирует заголовочные файлы SDK, парсит декларации BCM API,
извлекает Doxygen-комментарии, chip guards и сохраняет в SQLite.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.indexer.chip_map import ChipMap
from src.search.macro_parser import extract_macros
from src.search.rg_search import rg_files


@dataclass
class IndexStats:
    """Статистика индексации."""

    functions_count: int = 0
    """Количество проиндексированных функций."""
    macros_count: int = 0
    """Количество макросов."""
    modules_count: int = 0
    """Количество модулей."""
    elapsed_ms: int = 0
    """Время индексации в миллисекундах."""


class SdkIndexer:
    """Индексатор SDK.

    Сканирует заголовочные файлы SDK, парсит функции и макросы,
    сохраняет в SQLite для быстрого поиска.
    """

    def __init__(
        self,
        sdk_path: Path,
        cache_dir: Path,
        chip_map: ChipMap,
    ) -> None:
        """Инициализация индексатора.

        Args:
            sdk_path: Путь к корню SDK.
            cache_dir: Директория для кэша.
            chip_map: Маппинг чипов.
        """
        self.sdk_path = sdk_path
        self.cache_dir = cache_dir
        self.chip_map = chip_map
        self.db_path = cache_dir / "index.db"
        self._conn: sqlite3.Connection | None = None

    def _get_connection(self) -> sqlite3.Connection:
        """Получить соединение с БД (создать, если нужно)."""
        if self._conn is None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=OFF")
            self._init_schema()
        return self._conn

    def _init_schema(self) -> None:
        """Инициализация схемы БД."""
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists() and self._conn is not None:
            with open(schema_path) as f:
                self._conn.executescript(f.read())

    def ensure_indexed(self) -> bool:
        """Проверить, есть ли индекс. Если нет — запустить индексацию.

        Returns:
            True если индекс готов.
        """
        if not self.db_path.exists() or self.db_path.stat().st_size == 0:
            self.index()
            return True
        return True

    def needs_reindex(self) -> bool:
        """Проверить, изменился ли SDK после последней индексации.

        Returns:
            True если нужна переиндексация.
        """
        if not self.db_path.exists():
            return True

        # Проверяем время модификации
        index_mtime = self.db_path.stat().st_mtime

        # Проверяем include/bcm/ директорию
        bcm_dir = self.sdk_path / "include" / "bcm"
        if bcm_dir.exists():
            latest_mtime = max(p.stat().st_mtime for p in bcm_dir.rglob("*.h") if p.is_file())
            if latest_mtime > index_mtime:
                return True

        return False

    def index(self) -> IndexStats:
        """Полная индексация SDK.

        Returns:
            Статистика индексации.
        """
        start = time.time()
        conn = self._get_connection()

        # Очищаем старые данные
        conn.executescript(
            "DELETE FROM functions; DELETE FROM function_params; "
            "DELETE FROM macros; DELETE FROM api_macros;"
        )

        # Индексация функций из заголовочных файлов
        self._index_functions()
        self._index_macros()

        elapsed = int((time.time() - start) * 1000)

        # Собираем статистику
        cur = conn.execute("SELECT COUNT(*) FROM functions")
        func_count = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM macros")
        macro_count = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(DISTINCT module) FROM functions WHERE module != ''")
        mod_count = cur.fetchone()[0]

        return IndexStats(
            functions_count=func_count,
            macros_count=macro_count,
            modules_count=mod_count,
            elapsed_ms=elapsed,
        )

    def _index_functions(self) -> None:
        """Индексация функций из include/bcm/*.h."""
        conn = self._get_connection()
        bcm_dir = self.sdk_path / "include" / "bcm"

        if not bcm_dir.exists():
            return

        # Поиск деклараций через rg — ищем bcm_ функции без привязки к началу строки
        func_pattern = r"\bbcm_\w+\s*\("
        matches = rg_files(
            pattern=func_pattern,
            path=bcm_dir,
            file_pattern="*.h",
        )

        # Для каждого файла читаем и парсим декларации
        header_files = matches
        for h_file in header_files:
            try:
                with open(h_file, errors="replace") as f:
                    content = f.read()
            except (FileNotFoundError, PermissionError):
                continue

            # Удаляем комментарии
            import re as _re

            content_no_comments = _re.sub(r"/\*.*?\*/", "", content, flags=_re.DOTALL)

            for match in _re.finditer(
                r"(?:extern\s+)?(\w+(?:\s*\*)?)\s+(\w+)\s*\(([^)]*)\)\s*;",
                content_no_comments,
            ):
                if not match.group(2).startswith("bcm_"):
                    continue

                return_type = match.group(1).strip()
                name = match.group(2).strip()
                params_str = match.group(3).strip()

                if not name.startswith("bcm_"):
                    continue

                # Парсинг параметров
                params = []
                if params_str and params_str != "void":
                    for p in _re.finditer(
                        r"(\w+(?:\s*\*)?)\s+(\w+)\s*",
                        params_str,
                    ):
                        params.append(
                            {
                                "type": p.group(1).strip(),
                                "name": p.group(2).strip(),
                                "description": "",
                            }
                        )

                signature = f"{return_type} {name}({params_str})"
                module = name.split("_")[1].upper() if len(name.split("_")) > 1 else ""

                # Определяем строку в файле
                line_no = 1
                for i, fline in enumerate(content.split("\n")):
                    if name in fline:
                        line_no = i + 1
                        break

                conn.execute(
                    """INSERT OR IGNORE INTO functions
                       (name, signature, return_type, file_path, line, module, description, doc_comment, chip_macros)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        name,
                        signature,
                        return_type,
                        str(h_file),
                        line_no,
                        module,
                        "",
                        "{}",
                        "[]",
                    ),
                )

    def _index_macros(self) -> None:
        """Индексация макросов из всех .h файлов."""
        conn = self._get_connection()
        include_path = self.sdk_path / "include"

        if not include_path.exists():
            return

        # Ищем .h файлы с макросами
        h_files = list(include_path.rglob("*.h"))

        for h_file in h_files:
            try:
                with open(h_file, errors="replace") as f:
                    lines = f.readlines()
            except (FileNotFoundError, PermissionError):
                continue

            macros = extract_macros(lines)
            for macro in macros:
                # Определяем ассоциацию с чипом
                chip_assoc = ""
                if "BCM_" in macro.name and "_SUPPORT" in macro.name:
                    # Ищем чип по макросу
                    for chip_name in self.chip_map.list_chips():
                        chip_data = self.chip_map.get_chip(chip_name)
                        if chip_data and macro.name in chip_data.get("feature_macros", []):
                            chip_assoc = chip_name
                            break

                conn.execute(
                    """INSERT OR IGNORE INTO macros
                       (name, definition_file, definition_line, definition_value, chip_association)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        macro.name,
                        str(h_file),
                        macro.line,
                        macro.value,
                        chip_assoc,
                    ),
                )

    def search_api(
        self,
        name: str,
        chip: str | None = None,
        fuzzy: bool = False,
    ) -> list[dict[str, Any]]:
        """Поиск API в индексе.

        Args:
            name: Имя API (например, "bcm_vlan_create").
            chip: Фильтр по чипу (например, "Tomahawk4").
            fuzzy: Включить нечёткий поиск при отсутствии точного совпадения.

        Returns:
            Список результатов.
        """
        conn = self._get_connection()

        # Точный поиск
        cur = conn.execute(
            """SELECT f.*, GROUP_CONCAT(fp.name || ':' || fp.param_type || ':' || fp.description, '|')
               FROM functions f
               LEFT JOIN function_params fp ON fp.function_id = f.id
               WHERE f.name = ?
               GROUP BY f.id""",
            (name,),
        )
        results = self._rows_to_dicts(cur)

        # Фильтр по чипу
        if chip and chip != "all" and results:
            chip_data = self.chip_map.get_chip(chip)
            if chip_data:
                chip_macros = chip_data.get("feature_macros", [])
                filtered = []
                for r in results:
                    r_macros = json.loads(r.get("chip_macros", "[]"))
                    if any(m in chip_macros for m in r_macros):
                        filtered.append(r)
                results = filtered

        # Fuzzy поиск при отсутствии точного совпадения
        if not results and fuzzy:
            from rapidfuzz import fuzz, process

            cur = conn.execute("SELECT DISTINCT name FROM functions")
            all_names = [row[0] for row in cur.fetchall()]

            matches = process.extract(
                name,
                all_names,
                scorer=fuzz.WRatio,
                limit=5,
            )
            if matches:
                fuzzy_names = [m[0] for m in matches if m[1] > 60]
                for fname in fuzzy_names:
                    cur = conn.execute(
                        """SELECT f.*, GROUP_CONCAT(fp.name || ':' || fp.param_type || ':' || fp.description, '|')
                           FROM functions f
                           LEFT JOIN function_params fp ON fp.function_id = f.id
                           WHERE f.name = ?
                           GROUP BY f.id""",
                        (fname,),
                    )
                    results.extend(self._rows_to_dicts(cur))

        return results

    def get_stats(self) -> IndexStats:
        """Получить статистику индекса.

        Returns:
            IndexStats.
        """
        conn = self._get_connection()

        cur = conn.execute("SELECT COUNT(*) FROM functions")
        func_count = cur.fetchone()[0]

        cur = conn.execute("SELECT COUNT(*) FROM macros")
        macro_count = cur.fetchone()[0]

        cur = conn.execute("SELECT COUNT(DISTINCT module) FROM functions WHERE module != ''")
        mod_count = cur.fetchone()[0]

        return IndexStats(
            functions_count=func_count,
            macros_count=macro_count,
            modules_count=mod_count,
        )

    @staticmethod
    def _rows_to_dicts(cur: sqlite3.Cursor) -> list[dict[str, Any]]:
        """Преобразовать строки курсора в список словарей."""
        columns = [desc[0] for desc in cur.description]
        results = []
        for row in cur.fetchall():
            d = dict(zip(columns, row, strict=False))
            results.append(d)
        return results
