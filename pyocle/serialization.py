import re


class CamelCaseAttributesMixin:
    """
    Mixin intended to be used alongside jsonpickle (and any other serialization library that uses __getstate__)
    to convert all fields to camel case.

    WARNING: This mixin will break if the serialization library does not use __getstate__ to acquire information
    about an object.

    WARNING: This is not a recursive solution. Only properties at the root field will be updated.
    """

    def __getstate__(self):
        def is_snake_case(value: str) -> bool:
            """
            Really shitty function that determines if a given string is formatted using snake case.
            Simply checks for '_' character in the string.
            :param value: The string to check for snake case formatting
            :return: Whether the given string was formatted in snake case
            """
            return '_' in value

        def to_camel_case(value: str) -> str:
            """
            Converts a given string to camel case
            :param value: The snake case string that will be converted to camel case
            :return: The converted string
            """
            return snake_case_to_camel_case(value) if is_snake_case(value) else value

        # Creates a new dictionary maintaining order while only replacing the names with camel cased names instead.
        return {to_camel_case(key): value for key, value in self.__dict__.items()}


def snake_case_to_camel_case(value: str) -> str:
    """
    Converts given string from snake case to camel case
    :param value: The snake case string
    :return: The given string in camel case format
    """

    def convert(match):
        return match.group(1) + match.group(2).upper()

    # Regex matches with text before and after an under score
    # The convert function then upper cases the second group which is the text after the underscore
    regex = r'(.*?)_([a-zA-Z])'
    return re.sub(regex, convert, value, 0)
