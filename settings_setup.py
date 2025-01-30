from src.core.state import project_settings, ProjectSettings, PyModuleConfig, JsonFileConfig


def setup_settings() -> ProjectSettings:
    project_settings.register_config(PyModuleConfig('src.config'))  # Must be first
    project_settings.register_config(JsonFileConfig(project_settings.SECRET_CONFIG_PATH))
    project_settings.register_config(JsonFileConfig(project_settings.STATUS_CODES_CONFIG_PATH))

    return project_settings
