from typing import Union, Dict, Any

import boto3
import jsonpickle

from pyocle.service.core import BaseForm


class MessageAttribute(BaseForm):
    """
    Form exposing a type safe API expressing what information
    is required when attaching a message attribute to a message
    """

    def __init__(self,
                 *,
                 data_type: str,
                 string_value: str = None,
                 binary_value: bytes = None):
        self.data_type = data_type
        self.string_value = string_value
        self.binary_value = binary_value

    def _dict(self):
        return {
            'DataType': self.data_type,
            'StringValue': self.string_value,
            'BinaryValue': self.binary_value
        }


class PublishMessageForm(BaseForm):
    """
    Form exposing a type safe API expressing what information
    is required when publish a message with AWS SNS.
    """

    def __init__(self,
                 *,
                 message: Union[str, Dict[str, Any]],
                 topic_arn: str = None,
                 target_arn: str = None,
                 phone_number: str = None,
                 subject: str = None,
                 message_structure: str = None,
                 message_attributes: Dict[str, MessageAttribute] = None):
        self.message = message
        self.topic_arn = topic_arn
        self.target_arn = target_arn
        self.phone_number = phone_number
        self.subject = subject
        self.message_structure = message_structure
        self.message_attributes = message_attributes or {}

        if phone_number is None and topic_arn is None and target_arn is None:
            raise ValueError('A phone number, topic or target must be specified')

    def _dict(self):
        message = self.message
        if isinstance(message, dict):
            message = jsonpickle.dumps({'default': message}, unpicklable=True)

        return {
            'Message': message,
            'Subject': self.subject,
            'TopicArn': self.topic_arn,
            'TargetArn': self.target_arn,
            'MessageStructure': self.message_structure,
            'MessageAttributes': {key: value.dict() for key, value in self.message_attributes.items()}
        }


class SimpleNotificationService:
    """
    Service used to interface with AWS SNS.
    """

    def __init__(self, client=None):
        """
        Constructs a new Simple Notification Service with a boto3 SNS client

        :param client: Client that will be used to interface with AWS SES.
                       It is unlikely that you will ever need to pass another client to this constructor.
        """
        self.client = client or boto3.client('sns')

    def publish(self, form: PublishMessageForm):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish

        :param form: Details that will be used to publish a message
        :return: Client response
        """
        return self.client.publish(**form.dict())
