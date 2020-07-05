from typing import Sequence, Union, Dict, Any, Type, TypeVar

import jsonpickle
from pydantic import ValidationError, BaseModel

from pyocle.error import FormValidationError
from pyocle.response import ErrorDetail, FieldErrorDetail

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
        error_details = _build_error_details(ex.errors())
        raise FormValidationError(error_details=error_details, schema=form_type.schema())
    except (TypeError, ValueError) as ex:
        error_details = [ErrorDetail(description='Request body either either did not exist or was not valid JSON.')]
        raise FormValidationError(
            message='Form could not be validated due to given json not existing or being valid',
            error_details=error_details,
            schema=form_type.schema()
        ) from ex


def _build_error_details(errors) -> Sequence[FieldErrorDetail]:
    """
    Creates list of field error details from given pydantic errors

    :param errors: List of pydantic errors
    :return: List of field error details built from given pydantic errors
    """
    return [FieldErrorDetail(field_name='.'.join(error['loc']), description=error['msg']) for error in errors]
