"""E2E тесты для MCP сервера."""

import os
from pathlib import Path

import pytest

# Устанавливаем env переменные до импорта src.config
os.environ.setdefault("OPENBCM_SDK_PATH", "/tmp/fake_sdk_for_test")
os.environ.setdefault("OPENBCM_MCP_LOG_LEVEL", "ERROR")

from src.config import Settings
from src.server.logger import setup_logging
from src.server.mcp_server import OpenBcmMcpServer


@pytest.fixture
def fake_sdk_settings(tmp_path: Path) -> Settings:
    """Настройки с фейковым SDK."""
    sdk_root = tmp_path / "sdk"
    (sdk_root / "include/bcm").mkdir(parents=True)
    (sdk_root / "include/bcm/vlan.h").write_text(
        "/** @brief Create a new VLAN */\nint bcm_vlan_create(int unit, bcm_vlan_t vlan);\n"
    )
    (sdk_root / "src/examples").mkdir(parents=True)
    (sdk_root / "src/examples/vlan_create.c").write_text(
        "/*\n * Example\n * Tested on: Tomahawk4\n */\n#include <bcm/vlan.h>\nint test() { bcm_vlan_create(0, 100); return 0; }\n"
    )
    (sdk_root / "include/soc").mkdir(parents=True)
    (sdk_root / "include/soc/devids.h").write_text("#define BCM56980_DEVICE_ID 0x56980\n")

    os.environ["OPENBCM_SDK_PATH"] = str(sdk_root)
    os.environ["OPENBCM_MCP_LOG_LEVEL"] = "ERROR"
    os.environ["OPENBCM_MCP_CACHE_DIR"] = str(tmp_path / "cache")

    settings = Settings()
    return settings


class TestE2E:
    """E2E тесты."""

    @pytest.mark.asyncio
    async def test_server_initialization(self, fake_sdk_settings: Settings):
        """Сервер инициализируется без ошибок."""
        logger = setup_logging()
        server = OpenBcmMcpServer(fake_sdk_settings, logger)
        assert server is not None
        assert server.sdk_path is not None

    @pytest.mark.asyncio
    async def test_ping_tool(self, fake_sdk_settings: Settings):
        """Ping tool возвращает корректный результат."""
        logger = setup_logging()
        server = OpenBcmMcpServer(fake_sdk_settings, logger)

        result = await server._dispatch_tool("ping", {})
        assert result.get("ok") is True
        assert result["result"]["status"] == "ok"
        assert result["result"]["version"] == "0.1.0"
        assert result["result"]["sdk_configured"] is True

    @pytest.mark.asyncio
    async def test_get_chip_info_known_chip(self, fake_sdk_settings: Settings):
        """get_chip_info для известного чипа."""
        logger = setup_logging()
        server = OpenBcmMcpServer(fake_sdk_settings, logger)

        result = await server._dispatch_tool("get_chip_info", {"chip": "Tomahawk4"})
        assert result.get("ok") is True
        assert result["result"]["chip"] == "Tomahawk4"
        assert "BCM56980_DEVICE_ID" in result["result"]["dev_ids"]

    @pytest.mark.asyncio
    async def test_get_chip_info_unknown_chip(self, fake_sdk_settings: Settings):
        """get_chip_info для неизвестного чипа."""
        logger = setup_logging()
        server = OpenBcmMcpServer(fake_sdk_settings, logger)

        result = await server._dispatch_tool("get_chip_info", {"chip": "UnknownChip"})
        assert result.get("ok") is False

    @pytest.mark.asyncio
    async def test_dispatch_unknown_tool(self, fake_sdk_settings: Settings):
        """Вызов неизвестного инструмента."""
        logger = setup_logging()
        server = OpenBcmMcpServer(fake_sdk_settings, logger)

        result = await server._dispatch_tool("nonexistent_tool", {})
        assert result.get("ok") is False
        assert "Unknown tool" in result.get("error", "")
