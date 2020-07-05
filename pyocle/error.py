import logging
from typing import Optional, Dict, Any, Sequence

from pyocle import response


class FormError(Exception):
    """
    Any error that may be raised while handling a form
    """
    pass


class ServiceError(Exception):
    """
    Any error that may be raised from a service
    """
    pass


class ResourceNotFoundError(ServiceError):
    """
    Error raised when a resource could not be found with a particular identifier.
    """

    def __init__(self, identifier: str, message: str = None):
        self.identifier = identifier
        self.message = message or f'Resource with id {identifier} could not be found'


class FormValidationError(FormError):
    """
    Error raised when an incoming request form is invalid
    """

    def __init__(self,
                 error_details: Optional[Sequence[response.ErrorDetail]] = None,
                 message: str = None,
                 schema: Dict[str, Any] = None):
        self.error_details = error_details or []
        self.message = message or 'Form was not validated successfully'
        self.schema = schema


def error_handler(decorated):
    """
    Wraps functions with error handling capabilities. Be sure to include this decoration after all other decorators.

    @app.route('/)
    @error_handler
    def route():
        # route logic that potentially raises errors
    :param decorated: The function implementation that will be extended with error handling
    :return: The decorated function wrapped with error handling capabilities
    """

    def wrapped_handler(*args, **kwargs):
        try:
            return decorated(*args, **kwargs)
        except ResourceNotFoundError as ex:
            return response.not_found(ex.identifier)
        except FormValidationError as ex:
            return response.bad(error_details=ex.error_details, schema=ex.schema)
        except Exception as ex:
            logging.error('Caught exception for %s', ex)
            return response.internal_error()

    return wrapped_handler
