import pytest

import pyocle
from pyocle.config import MissingEnvironmentVariableError


@pytest.fixture
def env():
    return {
        'CONNECTION_STRING': 'connect'
    }


def test_env_var_is_retrieved_correctly(env):
    environment_variable = pyocle.config.env_var('CONNECTION_STRING', environment=env)
    assert environment_variable is not None
    assert environment_variable == 'connect'


def test_env_var_raises_error_when_variable_does_not_exist(env):
    missing_variable = 'does not exist'
    with pytest.raises(MissingEnvironmentVariableError) as exception_info:
        pyocle.config.env_var(missing_variable, environment=env)

    exception = exception_info.value
    assert exception.env_var_name == missing_variable
    assert str(exception) == f'An environment variable with the name: {missing_variable} could not be found.'
