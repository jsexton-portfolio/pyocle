from chalice import Response

from pyocle.error import error_handler, ResourceNotFoundError
from pyocle.response import ok


def test_ok_handler_response():
    @error_handler
    def handler():
        return ok({'test_data': 5})

    response = handler()
    assert not None
    assert isinstance(response, Response)
    assert response.status_code == 200


def test_not_found_handler_response():
    @error_handler
    def handler():
        raise ResourceNotFoundError('123')

    response = handler()
    assert not None
    assert isinstance(response, Response)
    assert response.status_code == 404


def test_internal_server_error_handler_response():
    @error_handler
    def handler():
        raise Exception()

    response = handler()
    assert not None
    assert isinstance(response, Response)
    assert response.status_code == 500
