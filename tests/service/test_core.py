from collections import namedtuple
from typing import Dict

import pytest

from pyocle.service.core import BaseForm

FormTestFixture = namedtuple(typename='FormTestFixture', field_names='value,dict')


class DummyBaseForm(BaseForm):
    def __init__(self, name: str = None, items: Dict[str, str] = None):
        self.name = name
        self.items = items

    def _dict(self):
        return {
            'name': self.name,
            'items': self.items
        }


@pytest.fixture
def dummy_form() -> FormTestFixture:
    return FormTestFixture(
        value=DummyBaseForm(name='test', items={'test': 'test'}),
        dict={
            'name': 'test',
            'items': {
                'test': 'test'
            }
        }
    )


def test_base_form_correctly_resolves_null_values():
    actual_form = DummyBaseForm().dict()
    expected_form = {}
    assert actual_form == expected_form


def test_base_form_correctly_resolves_dict(dummy_form: FormTestFixture):
    actual_form = dummy_form.value.dict()
    expected_form = dummy_form.dict
    assert actual_form == expected_form
