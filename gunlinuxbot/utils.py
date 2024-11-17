import logging
import importlib.util
import os


def logger_setup(name):
    default_format = "[%(asctime)s] %(name)-18s [%(levelname)s] %(message)s"
    log_format = os.getenv("LOG_FORMAT", default_format)
    if importlib.util.find_spec("coloredlogs"):
        from coloredlogs import ColoredFormatter
        log_formatter = ColoredFormatter(log_format)
    else:
        log_formatter = logging.Formatter(log_format)

    logging.basicConfig(
        level=int(os.getenv("LOG_LEVEL", logging.INFO)),
    )
    logger = logging.getLogger(name)
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear()
    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(log_formatter)
    logger.addHandler(logger_handler)
    return logger
