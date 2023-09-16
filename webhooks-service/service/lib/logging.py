"""
Utility code for better logging.
"""
import logging
from logging.config import dictConfig


ORG_NAME = "baked"


def get_logger(module_name):
    return logging.getLogger(ORG_NAME + "." + module_name)


logger = get_logger(__name__)


def configure_logging(raw_log_level, filename=None):
    log_level = raw_log_level.upper()
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level":"DEBUG",
                "formatter": "default",
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
    }

    if filename:
        config["handlers"]["logfile"] = {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": filename or "out.log",
        }
        config["root"]["handlers"].append("logfile")

    dictConfig(config)
    logger.info(f"Logging configured with log level: {log_level}")
