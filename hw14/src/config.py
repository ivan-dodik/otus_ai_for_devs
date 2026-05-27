"""Конфигурация приложения из переменных окружения и .env файла."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings

# Корень проекта — директория, где находится src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Настройки OpenBCM Helper MCP Server.

    Загружаются из переменных окружения (с приоритетом) или из .env файла.
    """

    openbcm_sdk_path: Path | None = None
    """Путь к корню OpenBCM SDK (обязательный параметр)."""

    openbcm_mcp_log_level: str = "INFO"
    """Уровень логирования (DEBUG, INFO, WARNING, ERROR)."""

    openbcm_mcp_cache_dir: Path = Path("./cache")
    """Директория для кэша (SQLite индекс)."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def resolved_cache_dir(self) -> Path:
        """Абсолютный путь к кэшу."""
        cache = self.openbcm_mcp_cache_dir
        if not cache.is_absolute():
            cache = PROJECT_ROOT / cache
        cache.mkdir(parents=True, exist_ok=True)
        return cache

    @property
    def resolved_config_dir(self) -> Path:
        """Абсолютный путь к config/."""
        return PROJECT_ROOT / "config"


def get_settings() -> Settings:
    """Создать и вернуть настройки.

    Используется вместо синглтона для поддержки тестов.
    """
    return Settings()
