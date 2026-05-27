"""Загрузка и предоставление маппинга чипов из JSON конфига."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ChipMap:
    """Маппинг имён чипов на их характеристики (dev ids, feature macros, модули)."""

    def __init__(self, config_path: Path) -> None:
        """Загрузка маппинга из JSON файла.

        Args:
            config_path: Путь к config/chip_map.json.
        """
        with open(config_path) as f:
            self._data: dict[str, Any] = json.load(f)

    def get_chip(self, name: str) -> dict[str, Any] | None:
        """Получить информацию о чипе по имени.

        Args:
            name: Имя чипа (например, "Tomahawk4").

        Returns:
            Словарь с данными чипа или None.
        """
        # Поиск точного совпадения
        if name in self._data:
            return self._data[name]  # type: ignore[no-any-return]

        # Поиск по частичному совпадению (case-insensitive)
        name_lower = name.lower()
        for chip_name, chip_data in self._data.items():
            if chip_name.lower() == name_lower:
                return chip_data  # type: ignore[no-any-return]
            if name_lower in chip_name.lower():
                return chip_data  # type: ignore[no-any-return]

        return None

    def list_chips(self) -> list[str]:
        """Список всех известных чипов.

        Returns:
            Список имён чипов.
        """
        return list(self._data.keys())

    def get_feature_macros(self, chip: str) -> list[str]:
        """Получить feature macros для чипа.

        Args:
            chip: Имя чипа.

        Returns:
            Список макросов или пустой список.
        """
        chip_data = self.get_chip(chip)
        return chip_data.get("feature_macros", []) if chip_data else []
