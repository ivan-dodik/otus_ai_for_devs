"""MCP сервер для OpenBCM SDK.

Регистрирует все инструменты через list_tools/call_tool хендлеры,
настраивает логирование, инициализирует зависимости.
"""

from __future__ import annotations

import time
from pathlib import Path

import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    TextContent,
    Tool,
)

from src.config import Settings
from src.indexer.chip_map import ChipMap
from src.indexer.sdk_indexer import SdkIndexer
from src.security.path_guard import PathGuard
from src.tools.find_api_examples import run_find_api_examples
from src.tools.find_bcm_api import run_find_bcm_api
from src.tools.find_cint_scripts import run_find_cint_scripts
from src.tools.get_chip_info import run_get_chip_info
from src.tools.get_sdk_info import run_get_sdk_info
from src.tools.ping import run_ping
from src.tools.trace_implementation import run_trace_implementation

# Определения инструментов
TOOL_DEFINITIONS: list[Tool] = [
    Tool(
        name="ping",
        description="Health check — проверка, что сервер работает и SDK сконфигурирован",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_sdk_info",
        description="Информация о SDK: версия, путь, статус индексации, количество API",
        inputSchema={
            "type": "object",
            "properties": {
                "include_modules": {
                    "type": "boolean",
                    "description": "Показать список модулей",
                    "default": False,
                },
            },
        },
    ),
    Tool(
        name="find_bcm_api",
        description="Поиск декларации BCM API в заголовочных файлах SDK",
        inputSchema={
            "type": "object",
            "properties": {
                "api": {
                    "type": "string",
                    "description": "Имя API (например, bcm_vlan_create)",
                },
                "chip": {
                    "type": "string",
                    "description": "Фильтр по чипу (Tomahawk4, Trident3, all)",
                    "default": "all",
                },
                "fuzzy": {
                    "type": "boolean",
                    "description": "Включить нечёткий поиск при отсутствии точного совпадения",
                    "default": False,
                },
            },
            "required": ["api"],
        },
    ),
    Tool(
        name="find_api_examples",
        description="Поиск примеров использования API в C-коде и CINT скриптах",
        inputSchema={
            "type": "object",
            "properties": {
                "api": {
                    "type": "string",
                    "description": "Имя API (например, bcm_l3_route_add)",
                },
                "source_type": {
                    "type": "string",
                    "description": "all, c, cint, bcm_config",
                    "default": "all",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Максимум результатов (max 50)",
                    "default": 10,
                },
                "context_lines": {
                    "type": "integer",
                    "description": "Строк контекста (max 10)",
                    "default": 3,
                },
                "include_full_source": {
                    "type": "boolean",
                    "description": "Показать полный исходник CINT скрипта",
                    "default": False,
                },
            },
            "required": ["api"],
        },
    ),
    Tool(
        name="trace_api_implementation",
        description="Показать цепочку реализации от public API до chip-specific кода",
        inputSchema={
            "type": "object",
            "properties": {
                "api": {
                    "type": "string",
                    "description": "Имя API",
                },
                "chip": {
                    "type": "string",
                    "description": "Фильтр по чипу",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Глубина трассировки (max 7)",
                    "default": 3,
                },
            },
            "required": ["api"],
        },
    ),
    Tool(
        name="get_chip_info",
        description="Получить сводку по ASIC: dev ids, feature macros, модули, CINT скрипты",
        inputSchema={
            "type": "object",
            "properties": {
                "chip": {
                    "type": "string",
                    "description": "Имя чипа (Tomahawk4, Trident3, Jericho2)",
                },
                "include_apis": {
                    "type": "boolean",
                    "description": "Показать примеры API",
                    "default": False,
                },
                "include_cint_scripts": {
                    "type": "boolean",
                    "description": "Показать CINT скрипты для этого чипа",
                    "default": False,
                },
            },
            "required": ["chip"],
        },
    ),
    Tool(
        name="find_cint_scripts",
        description="Поиск CINT скриптов по функционалу, чипу или параметрам",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос (функционал, чип, имя файла)",
                },
                "chip": {
                    "type": "string",
                    "description": "Фильтр по чипу",
                },
                "include_logs": {
                    "type": "boolean",
                    "description": "Включить логи вывода",
                    "default": False,
                },
                "include_configs": {
                    "type": "boolean",
                    "description": "Включить .bcm конфиги",
                    "default": False,
                },
                "include_full_source": {
                    "type": "boolean",
                    "description": "Показать полный исходник",
                    "default": False,
                },
            },
            "required": ["query"],
        },
    ),
]


