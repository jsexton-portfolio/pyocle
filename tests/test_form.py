import copy
from typing import Dict, Any

import jsonpickle
import pytest
from pydantic import BaseModel

from pyocle.error import FormValidationError
from pyocle.form import resolve_form


class DummyForm(BaseModel):
    first_name: str
    last_name: str


@pytest.fixture
def dummy_form() -> Dict[str, Any]:
    valid_form = {
        'first_name': 'first',
        'last_name': 'last'
    }

    return copy.deepcopy(valid_form)


@pytest.fixture
def valid_form_json(dummy_form) -> str:
    return jsonpickle.dumps(dummy_form, unpicklable=False)


@pytest.fixture
def valid_form_bytes(valid_form_json) -> bytes:
    return bytes(valid_form_json, 'utf-8')


def test_resolve_form_when_form_is_valid(dummy_form):
    resolved_dummy_form = resolve_form(dummy_form, DummyForm)
    assert resolved_dummy_form is not None


def test_resolve_form_returns_resolved_form__when_given_valid_string(valid_form_json):
    resolved_dummy_form = resolve_form(valid_form_json, DummyForm)
    assert resolved_dummy_form is not None


def test_resolve_form_returns_resolved_form_when_given_valid_bytes(valid_form_bytes):
    resolved_dummy_form = resolve_form(valid_form_bytes, DummyForm)
    assert resolved_dummy_form is not None


@pytest.mark.parametrize('data', [
    None,
    '',
    '{',
    '123'
])
def test_resolve_form_raises_form_validation_error_when_given_invalid_or_no_json(data):
    with pytest.raises(FormValidationError) as exception_info:
        resolve_form(data, DummyForm)

    exception = exception_info.value
    assert exception.message == 'Form could not be validated due to given json not existing or being valid'
    assert exception.schema is not None
    assert len(exception.error_details) == 1


def test_resolve_form_raises_value_error_when_given_unsupported_form_type():
    class InvalidForm(BaseModel):
        pass

    with pytest.raises(ValueError) as exception_info:
        resolve_form({}, InvalidForm)

    expected_message = 'Unsupported form type: InvalidForm. Type must be subclass of pydantic.BaseModel'
    assert expected_message in str(exception_info.value)
