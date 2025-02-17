from dataclasses import dataclass, asdict
import logging
import json
import os
import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def dump_json(data: dataclass) -> str:
    return json.dumps(asdict(data), cls=DateTimeEncoder)


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
