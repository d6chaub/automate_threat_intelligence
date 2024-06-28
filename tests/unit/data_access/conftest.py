import json

import pytest
from dotenv import dotenv_values

from config.config import ConfigManager


@pytest.fixture(scope="module")
def mock_feedly_data():
    """Load mock alert data from a JSON file."""
    with open('tests/unit/data_access/mock_feedly_data.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# ToDo: At some point in the future maybe refactor all this to inject the ConfigManager
#       every time so that the config manager doesn't need to be reset in this way.

@pytest.fixture(scope="function")
def load_env_vars(monkeypatch):
    """
    Load environment variables from a .env file.
    """
    print("load_env_vars called first time", flush=True)
    env_vars = dotenv_values('tests/unit/data_access/.env.test')

    for k,v in env_vars.items():
        monkeypatch.setenv(k, v)

@pytest.fixture(scope="function") # NOTE: Depends on load_env_vars, which depends on monkeypatch, which is function-scoped. So mock_config_manager must be function-scoped, even though this is less efficient. Pytest does not allow a fixture with a broader scope to depend on a fixture with a narrower scope.
def mock_config_manager(load_env_vars):
    """
    Load mock configurations for the whole app from mock yaml file and environment variables.
    Singleton 'app_configs' is reset before and after each test to avoid state leakage.
    """
    ConfigManager.reset()
    app_configs = ConfigManager('tests/unit/data_access/config/mock_alerts_sources.yaml')
    yield app_configs
    ConfigManager.reset()