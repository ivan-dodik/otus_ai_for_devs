"""Настройка структурированного логирования через structlog."""

import structlog


def setup_logging() -> structlog.stdlib.BoundLogger:
    """Настройка structlog.

    Уровень логирования берётся из переменной окружения OPENBCM_MCP_LOG_LEVEL
    (по умолчанию INFO).

    Returns:
        Настроенный логгер.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()  # type: ignore[no-any-return]
