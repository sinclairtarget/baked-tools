"""
Loads the status mapping configuration file.
"""
import yaml
import pydantic

from .models.config import StatusMapping
from .errors import ConfigurationError


DEFAULT_STATUS_MAPPING_FILEPATH = "status_mapping.yaml"


def load_status_mapping(filepath=DEFAULT_STATUS_MAPPING_FILEPATH):
    try:
        with open(filepath, "rt") as f:
            data = yaml.safe_load(f)
    except (OSError, FileNotFoundError) as e:
        raise ConfigurationError(
            f"Could not find file at path {filepath}"
        ) from e
    except yaml.YAMLError as e:
        raise ConfigurationError(
            f"Could not parse YAML file at {filepath}. Reason: {e}"
        ) from e

    try:
        status_mapping = StatusMapping.parse_obj(data)
    except pydantic.ValidationError as e:
        raise ConfigurationError(
            f"Status mapping loaded from {filepath} was invalid. Reason: {e}"
        ) from e

    return status_mapping
