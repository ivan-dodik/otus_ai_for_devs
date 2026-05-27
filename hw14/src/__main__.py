"""Точка входа: python -m src

Запускает MCP сервер для OpenBCM SDK.
"""

import asyncio
import sys

from src.config import get_settings
from src.server.logger import setup_logging
from src.server.mcp_server import OpenBcmMcpServer


def main() -> None:
    """Главная функция — запуск MCP сервера."""
    settings = get_settings()
    logger = setup_logging()
    logger.info(
        "Starting OpenBCM Helper MCP Server",
        sdk_path=str(settings.openbcm_sdk_path),
    )

    # Проверка SDK_PATH
    if not settings.openbcm_sdk_path or not settings.openbcm_sdk_path.exists():
        logger.error(
            "SDK path does not exist",
            path=str(settings.openbcm_sdk_path),
        )
        print(
            f"ERROR: SDK path '{settings.openbcm_sdk_path}' does not exist. "
            f"Set OPENBCM_SDK_PATH in .env file.",
            file=sys.stderr,
        )
        sys.exit(1)

    server = OpenBcmMcpServer(settings, logger)

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
