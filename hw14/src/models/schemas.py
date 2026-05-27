"""Pydantic модели для I/O контрактов всех инструментов."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ToolMeta(BaseModel):
    """Мета-информация о выполнении инструмента."""

    elapsed_ms: int = 0
    """Время выполнения в миллисекундах."""

    source: str = ""
    """Источник данных (sqlite, ripgrep, cache)."""

    max_depth_reached: int = 0
    """Максимальная достигнутая глубина трассировки."""


class ToolResult(BaseModel, Generic[T]):
    """Универсальная обёртка результата инструмента."""

    ok: bool = True
    """Флаг успешности выполнения."""

    result: T | None = None
    """Данные результата (зависит от инструмента)."""

    error: str | None = None
    """Сообщение об ошибке (если ok=False)."""

    meta: ToolMeta = Field(default_factory=ToolMeta)
    """Мета-информация о выполнении."""


# ─── TOOL 1: ping ─────────────────────────────────────────────────


class PingResult(BaseModel):
    """Результат health-check."""

    status: str = "ok"
    """Статус сервера."""

    sdk_configured: bool = False
    """SDK path сконфигурирован и доступен."""

    indexed: bool = False
    """Индекс SDK построен."""

    version: str = "0.1.0"
    """Версия сервера."""


# ─── TOOL 2: get_sdk_info ─────────────────────────────────────────


class ModuleInfo(BaseModel):
    """Информация о модуле SDK."""

    name: str
    """Имя модуля (например, L2, L3, VLAN)."""

    api_count: int = 0
    """Количество API в модуле."""

    header_file: str = ""
    """Путь к заголовочному файлу модуля."""


class SdkInfoResult(BaseModel):
    """Информация о SDK."""

    sdk_path: str = ""
    """Путь к корню SDK."""

    version: str = ""
    """Версия SDK (определяется из файлов)."""

    indexed: bool = False
    """Индекс построен."""

    modules_count: int = 0
    """Количество модулей."""

    apis_count: int = 0
    """Общее количество API."""

    cache_dir: str = ""
    """Директория кэша."""

    modules: list[ModuleInfo] = []
    """Список модулей (если запрошено)."""


# ─── TOOL 3: find_bcm_api ─────────────────────────────────────────


class ParameterInfo(BaseModel):
    """Информация о параметре функции."""

    name: str = ""
    """Имя параметра."""

    type: str = ""
    """Тип параметра."""

    description: str = ""
    """Описание параметра (из Doxygen)."""


class ReturnInfo(BaseModel):
    """Информация о возвращаемом значении."""

    type: str = ""
    """Тип возвращаемого значения."""

    description: str = ""
    """Описание возвращаемого значения."""


class ApiResult(BaseModel):
    """Декларация API функции."""

    name: str = ""
    """Имя API."""

    signature: str = ""
    """Полная сигнатура функции."""

    module: str = ""
    """Модуль (например, VLAN, L2, L3)."""

    header: str = ""
    """Путь к заголовочному файлу."""

    line: int = 0
    """Номер строки в файле."""

    description: str = ""
    """Описание API."""

    parameters: list[ParameterInfo] = []
    """Список параметров."""

    returns: ReturnInfo = Field(default_factory=ReturnInfo)
    """Информация о возвращаемом значении."""

    chip_availability: list[str] = []
    """Список чипов, где доступно API."""

    related_apis: list[str] = []
    """Связанные API."""


# ─── TOOL 4: find_api_examples ────────────────────────────────────


class RelatedFile(BaseModel):
    """Связанный файл (лог, конфиг)."""

    path: str = ""
    """Путь к файлу."""

    type: str = ""
    """Тип файла (log, config)."""

    size_bytes: int = 0
    """Размер файла в байтах."""


class ExampleResult(BaseModel):
    """Пример использования API."""

    file: str = ""
    """Путь к файлу с примером."""

    line: int = 0
    """Номер строки."""

    snippet: str = ""
    """Фрагмент кода с контекстом."""

    source_type: str = ""
    """Тип источника (c, cint, bcm_config)."""

    script_header: str | None = None
    """Заголовок CINT скрипта (если есть)."""

    related_files: list[RelatedFile] = []
    """Связанные файлы."""


class ExampleListResult(BaseModel):
    """Список примеров использования API."""

    api: str = ""
    """Имя API."""

    total_found: int = 0
    """Общее количество найденных примеров."""

    examples: list[ExampleResult] = []
    """Список примеров."""


# ─── TOOL 5: trace_api_implementation ──────────────────────────────


class TraceEntry(BaseModel):
    """Элемент цепочки реализации."""

    level: int = 0
    """Уровень вложенности (1 = entry point)."""

    function: str = ""
    """Имя функции."""

    file: str = ""
    """Файл."""

    line: int = 0
    """Номер строки."""

    chip_conditions: list[str] = []
    """Условия доступности для чипов."""

    guard_pattern: str = ""
    """Паттерн guard (например, #if defined или SOC_IS_*)."""


class ChipBranch(BaseModel):
    """Chip-specific ветка реализации."""

    condition: str = ""
    """Условие (например, SOC_IS_TOMAHAWK4)."""

    functions: list[str] = []
    """Функции в этой ветке."""

    soc_file: str = ""
    """Файл с chip-specific кодом."""


class TraceResult(BaseModel):
    """Результат трассировки реализации."""

    api: str = ""
    """Имя API."""

    entry_point: TraceEntry = Field(default_factory=TraceEntry)
    """Точка входа (публичное API)."""

    implementation_chain: list[TraceEntry] = []
    """Цепочка реализации."""

    chip_specific_branches: list[ChipBranch] = []
    """Chip-specific ветки."""


# ─── TOOL 6: get_chip_info ─────────────────────────────────────────


class ChipCintScript(BaseModel):
    """CINT скрипт, связанный с чипом."""

    file: str = ""
    """Путь к скрипту."""

    header: str = ""
    """Заголовок скрипта."""

    apis_used: list[str] = []
    """API, используемые в скрипте."""


class ChipInfoResult(BaseModel):
    """Информация о чипе."""

    chip: str = ""
    """Имя чипа."""

    dev_ids: list[str] = []
    """Идентификаторы устройств."""

    feature_macros: list[str] = []
    """Feature macros."""

    modules: list[str] = []
    """Поддерживаемые модули."""

    soc_directories: list[str] = []
    """Директории с SOC-специфичным кодом."""

    api_count_estimate: int = 0
    """Оценочное количество API."""

    example_apis: list[str] = []
    """Примеры API."""

    cint_scripts: list[ChipCintScript] = []
    """CINT скрипты для этого чипа."""


# ─── TOOL 7: find_cint_scripts ────────────────────────────────────


class CintScriptResult(BaseModel):
    """Результат поиска CINT скрипта."""

    file: str = ""
    """Путь к скрипту."""

    header_comment: str | None = None
    """Заголовочный комментарий."""

    apis_used: list[str] = []
    """API, используемые в скрипте."""

    related_files: list[RelatedFile] = []
    """Связанные файлы."""


class CintScriptListResult(BaseModel):
    """Список CINT скриптов."""

    query: str = ""
    """Поисковый запрос."""

    total_found: int = 0
    """Количество найденных скриптов."""

    scripts: list[CintScriptResult] = []
    """Список скриптов."""
