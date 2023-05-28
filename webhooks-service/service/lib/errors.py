class BakedError(Exception):
    pass


class ConfigurationError(BakedError):
    pass


class UnknownStatusError(BakedError):
    pass


class APIKeyNotFoundError(BakedError):
    pass


class ProjectNotFoundError(BakedError):
    def __init__(self, project_name, existing_projects):
        self.project_name = project_name
        self.existing_projects = existing_projects

    def __str__(self):
        return f"Could not find project: {self.project_name}"


class GoogleCredentialsNotFoundError(BakedError):
    pass
