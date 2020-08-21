import boto3
import pytest

from pyocle.service.sns import MessageAttribute, PublishMessageForm, SimpleNotificationService
from tests.service.test_core import FormTestFixture


@pytest.fixture
def message_attribute() -> FormTestFixture:
    return FormTestFixture(
        value=MessageAttribute(
            data_type='data type',
            string_value='string value',
            binary_value=b'binary value'
        ),
        dict={
            'DataType': 'data type',
            'StringValue': 'string value',
            'BinaryValue': b'binary value'
        }
    )


@pytest.fixture
def publish_message(message_attribute: FormTestFixture) -> FormTestFixture:
    return FormTestFixture(
        value=PublishMessageForm(
            message='message',
            topic_arn='topic arn',
            target_arn='target arn',
            phone_number='phone number',
            subject='subject',
            message_structure='message structure',
            message_attributes={
                'key': message_attribute.value
            }
        ),
        dict={
            'Message': 'message',
            'Subject': 'subject',
            'TopicArn': 'topic arn',
            'TargetArn': 'target arn',
            'MessageStructure': 'message structure',
            'MessageAttributes': {
                'key': message_attribute.dict
            }
        }
    )


def test_message_attribute_is_correctly_converted_to_dict(message_attribute: FormTestFixture):
    actual_dict = message_attribute.value.dict()
    expected_dict = message_attribute.dict
    assert actual_dict == expected_dict


def test_publish_message_form_is_correctly_converted_to_dict(publish_message: FormTestFixture):
    actual_dict = publish_message.value.dict()
    expected_dict = publish_message.dict
    assert actual_dict == expected_dict


def test_publish_message_form_is_correctly_converted_to_dict_with_dict_message(publish_message: FormTestFixture):
    publish_message.value.message = {
        'key': 'value'
    }
    actual_dict = publish_message.value.dict()
    expected_dict = publish_message.dict
    expected_dict.update({
        'Message': '{"default": {"key": "value"}}'
    })
    assert actual_dict == expected_dict


def test_publish_message_form_raises_value_error_when_phone_target_or_topic_is_not_provided():
    with pytest.raises(ValueError) as ex_info:
        PublishMessageForm(
            message='message'
        )

    error = ex_info.value
    assert str(error) == 'A phone number, topic or target must be specified'


def test_simple_notification_service_invokes_publish_operation_correctly(
        mocker,
        publish_message: FormTestFixture):
    mock_client = mocker.patch.object(boto3.client('sns'), 'publish')
    sns = SimpleNotificationService(mock_client)
    sns.publish(publish_message.value)

    mock_client.publish.assert_called_once()
    mock_client.publish.assert_called_with(**publish_message.dict)
