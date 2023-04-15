import logging
from logging.config import dictConfig


ORG_NAME = "baked"


def get_logger(module_name):
    return logging.getLogger(ORG_NAME + "." + module_name)


logger = get_logger(__name__)


def configure_logging(raw_log_level):
    log_level = raw_log_level.upper()
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    dictConfig({
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "cli": {
                "format": "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
            },
        },
        "handlers": {
            "console":{
                "class": "logging.StreamHandler",
                "level":"DEBUG",
                "formatter": "cli",
                "stream": "ext://sys.stderr",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "loggers": {
            ORG_NAME: {
                "level": log_level,
            },
        }
    })

    logger.info(f"Logging configured with log level: {log_level}")