class OpenBcmMcpServer:
    """MCP сервер для OpenBCM SDK."""

    def __init__(self, settings: Settings, logger: structlog.stdlib.BoundLogger) -> None:
        """Инициализация сервера."""
        self.settings = settings
        self.logger = logger
        self.server = Server("openbcm-helper")

        # Инициализация зависимостей
        self.sdk_path: Path = settings.openbcm_sdk_path or Path("/nonexistent")
        self.path_guard = PathGuard(self.sdk_path)
        self.chip_map = ChipMap(settings.resolved_config_dir / "chip_map.json")
        self.indexer = SdkIndexer(
            self.sdk_path,
            settings.resolved_cache_dir,
            self.chip_map,
        )

        # Индексация при старте (ленивая)
        self._index_ready = False

        self._register_handlers()

    def _register_handlers(self) -> None:
        """Регистрация list_tools и call_tool хендлеров."""

        @self.server.list_tools()  # type: ignore
        async def handle_list_tools() -> list[Tool]:
            """Возвращает список доступных инструментов."""
            return TOOL_DEFINITIONS

        @self.server.call_tool()  # type: ignore
        async def handle_call_tool(tool_name: str, arguments: dict[str, object]) -> CallToolResult:
            """Обработка вызова инструмента."""
            start = time.time()

            self.logger.info(
                "tool_call",
                tool=tool_name,
                params={k: v for k, v in arguments.items() if k not in ("sdk_path",)},
            )

            try:
                result = await self._dispatch_tool(tool_name, arguments)
                elapsed = int((time.time() - start) * 1000)

                self.logger.info(
                    "tool_result",
                    tool=tool_name,
                    status="success" if result.get("ok") else "error",
                    elapsed_ms=elapsed,
                )

                return CallToolResult(content=[TextContent(type="text", text=str(result))])
            except Exception as e:
                elapsed = int((time.time() - start) * 1000)
                self.logger.error(
                    "tool_result",
                    tool=tool_name,
                    status="error",
                    error=str(e),
                    elapsed_ms=elapsed,
                )
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=str(
                                {
                                    "ok": False,
                                    "error": str(e),
                                    "meta": {"elapsed_ms": elapsed},
                                }
                            ),
                        )
                    ]
                )

    async def _dispatch_tool(
        self, tool_name: str, arguments: dict[str, object]
    ) -> dict[str, object]:
        """Вызов конкретного инструмента."""
        if tool_name == "ping":
            self._ensure_indexed()
            return await run_ping(
                sdk_path=self.sdk_path,
                index_ready=self._index_ready,
            )

        elif tool_name == "get_sdk_info":
            self._ensure_indexed()
            return await run_get_sdk_info(
                sdk_path=self.sdk_path,
                indexer=self.indexer,
                include_modules=bool(arguments.get("include_modules", False)),
            )

        elif tool_name == "find_bcm_api":
            self._ensure_indexed()
            return await run_find_bcm_api(
                api=str(arguments["api"]),
                indexer=self.indexer,
                chip=str(arguments.get("chip", "all")),
                fuzzy=bool(arguments.get("fuzzy", False)),
            )

        elif tool_name == "find_api_examples":
            return await run_find_api_examples(
                api=str(arguments["api"]),
                sdk_path=self.sdk_path,
                source_type=str(arguments.get("source_type", "all")),
                max_results=int(str(arguments.get("max_results", 10))),
                context_lines=int(str(arguments.get("context_lines", 3))),
                include_full_source=bool(arguments.get("include_full_source", False)),
            )

        elif tool_name == "trace_api_implementation":
            chip_val = arguments.get("chip")
            return await run_trace_implementation(
                api=str(arguments["api"]),
                sdk_path=self.sdk_path,
                chip=str(chip_val) if chip_val is not None else None,
                max_depth=int(str(arguments.get("max_depth", 3))),
            )

        elif tool_name == "get_chip_info":
            return await run_get_chip_info(
                chip=str(arguments["chip"]),
                chip_map=self.chip_map,
                sdk_path=self.sdk_path,
                include_apis=bool(arguments.get("include_apis", False)),
                include_cint_scripts=bool(arguments.get("include_cint_scripts", False)),
            )

        elif tool_name == "find_cint_scripts":
            chip_val = arguments.get("chip")
            return await run_find_cint_scripts(
                query=str(arguments["query"]),
                sdk_path=self.sdk_path,
                chip=str(chip_val) if chip_val is not None else None,
                include_logs=bool(arguments.get("include_logs", False)),
                include_configs=bool(arguments.get("include_configs", False)),
                include_full_source=bool(arguments.get("include_full_source", False)),
            )

        else:
            return {"ok": False, "error": f"Unknown tool: {tool_name}"}

    def _ensure_indexed(self) -> None:
        """Обеспечить, что индекс SDK построен."""
        if not self._index_ready:
            self.logger.info("index", status="starting")
            stats = self.indexer.index()
            self._index_ready = True
            self.logger.info(
                "index",
                status="done",
                functions=stats.functions_count,
                macros=stats.macros_count,
                modules=stats.modules_count,
                elapsed_ms=stats.elapsed_ms,
            )

    async def run(self) -> None:
        """Запуск сервера через stdio транспорт."""
        self.logger.info(
            "server_start",
            sdk_path=str(self.sdk_path),
            cache_dir=str(self.settings.openbcm_mcp_cache_dir),
        )

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )
