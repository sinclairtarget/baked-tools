class BakedError(Exception):
    pass


class ConfigurationError(BakedError):
    pass


class UnknownStatusError(BakedError):
    pass


class APIKeyNotFoundError(BakedError):
    pass
