import logging
import os
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def logger_setup(name: str) -> logging.Logger:
    """
    Настраивает и возвращает логгер.

    Args:
        name: Имя логгера

    Returns:
        Настроенный логгер

    Note:
        Уровень логирования и формат можно настроить через переменные окружения:
        - LOG_LEVEL: уровень логирования (по умолчанию DEBUG)
        - LOG_FORMAT: формат сообщений лога
    """
    default_format = '[%(asctime)s] %(name)-18s [%(levelname)s] %(message)s'
    log_format = os.getenv('LOG_FORMAT', default_format)
    log_formatter = logging.Formatter(log_format)
    sentry_dsn: str = os.getenv('SENTRY_DSN', '')
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above as breadcrumbs
                    event_level=logging.ERROR,  # Send records as events
                ),
            ],
        )

    try:
        log_level = int(os.getenv('LOG_LEVEL', logging.DEBUG))
        if log_level not in (
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ):
            log_level = logging.DEBUG
    except ValueError:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)
    logger = logging.getLogger(name)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(log_formatter)
    logger.addHandler(logger_handler)

    return logger
