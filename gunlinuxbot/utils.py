import importlib.util
import logging
import os


def logger_setup(name: str) -> logging.Logger:
    default_format = "[%(asctime)s] %(name)-18s [%(levelname)s] %(message)s"
    log_format = os.getenv("LOG_FORMAT", default_format)
    log_formatter = logging.Formatter(log_format)

    logging.basicConfig(
        level=int(os.getenv("LOG_LEVEL", logging.DEBUG)),
    )
    logger = logging.getLogger(name)
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear()
    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(log_formatter)
    logger.addHandler(logger_handler)
    return logger
