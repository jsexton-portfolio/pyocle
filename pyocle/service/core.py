from abc import abstractmethod, ABC
from typing import Dict, Any


class BaseForm(ABC):
    """
    Represents a form or attributes that are needed to perform some AWS service action.
    Implementing this class is intended to provide a wrapper/interface around AWS boto3 client.
    """

    @abstractmethod
    def _dict(self):
        """
        :return: The AWS dict representation that will be given to the service.
        """
        pass

    def dict(self):
        """
        :return: The final AWS dict representation that will be given to the service.
        """

        def clean_dict(dictionary: Dict[str, Any]):
            return {key: clean_dict(value) if isinstance(value, dict) else value for key, value in dictionary.items()
                    if valid_entry(key, value)}

        def valid_entry(key, value) -> bool:
            return key is not None and value is not None and len(value) > 0

        return clean_dict(self._dict())


class ResourceNotFoundError(Exception):
    """
    Error raised when a resource could not be found with a particular identifier.
    """

    def __init__(self, identifier: str, message: str = None):
        self.identifier = identifier
        self.message = message or f'Resource with id {identifier} could not be found'
