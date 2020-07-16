import copy
from typing import Dict, Any, Optional, Type

import jsonpickle
import pytest
from pydantic import BaseModel, ValidationError

from pyocle.form import resolve_form, PaginationQueryParameters, FormValidationError, resolve_query_params


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


class DummyForm(BaseModel):
    first_name: str
    last_name: str


class TestResolveForm:
    def test_when_form_is_valid(self, dummy_form):
        resolved_dummy_form = resolve_form(dummy_form, DummyForm)
        assert resolved_dummy_form is not None

    def test_returns_resolved_form__when_given_valid_string(self, valid_form_json):
        resolved_dummy_form = resolve_form(valid_form_json, DummyForm)
        assert resolved_dummy_form is not None

    def test_returns_resolved_form_when_given_valid_bytes(self, valid_form_bytes):
        resolved_dummy_form = resolve_form(valid_form_bytes, DummyForm)
        assert resolved_dummy_form is not None

    @pytest.mark.parametrize('data', [
        None,
        '',
        '{',
        '123'
    ])
    def test_raises_form_validation_error_when_given_invalid_or_no_json(self, data):
        with pytest.raises(FormValidationError) as exception_info:
            resolve_form(data, DummyForm)

        exception = exception_info.value
        assert exception.message == 'Form could not be validated due to given json not existing or being valid'
        assert exception.schemas is not None
        assert len(exception.errors) == 1

    def test_raises_value_error_when_given_unsupported_form_type(self):
        class InvalidForm:
            pass

        with pytest.raises(ValueError) as exception_info:
            resolve_form({}, InvalidForm)

        expected_message = 'Unsupported form type: InvalidForm. Type must be subclass of pydantic.BaseModel'
        assert expected_message in str(exception_info.value)


class TestPaginationQueryParameters:
    @pytest.mark.parametrize('page,limit', [
        (0, 10),
        (1, 999),
        (0, 1000),
        (500, 1000)
    ])
    def test_does_not_raise_validation_error_given_valid_values(self, page: int, limit: int):
        PaginationQueryParameters(page=page, limit=limit)

    @pytest.mark.parametrize('page,limit', [
        (-1, 10),
        (0, 1001),
        (-1, 1001),
        ('a', 10),
        (0, 'a'),
        ('a', {}),

    ])
    def test_raises_validation_error_given_invalid_values(self, page: int, limit: int):
        with pytest.raises(ValidationError):
            PaginationQueryParameters(page=page, limit=limit)


@pytest.mark.parametrize('query_params,expected,model', [
    (None,
     PaginationQueryParameters(),
     PaginationQueryParameters),
    ({
         'page': 1,
         'limit': 100
     },
     PaginationQueryParameters(page=1, limit=100),
     PaginationQueryParameters),
    ({
         'page': 5,
         'limit': 500,
         'extra': 'should be ignored'
     },
     PaginationQueryParameters(page=5, limit=500),
     PaginationQueryParameters)
])
def test_resolve_query_params(query_params: Optional[Dict[str, Any]],
                              expected: PaginationQueryParameters,
                              model: Type[BaseModel]):
    resolved_query_params = resolve_query_params(query_params, model)
    assert resolved_query_params == expected
