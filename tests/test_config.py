import pytest

from pyocle import config


@pytest.fixture
def env():
    return {
        'CONNECTION_STRING': 'connect'
    }


def test_env_var_is_retrieved_correctly(env):
    environment_variable = config.env_var('CONNECTION_STRING', environment=env)
    assert environment_variable is not None
    assert environment_variable == 'connect'
