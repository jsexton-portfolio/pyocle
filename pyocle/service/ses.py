from typing import List, Dict, Union, Any

import boto3
import jsonpickle

from pyocle.service.core import BaseForm


class EmailTag:
    """
    Form exposing a type safe API expressing what information
    is required when attaching an email tag to an email
    """

    def __init__(self, *, name: str, value: str):
        self.name = name
        self.value = value

    def dict(self) -> Dict[str, str]:
        return {
            'Name': self.name,
            'Value': self.value
        }


class BaseEmailForm(BaseForm):
    """
    Form used to represent an email sent from AWS SES.
    Contains base properties that all sent emails could possibly contain.
    """

    def __init__(self,
                 *,
                 source: str,
                 to_addresses: List[str],
                 cc_addresses: List[str] = None,
                 bcc_addresses: List[str] = None,
                 reply_to_addresses: List[str] = None,
                 source_arn: str = None,
                 return_path: str = None,
                 return_path_arn: str = None,
                 tags: List[EmailTag] = None,
                 configuration_set: str = None):
        self.source = source
        self.to_addresses = to_addresses
        self.cc_addresses = cc_addresses or []
        self.bcc_addresses = bcc_addresses or []
        self.reply_to_addresses = reply_to_addresses or []
        self.source_arn = source_arn
        self.return_path = return_path
        self.return_path_arn = return_path_arn
        self.tags = tags or []
        self.configuration_set = configuration_set

    def _dict(self):
        tags = [tag.dict() for tag in self.tags]

        return {
            'Source': self.source,
            'Destination': {
                'ToAddresses': self.to_addresses,
                'CcAddresses': self.cc_addresses,
                'BccAddresses': self.bcc_addresses
            },
            'ReplyToAddresses': self.reply_to_addresses,
            'ReturnPath': self.return_path,
            'SourceArn': self.source_arn,
            'ReturnPathArn': self.return_path_arn,
            'Tags': tags,
            'ConfigurationSetName': self.configuration_set
        }


class EmailForm(BaseEmailForm):
    """
    Form exposing a type safe API expressing what information
    is required when sending an email with AWS SES
    """

    def __init__(self,
                 *,
                 subject: str,
                 subject_charset='UTF-8',
                 text: str = None,
                 text_charset: str = 'UTF-8',
                 html: str = None,
                 html_charset: str = 'UTF-8',
                 **kwargs):
        super().__init__(**kwargs)
        self.subject = subject
        self.subject_charset = subject_charset
        self.text = text
        self.text_charset = text_charset
        self.html = html
        self.html_charset = html_charset

        if html is None and text is None:
            raise ValueError('html or text attribute must be populated')

    def _dict(self):
        return {
            **super()._dict(),
            'Message': {
                'Subject': {
                    'Data': self.subject,
                    'Charset': self.subject_charset
                },
                'Body': {
                    'Text' if self.text is not None else None: {
                        'Data': self.text,
                        'Charset': self.text_charset
                    },
                    'Html' if self.html is not None else None: {
                        'Data': self.html,
                        'Charset': self.html_charset
                    }
                }
            }
        }


class TemplatedEmailForm(BaseEmailForm):
    """
    Form exposing a type safe API expressing what information
    is required when sending a templated email AWS SES.
    """

    def __init__(self,
                 *,
                 template: str,
                 template_data: Union[Dict[str, Any], str],
                 **kwargs):
        super().__init__(**kwargs)
        self.template = template
        self.template_data = template_data

    def _dict(self):
        # Make sure data is in string json format, if not, serialize it
        data = self.template_data
        if isinstance(data, dict):
            data = jsonpickle.dumps(data, unpicklable=True)

        return {
            **super()._dict(),
            'Template': self.template,
            'TemplateData': data
        }


class SimpleEmailService:
    """
    Service used to interface with AWS SES.
    """

    def __init__(self, client=None):
        """
        Constructs a new Simple Email Service with a boto3 SES client

        :param client: Client that will be used to interface with AWS SES.
                       It is unlikely that you will ever need to pass another client to this constructor.
        """
        self.client = client or boto3.client('ses')

    def send_email(self, form: EmailForm):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.send_email

        :param form: Details that will be used to send an email
        :return: Client response
        """
        return self.client.send_email(**form.dict())

    def send_templated_email(self, form: TemplatedEmailForm):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.send_templated_email

        :param form: Details that will be used to send a templated email
        :return: Client response
        """
        return self.client.send_templated_email(**form.dict())
