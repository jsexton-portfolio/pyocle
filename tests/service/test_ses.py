import boto3
import pytest

from pyocle.service.ses import EmailForm, TemplatedEmailForm, BaseEmailForm, SimpleEmailService, EmailTag
from tests.service.test_core import FormTestFixture


@pytest.fixture
def email_tag() -> FormTestFixture:
    return FormTestFixture(
        value=EmailTag(name='name', value='value'),
        dict={
            'Name': 'name',
            'Value': 'value'
        })


@pytest.fixture
def base_email_form(email_tag: FormTestFixture) -> FormTestFixture:
    return FormTestFixture(
        value=BaseEmailForm(
            source='source',
            to_addresses=['to', 'addresses'],
            cc_addresses=['cc', 'addresses'],
            bcc_addresses=['bcc', 'addresses'],
            reply_to_addresses=['reply', 'to', 'addresses'],
            source_arn='source arn',
            return_path='return path',
            return_path_arn='return path arn',
            tags=[
                email_tag.value
            ],
            configuration_set='configuration set'
        ),
        dict={
            'Source': 'source',
            'Destination': {
                'ToAddresses': ['to', 'addresses'],
                'CcAddresses': ['cc', 'addresses'],
                'BccAddresses': ['bcc', 'addresses']
            },
            'ReplyToAddresses': ['reply', 'to', 'addresses'],
            'ReturnPath': 'return path',
            'SourceArn': 'source arn',
            'ReturnPathArn': 'return path arn',
            'Tags': [
                {
                    'Name': 'name',
                    'Value': 'value'
                }
            ],
            'ConfigurationSetName': 'configuration set'
        }
    )


@pytest.fixture
def email_form(base_email_form: FormTestFixture) -> FormTestFixture:
    return FormTestFixture(
        value=EmailForm(
            subject='subject',
            text='text',
            html='html',
            **base_email_form.value.__dict__
        ),
        dict={
            'Source': 'source',
            'Destination': {
                'ToAddresses': ['to', 'addresses'],
                'CcAddresses': ['cc', 'addresses'],
                'BccAddresses': ['bcc', 'addresses']
            },
            'ReplyToAddresses': ['reply', 'to', 'addresses'],
            'ReturnPath': 'return path',
            'SourceArn': 'source arn',
            'ReturnPathArn': 'return path arn',
            'Tags': [
                {
                    'Name': 'name',
                    'Value': 'value'
                }
            ],
            'ConfigurationSetName': 'configuration set',
            'Message': {
                'Subject': {
                    'Data': 'subject',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': 'text',
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': 'html',
                        'Charset': 'UTF-8'
                    }
                }
            }
        }
    )


@pytest.fixture
def templated_email_form(base_email_form: FormTestFixture) -> FormTestFixture:
    return FormTestFixture(
        value=TemplatedEmailForm(
            template='template',
            template_data={
                'template': 'data'
            },
            **base_email_form.value.__dict__
        ),
        dict={
            'Source': 'source',
            'Destination': {
                'ToAddresses': ['to', 'addresses'],
                'CcAddresses': ['cc', 'addresses'],
                'BccAddresses': ['bcc', 'addresses']
            },
            'ReplyToAddresses': ['reply', 'to', 'addresses'],
            'ReturnPath': 'return path',
            'SourceArn': 'source arn',
            'ReturnPathArn': 'return path arn',
            'Tags': [
                {
                    'Name': 'name',
                    'Value': 'value'
                }
            ],
            'ConfigurationSetName': 'configuration set',
            'Template': 'template',
            'TemplateData': '{"template": "data"}'
        }
    )


def test_email_tag_is_correctly_converted_to_dict(email_tag: FormTestFixture):
    actual_dict = email_tag.value.dict()
    expected_dict = email_tag.dict
    assert actual_dict == expected_dict


def test_email_form_raises_value_error_when_text_or_html_is_not_provided():
    with pytest.raises(ValueError) as ex_info:
        EmailForm(
            source='source',
            to_addresses=['to', 'addresses'],
            subject='subject',
        )

    error = ex_info.value
    assert str(error) == 'Html or text content must be specified'


def test_base_email_form_is_correctly_converted_to_dict(base_email_form: FormTestFixture):
    actual_dict = base_email_form.value.dict()
    expected_dict = base_email_form.dict
    assert actual_dict == expected_dict


def test_email_form_is_correctly_converted_to_dict(email_form: FormTestFixture):
    actual_dict = email_form.value.dict()
    expected_dict = email_form.dict
    assert actual_dict == expected_dict


def test_templated_email_form_is_correctly_converted_to_dict(templated_email_form: FormTestFixture):
    actual_dict = templated_email_form.value.dict()
    expected_dict = templated_email_form.dict
    assert actual_dict == expected_dict


def test_templated_email_form_is_correctly_converted_to_dict_with_string_template_data(
        templated_email_form: FormTestFixture):
    templated_email_form.value.template_data = '{"template": "data"}'
    actual_dict = templated_email_form.value.dict()
    expected_dict = templated_email_form.dict
    assert actual_dict == expected_dict


def test_simple_email_service_invokes_client_send_email_operation_correctly(
        mocker,
        email_form: FormTestFixture):
    mock_client = mocker.patch.object(boto3.client('ses'), 'send_email')
    kms = SimpleEmailService(mock_client)
    kms.send_email(email_form.value)

    mock_client.send_email.assert_called_once()
    mock_client.send_email.assert_called_with(**email_form.dict)


def test_simple_email_service_invokes_client_send_templated_email_operation_correctly(
        mocker,
        templated_email_form: FormTestFixture):
    mock_client = mocker.patch.object(boto3.client('ses'), 'send_templated_email')
    kms = SimpleEmailService(mock_client)
    kms.send_templated_email(templated_email_form.value)

    mock_client.send_templated_email.assert_called_once()
    mock_client.send_templated_email.assert_called_with(**templated_email_form.dict)
