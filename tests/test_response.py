import pytest
from pydantic import BaseModel

from pyocle.response import *
from pyocle.response import _build_error_details


class DummyForm(BaseModel):
    first_name: str
    last_name: str


@pytest.fixture
def schemas():
    return {'requestBody': DummyForm.schema()}


class TestMetaDataBuilder:
    def test_ok(self):
        actual_meta = ok_metadata()
        expected_meta = MetaData(
            message='Request completed successfully'
        )

        assert actual_meta == expected_meta

    def test_bad(self, schemas):
        error_details = [
            ErrorDetail(description='description', location='some_field'),
            ErrorDetail(description='description', location='test_field')
        ]
        actual_meta = bad_metadata(error_details=error_details, schemas=schemas)
        expected_meta = MetaData(
            message='Given inputs were incorrect. Consult the below details to address the issue.',
            error_details=error_details,
            schemas=schemas
        )

        assert actual_meta == expected_meta

    def test_not_found(self):
        identifier = '123'
        actual_meta = not_found_metadata(identifier)
        expected_meta = MetaData(
            message='Resource with id 123 does not exist'
        )

        assert actual_meta == expected_meta

    def test_internal_error(self):
        actual_meta = internal_error_metadata()
        expected_meta = MetaData(
            message='Request failed due to internal server error'
        )

        assert actual_meta == expected_meta


class TestResponseBuilder:
    def test_ok(self):
        data = {'field_name': 'field_value'}
        res = ok(data)

        actual_body = jsonpickle.loads(res.body)
        expected_body = {
            'success': True,
            'meta': {
                'message': 'Request completed successfully',
                'errorDetails': [],
                'paginationDetails': {},
                'schemas': {}
            },
            'data': data
        }

        assert res.status_code == 200
        assert actual_body == expected_body
        assert res.headers == {}

    def test_ok_with_pagination(self):
        data = {'field_name': 'field_value'}
        pagination = PaginationQueryParameters(page=1, limit=50)
        res = ok(data, pagination)

        actual_body = jsonpickle.loads(res.body)
        expected_body = {
            'success': True,
            'meta': {
                'message': 'Request completed successfully',
                'errorDetails': [],
                'paginationDetails': pagination.dict(),
                'schemas': {}
            },
            'data': data
        }

        assert res.status_code == 200
        assert actual_body == expected_body
        assert res.headers == {}

    def test_created(self):
        data = {'field_name': 'field_value'}
        res = created(data)

        actual_body = jsonpickle.loads(res.body)
        expected_body = {
            'success': True,
            'meta': {
                'message': 'Request completed successfully',
                'errorDetails': [],
                'paginationDetails': {},
                'schemas': {}
            },
            'data': data
        }

        assert res.status_code == 201
        assert actual_body == expected_body
        assert res.headers == {}

    def test_bad(self):
        error_details = [
            ErrorDetail(description='description', location='some_field'),
            ErrorDetail(description='description', location='test_field')
        ]
        res = bad(error_details)

        actual_body = jsonpickle.loads(res.body)
        expected_body = {
            'success': False,
            'meta': {
                'message': 'Given inputs were incorrect. Consult the below details to address the issue.',
                'errorDetails': [
                    {
                        'description': 'description',
                        'location': 'some_field'
                    },
                    {
                        'description': 'description',
                        'location': 'test_field'
                    }
                ],
                'paginationDetails': {},
                'schemas': {}
            },
            'data': None
        }

        assert res.status_code == 400
        assert actual_body == expected_body
        assert res.headers == {}

    def test_not_found(self):
        identifier = '123'
        res = not_found(identifier)

        actual_body = jsonpickle.loads(res.body)
        expected_body = {
            'success': False,
            'meta': {
                'message': 'Resource with id 123 does not exist',
                'errorDetails': [],
                'paginationDetails': {},
                'schemas': {}
            },
            'data': None
        }

        assert res.status_code == 404
        assert actual_body == expected_body
        assert res.headers == {}

    def test_internal_error(self):
        res = internal_error()

        actual_body = jsonpickle.loads(res.body)
        expected_body = {
            'success': False,
            'meta': {
                'message': 'Request failed due to internal server error',
                'errorDetails': [],
                'paginationDetails': {},
                'schemas': {}
            },
            'data': None
        }

        assert res.status_code == 500
        assert actual_body == expected_body
        assert res.headers == {}


class TestErrorHandler:
    def test_ok_response(self):
        @error_handler
        def handler():
            return ok({'test_data': 5})

        handler_response = handler()
        assert not None
        assert isinstance(handler_response, Response)
        assert handler_response.status_code == 200

    def test_not_found_response(self):
        @error_handler
        def handler():
            raise ResourceNotFoundError('123')

        handler_response = handler()
        assert not None
        assert isinstance(handler_response, Response)
        assert handler_response.status_code == 404

    def test_internal_server_error_response(self):
        @error_handler
        def handler():
            raise Exception()

        handler_response = handler()
        assert not None
        assert isinstance(handler_response, Response)
        assert handler_response.status_code == 500

    def test_build_error_details(self):
        errors = [
            {'loc': ['person', 'name'], 'msg': 'message'},
        ]
        error_details = _build_error_details(errors)

        assert len(error_details) == 1
        assert isinstance(error_details[0], ErrorDetail)
        assert error_details[0].location == 'person.name'
        assert error_details[0].description == 'message'
