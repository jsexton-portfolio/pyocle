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


def test_env_var_returns_default_when_variable_is_missing(env):
    default = 'default'
    environment_variable = pyocle.config.env_var('does not exist', default=default, environment=env)
    assert environment_variable is not None
    assert environment_variable == default


def test_env_var_raises_error_when_variable_does_not_exist(env):
    missing_variable = 'does not exist'
    with pytest.raises(MissingEnvironmentVariableError) as exception_info:
        pyocle.config.env_var(missing_variable, environment=env)

    exception = exception_info.value
    assert exception.env_var_name == missing_variable
    assert str(exception) == f'An environment variable with the name: {missing_variable} could not be found.'


def test_encrypted_env_var_returns_default_when_variable_is_missing(env):
    def decrypter(value):
        """Dummy decrypter so that we do not trigger the kms decrypter"""
        return value

    default = 'default'
    environment_variable = pyocle.config.encrypted_env_var('does not exist',
                                                           default=default,
                                                           decrypter=decrypter,
                                                           environment=env)
    assert environment_variable is not None
    assert environment_variable == default
