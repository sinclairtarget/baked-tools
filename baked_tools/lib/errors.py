class BakedToolsError(Exception):
    pass


class ProjectNotFoundError(BakedToolsError):
    def __init__(self, project_name, existing_projects):
        self.project_name = project_name
        self.existing_projects = existing_projects


class MovieFileNotFoundError(BakedToolsError):
    pass


class APIKeyNotFoundError(BakedToolsError):
    def __init__(self, env_var_name):
        self.env_var_name = env_var_name

    def __str__(self):
        return f"Could not find API key in env var: {self.env_var_name}."
