import re

from pyocle.serialization import CamelCaseAttributesMixin


class DummyModel(CamelCaseAttributesMixin):
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name


def test_get_state_produces_dictionary_with_camel_cased_keys():
    dummy = DummyModel('first', 'last')
    assert not all([_is_camel_case(attribute_names) for attribute_names in dir(dummy)])

    state = dummy.__getstate__()
    assert all([_is_camel_case(key) for key in state.keys()])


def _is_camel_case(string: str) -> bool:
    """
    Helper method used to determine if a given string is camel case or not. See the below details on the
    exact rules that are applied.

    1. First series of characters should be lower case
    2. Every character group afterwards should string with an upper case character followed by lower case.
    3. The last character is allowed to be upper case lower case or a number

    :param string: The string value to check if camel cased
    :return: Whether the given string was camel cased or not
    """
    pattern = re.compile(r'[a-z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*')
    return re.match(pattern=pattern, string=string) is not None
