import logging
import os


def logger_setup(name):
    default_format = "[%(asctime)s] %(name)-18s [%(levelname)s] %(message)s"
    log_format = os.getenv("LOG_FORMAT", default_format)
    try:
        from coloredlogs import ColoredFormatter
        log_formatter = ColoredFormatter(log_format)
    except ImportError:
        log_formatter = logging.Formatter(log_format)

    logging.basicConfig(
        level=logging.INFO, format=os.getenv("LOG_FORMAT", default_format)
    )
    logger = logging.getLogger(name)
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear()
    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(log_formatter)
    logger.addHandler(logger_handler)
    return logger
