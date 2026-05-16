import json
import logging
from typing import Any

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format=_LOG_FORMAT, force=True)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_action(logger: logging.Logger, message: str, **fields: Any) -> None:
    payload = {"message": message, **fields}
    logger.info(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str))


def log_error(logger: logging.Logger, message: str, **fields: Any) -> None:
    payload = {"message": message, **fields}
    logger.error(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str))
