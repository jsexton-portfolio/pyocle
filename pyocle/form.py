from typing import Sequence, Union, Dict, Any, Type, TypeVar, Optional

import jsonpickle
from pydantic import ValidationError, BaseModel, conint


class FormValidationError(Exception):
    """
    Error raised when an incoming request form is invalid
    """

    def __init__(self,
                 errors: Optional[Sequence[Dict[str, Any]]] = None,
                 message: str = None,
                 schemas: Dict[str, Any] = None):
        self.errors = errors or []
        self.message = message or 'Form was not validated successfully'
        self.schemas = schemas


class PaginationQueryParameters(BaseModel):
    """
    Model representing pagination query parameters. Model contains built in validation and can be resolved with
    the resolve_query_params resolver function.

    Ex.
    resolved_params = resolve_query_params(app.current_request.query_params, PaginationQueryParameters)
    """
    page: conint(ge=0) = 0
    limit: conint(ge=1, le=1000) = 100


# Form should inherit from pydantic's BaseModel
T = TypeVar('T', bound=BaseModel)


def resolve_form(data: Union[str, bytes, Dict[str, Any]], form_type: Type[T]) -> T:
    """
    Resolves a form from given type and json in the form of a dict. Validates form against given json
    and raises FormValidationError if form is invalid.

    :param data: The json that will be used to build the form. This data can be given in
     the form of string, bytes or dictionary.
    :param form_type: The form type to resolve
    :return: The resolved form
    """

    # All validation is built around pydantic. For extra guard rails, lets make sure the type given is a subclass of
    # pydantic's BaseModel otherwise it just doesnt make sense.
    if not issubclass(form_type, BaseModel):
        raise ValueError(f'Unsupported form type: {form_type.__name__}. Type must be subclass of pydantic.BaseModel')

    try:
        if isinstance(data, (str, bytes)):
            data = jsonpickle.loads(data)

        return form_type(**data)
    except ValidationError as ex:
        schema_name = _resolve_schema_name(form_type)
        raise FormValidationError(errors=ex.errors(), schemas={schema_name: form_type.schema()})
    except (TypeError, ValueError) as ex:
        # Will be raised by the jsonpickle.loads call when incoming str or bytes are not valid JSON.
        errors = [
            {
                'loc': ['requestBody'],
                'msg': 'Request body either either did not exist or was not valid JSON.'
            }
        ]
        schema_name = _resolve_schema_name(form_type)
        raise FormValidationError(
            message='Form could not be validated due to given json not existing or being valid',
            errors=errors,
            schemas={schema_name: form_type.schema()}
        ) from ex


def resolve_query_params(params: Optional[Dict[str, str]], model: Type[BaseModel]):
    """
    Very similar to resolve_form function except query parameters are optional.
    Only recognizable data is validated and returned in the response.

    :param params: The dictionary of query parameters that should be resolved to
    :param model: The model the query parameters should be mapped to
    :return: The resolved query parameter model
    """
    return {} if params is None else resolve_form(params, model).dict(exclude_unset=True)


def _resolve_schema_name(model: Type[BaseModel]) -> str:
    """
    Hacky function to determine a schema name based on the model type. This should be updated to something more
    robust in the future.

    :param model: The model that will be used to determine the schema name
    :return: The schema name
    """
    model_name = model.__name__
    if model_name.endswith('QueryParameters'):
        return 'queryParameters'

    return 'requestBody'
