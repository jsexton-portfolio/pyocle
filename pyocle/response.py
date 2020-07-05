from typing import Any, Union, Sequence, Optional, Dict

import jsonpickle
from chalice import Response

from pyocle.serialization import CamelCaseAttributesMixin


class ErrorDetail(CamelCaseAttributesMixin):
    """
    Represents any error information regarding a request. Will mostly be used in 400 Bad Request responses.
    """

    def __init__(self, description: str):
        self.description = description

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ErrorDetail) and other.description == self.description

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __repr__(self):
        return f'ErrorDetail(description={self.description})'


class FieldErrorDetail(ErrorDetail):
    """
    Represents a field error and details around why this field caused an error and other meta data.
    """

    def __init__(self, description: str, field_name: str):
        super().__init__(description)
        self.field_name = field_name

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, FieldErrorDetail) and other.field_name == self.field_name

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __repr__(self):
        return f'FieldErrorDetail(description={self.description}, field_name={self.field_name})'


class MetaData(CamelCaseAttributesMixin):
    """
    Represents meta/introspected information about a response.
    """

    def __init__(self,
                 message: str,
                 error_details: Optional[Sequence[ErrorDetail]] = None,
                 schemas: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_details = error_details or []
        self.schemas = schemas or {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MetaData) and \
               other.message == self.message and \
               other.schemas == self.schemas and \
               other.error_details == self.error_details

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __repr__(self):
        return f'MetaData(message=\'{self.message}\', error_details={self.error_details}, schemas={self.schemas})'


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


def ok_metadata() -> MetaData:
    """
    :return: Successful request (Ok) meta data
    """
    return metadata(message='Request completed successfully')


def bad_metadata(error_details: Sequence[ErrorDetail] = None,
                 schema: Optional[Dict[str, Any]] = None) -> MetaData:
    """
    :param error_details: Error details that will be used to construct meta data
    :param schema: Schema that will be used to construct meta data
    :return: Bad request meta data
    """
    return metadata(
        message='Given inputs were incorrect. Consult the below details to address the issue.',
        error_details=error_details or [],
        schemas={'requestBody': schema} if schema is not None else {}
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
             schemas: Optional[Dict[str, Any]] = None) -> MetaData:
    """
    Factory method for metadata objects

    :param error_details: Error details that will be used to construct meta data
    :param schemas: Schema that will be used to construct meta data
    :param message: The message that will be used in the meta object
    :return: The created
    """
    return MetaData(
        message=message,
        error_details=error_details,
        schemas=schemas
    )


def ok(data: Any) -> Response:
    """
    :param data: Data that will be used to populate the response body
    :return: Ok response
    """
    return response(200, ok_metadata(), data)


def created(data: Any) -> Response:
    """
    :param data: Data that will be used to populate the response body
    :return: Created response
    """
    return response(201, meta=ok_metadata(), data=data)


def bad(error_details: Sequence[ErrorDetail] = None,
        schema: Optional[Dict[str, Any]] = None) -> Response:
    """
    :param error_details: Details detailing why the request was bad. These details will be used
    in the response body.
    :param schema: Request body  that will be displayed in meta information of response
    :return: Bad request response
    """
    response_metadata = bad_metadata(error_details=error_details, schema=schema)
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
