import datetime
import json
import logging
import os
import typing
from dataclasses import asdict


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o: object):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)


def dump_json(data: typing.Any) -> str:
    if isinstance(data, bytes):
        return str(data)
    if isinstance(data, str):
        return data
    if isinstance(data, typing.Mapping):
        return json.dumps(typing.Mapping)
    return json.dumps(asdict(data), cls=DateTimeEncoder)


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
