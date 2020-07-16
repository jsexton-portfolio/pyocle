import logging
from typing import Any, Union, Sequence, Optional, Dict, List

import jsonpickle
from chalice import Response

from pyocle.form import PaginationQueryParameters, FormValidationError
from pyocle.serialization import CamelCaseAttributesMixin
from pyocle.service import ResourceNotFoundError


class ErrorDetail(CamelCaseAttributesMixin):
    """
    Represents a field error and details around why this field caused an error and other meta data.
    """

    def __init__(self, description: str, location: str):
        self.description = description
        self.location = location

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ErrorDetail) and \
               other.location == self.location and \
               other.description == self.description

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __repr__(self):
        return f'FieldErrorDetail(description={self.description}, location={self.location})'


class PaginationDetails:
    """
    Model holding a particular requests pagination details
    """

    def __init__(self, page: int, limit: int, **kwargs):
        self.page = page
        self.limit = limit

    def __repr__(self):
        return f'PaginationDetails(page={self.page}, limit={self.limit})'


class MetaData(CamelCaseAttributesMixin):
    """
    Represents meta/introspected information about a response.
    """

    def __init__(self,
                 message: str,
                 error_details: Optional[Sequence[ErrorDetail]] = None,
                 pagination_details: Optional[PaginationDetails] = None,
                 schemas: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_details = error_details or []
        self.pagination_details = pagination_details or {}
        self.schemas = schemas or {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MetaData) and \
               other.message == self.message and \
               other.schemas == self.schemas and \
               other.error_details == self.error_details and \
               other.pagination_details == self.pagination_details

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __repr__(self):
        return (f'MetaData(message=\'{self.message}\','
                f' error_details={self.error_details},'
                f' pagination_details={self.pagination_details},'
                f' schemas={self.schemas})')


class ResponseBody:
    """
    Represents a response originating from this API.

    All response bodies are expected to have success, meta and data fields.
    """

    def __init__(self, success: bool, meta: MetaData, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.meta = meta
        self.data = data

    def to_json(self):
        return jsonpickle.dumps(self, unpicklable=False)


def ok_metadata(pagination: Optional[PaginationQueryParameters] = None) -> MetaData:
    """
    :return: Successful request (Ok) meta data
    """
    pagination_details = None if pagination is None else PaginationDetails(**pagination.dict())
    return metadata(message='Request completed successfully',
                    pagination_details=pagination_details)


def bad_metadata(error_details: Sequence[ErrorDetail] = None,
                 schemas: Optional[Dict[str, Any]] = None) -> MetaData:
    """
    :param error_details: Error details that will be used to construct meta data
    :param schemas: Schemas that will be used to construct meta data
    :return: Bad request meta data
    """
    return metadata(
        message='Given inputs were incorrect. Consult the below details to address the issue.',
        error_details=error_details or [],
        schemas=schemas if schemas is not None else {}
    )


def not_found_metadata(identifier: Union[str, int]) -> MetaData:
    """
    :param identifier: Identifier that will be used to construct message in meta data
    :return: Not found meta data
    """
    return metadata(message=f'Resource with id {identifier} does not exist')


def internal_error_metadata() -> MetaData:
    """
    :return: Internal server error meta data
    """
    return metadata(message='Request failed due to internal server error')


def metadata(message: str,
             error_details: Optional[Sequence[ErrorDetail]] = None,
             pagination_details: Optional[PaginationDetails] = None,
             schemas: Optional[Dict[str, Any]] = None) -> MetaData:
    """
    Factory method for metadata objects

    :param error_details: Error details that will be used to construct meta data
    :param schemas: Schemas that will be used to construct meta data
    :param pagination_details: Information describing what pagination rules were applied when collecting data
    :param message: The message that will be used in the meta object
    :return: The created
    """
    return MetaData(
        message=message,
        error_details=error_details,
        pagination_details=pagination_details,
        schemas=schemas
    )


def ok(data: Any, pagination: Optional[PaginationQueryParameters] = None) -> Response:
    """
    :param data: Data that will be used to populate the response body
    :param pagination: Pagination meta data used to collect the ok response data
    :return: Ok response
    """
    return response(200, ok_metadata(pagination), data)


def created(data: Any) -> Response:
    """
    :param data: Data that will be used to populate the response body
    :return: Created response
    """
    return response(201, meta=ok_metadata(), data=data)


def bad(error_details: Sequence[ErrorDetail] = None,
        schemas: Optional[Dict[str, Any]] = None) -> Response:
    """
    :param error_details: Details detailing why the request was bad. These details will be used
    in the response body.
    :param schemas: Schemas that will be displayed in meta information of response
    :return: Bad request response
    """
    response_metadata = bad_metadata(error_details=error_details, schemas=schemas)
    return response(400, response_metadata)


def not_found(identifier: Union[str, int]) -> Response:
    """
    :param identifier: Identifier that was used to attempt to select a resource, but could not.
    This value will be used in the body message description.
    :return: Not found response
    """
    response_metadata = not_found_metadata(identifier)
    return response(404, response_metadata)


def internal_error() -> Response:
    """
    :return: Internal server error response
    """
    return response(500, internal_error_metadata())


def response(status_code: int,
             meta: MetaData,
             data: Dict[str, Any] = None,
             headers: Optional[Dict[str, Any]] = None) -> Response:
    """
    Creates response instances from various information

    :param status_code: The status code that will be used to construct the response.
     Also used to determine if the response is a success or not. This information is populated in the body.
    :param meta: Response meta information
    :param data: Data element that will be used to populate the body content
    :param headers: Headers that will be used to construct the response
    :return: The created response information
    """
    success = status_code < 400
    body = ResponseBody(success=success, meta=meta, data=data)
    json_body = body.to_json()

    return Response(status_code=status_code, body=json_body, headers=headers)


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
            return not_found(ex.identifier)
        except FormValidationError as ex:
            error_details = _build_error_details(ex.errors)
            return bad(error_details=error_details, schemas=ex.schemas)
        except Exception as ex:
            logger = logging.getLogger(__name__)
            logger.error('Something crashed, view the below traceback for more information')
            logger.exception(ex)
            return internal_error()

    return wrapped_handler


def _build_error_details(errors: List[Dict[str, Any]]) -> Sequence[ErrorDetail]:
    """
    Creates list of error details from given pydantic errors

    :param errors: List of pydantic errors
    :return: List of field error details built from given pydantic errors
    """
    return [ErrorDetail(location='.'.join(error['loc']), description=error['msg']) for error in errors]
