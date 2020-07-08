import os
from typing import Callable, Dict, Any

from pyocle.service import KeyManagementService


class MissingEnvironmentVariableException(Exception):
    def __init__(self, env_var_name: str):
        self.env_var_name = env_var_name

    def __str__(self):
        return f'An environment variable with the name: {self.env_var_name} could not be found.'


def connection_string(default=None) -> str:
    """
    Retrieves the environment's connection string cipher text and decrypts with Key Management Service to
    connection string plain text

    :return: Environment connection string plain text.
    """
    return encrypted_env_var('CONNECTION_STRING', default=default)


def env_var(name: str, default: str = None, environment=os.environ) -> str:
    """
    Retrieves a specified environment variable.
    A default value can be provided in the case the value could not be found.
    Otherwise an exception is raised detailing that the variable could not be retrieved.

    :param name: The name of the environment variable to retrieve
    :param default: The value that will be used if no environment variable could be found.
    :param environment: The environment to attempt to retrieve the variable from. By default the os environment is used.
    :return:
    """
    try:
        return environment[name]
    except KeyError:
        if default is None:
            raise MissingEnvironmentVariableException(name)
        return default


def _kms_decrypter(value: str) -> str:
    """
    Helper function used decrypt an encrypted value with key management service.

    :param value: The value to decrypt
    :return: The decrypted value
    """
    response = KeyManagementService().decrypt(value)

    # plaintext comes back in the form of bytes. Need to decode to utf-8
    return response['Plaintext'].decode('utf-8')


def encrypted_env_var(name: str,
                      default: str = None,
                      decrypter: Callable[[str, Dict[str, Any]], str] = _kms_decrypter,
                      attrs: Dict[str, Any] = None,
                      environment=os.environ) -> str:
    """
    Retrieves a specified encrypted environment variable and decrypts the value.
    A default value can be provided in the case the value could not be found.
    Otherwise an exception is raised detailing that the variable could not be retrieved.

    :param name: The name of the environment variable to retrieve
    :param default: The value that will be used if no environment variable could be found.
    :param decrypter: Function used to decrypt the retrieved encrypted value
    :param attrs: Additional attributes that may be need to decrypt the value.
    :param environment: The environment to attempt to retrieve the variable from. By default the os environment is used.
    :return: The decrypted environment variable
    """
    if attrs is None:
        attrs = {}

    environment_variable = env_var(name, default, environment)
    return decrypter(environment_variable, **attrs)
