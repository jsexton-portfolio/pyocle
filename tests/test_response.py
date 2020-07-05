import pytest
from pydantic import BaseModel

from pyocle.response import *


class DummyForm(BaseModel):
    first_name: str
    last_name: str


@pytest.fixture
def schema():
    return DummyForm.schema()


def test_ok_meta():
    actual_meta = ok_metadata()
    expected_meta = MetaData(
        message='Request completed successfully'
    )

    assert actual_meta == expected_meta


def test_bad_message(schema):
    error_details = [
        ErrorDetail(description='description'),
        FieldErrorDetail(description='description', field_name='test_field')
    ]
    actual_meta = bad_metadata(error_details=error_details, schema=schema)
    expected_meta = MetaData(
        message='Given inputs were incorrect. Consult the below details to address the issue.',
        error_details=error_details,
        schemas={'requestBody': schema}
    )

    assert actual_meta == expected_meta


def test_not_found_message():
    identifier = '123'
    actual_meta = not_found_metadata(identifier)
    expected_meta = MetaData(
        message='Resource with id 123 does not exist'
    )

    assert actual_meta == expected_meta


def test_internal_error_message():
    actual_meta = internal_error_metadata()
    expected_meta = MetaData(
        message='Request failed due to internal server error'
    )

    assert actual_meta == expected_meta


def test_ok_response():
    data = {'field_name': 'field_value'}
    res = ok(data)

    actual_body = jsonpickle.loads(res.body)
    expected_body = {
        'success': True,
        'meta': {
            'message': 'Request completed successfully',
            'errorDetails': [],
            'schemas': {}
        },
        'data': data
    }

    assert res.status_code == 200
    assert actual_body == expected_body
    assert res.headers == {}


def test_created_response():
    data = {'field_name': 'field_value'}
    res = created(data)

    actual_body = jsonpickle.loads(res.body)
    expected_body = {
        'success': True,
        'meta': {
            'message': 'Request completed successfully',
            'errorDetails': [],
            'schemas': {}
        },
        'data': data
    }

    assert res.status_code == 201
    assert actual_body == expected_body
    assert res.headers == {}


def test_bad_response():
    error_details = [
        ErrorDetail(description='description'),
        FieldErrorDetail(description='description', field_name='test_field')
    ]
    res = bad(error_details)

    actual_body = jsonpickle.loads(res.body)
    expected_body = {
        'success': False,
        'meta': {
            'message': 'Given inputs were incorrect. Consult the below details to address the issue.',
            'errorDetails': [
                {
                    'description': 'description'
                },
                {
                    'description': 'description',
                    'fieldName': 'test_field'
                }
            ],
            'schemas': {

            }
        },
        'data': None
    }

    assert res.status_code == 400
    assert actual_body == expected_body
    assert res.headers == {}


def test_not_found_response():
    identifier = '123'
    res = not_found(identifier)

    actual_body = jsonpickle.loads(res.body)
    expected_body = {
        'success': False,
        'meta': {
            'message': 'Resource with id 123 does not exist',
            'errorDetails': [],
            'schemas': {}
        },
        'data': None
    }

    assert res.status_code == 404
    assert actual_body == expected_body
    assert res.headers == {}


def test_internal_error_response():
    res = internal_error()

    actual_body = jsonpickle.loads(res.body)
    expected_body = {
        'success': False,
        'meta': {
            'message': 'Request failed due to internal server error',
            'errorDetails': [],
            'schemas': {}
        },
        'data': None
    }

    assert res.status_code == 500
    assert actual_body == expected_body
    assert res.headers == {}
