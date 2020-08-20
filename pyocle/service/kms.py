import base64
from enum import Enum
from typing import Dict, Any, Union, List

import boto3

from pyocle.service.core import BaseForm


class EncryptionAlgorithm(Enum):
    """
    Algorithm that aws kms will be use to encrypt given plain text message
    """

    SYMMETRIC_DEFAULT = 'SYMMETRIC_DEFAULT'
    RSAES_OAEP_SHA_1 = 'RSAES_OAEP_SHA_1'
    RSAES_OAEP_SHA_256 = 'RSAES_OAEP_SHA_256'


class EncryptForm(BaseForm):
    """
    Form exposing a type safe API expressing what information
    is required when performing a encrypt operation with AWS KMS.

    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.encrypt
    """

    def __init__(self,
                 *,
                 key_id: str,
                 plain_text: Union[str, bytes],
                 encryption_context: Dict[str, str] = None,
                 grant_tokens: List[str] = None,
                 encryption_algorithm: EncryptionAlgorithm = None):
        self.key_id = key_id
        self.plain_text = plain_text
        self.encryption_context = encryption_context
        self.grant_tokens = grant_tokens
        self.encryption_algorithm = encryption_algorithm

    def _dict(self):
        return {
            'KeyId': self.key_id,
            'Plaintext': self.plain_text,
            'EncryptionContext': self.encryption_context,
            'GrantTokens': self.grant_tokens,
            'EncryptionAlgorithm': self.encryption_algorithm.value if self.encryption_algorithm else None
        }


class DecryptForm(BaseForm):
    """
    Form exposing a type safe API expressing what information
    is required when performing a decrypt operation with AWS KMS.

    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.decrypt
    """

    def __init__(self,
                 *,
                 cipher_text_blob: Union[str, bytes],
                 encryption_context: Dict[str, str] = None,
                 grant_tokens: List[str] = None,
                 key_id: str = None,
                 encryption_algorithm: EncryptionAlgorithm = None):
        self.cipher_text_blob = cipher_text_blob
        self.encryption_context = encryption_context
        self.grant_tokens = grant_tokens
        self.key_id = key_id
        self.encryption_algorithm = encryption_algorithm

    def _dict(self):
        blob = self.cipher_text_blob
        if isinstance(blob, str):
            blob = base64.b64decode(blob)
            KeyManagementService()

        return {
            'CiphertextBlob': blob,
            'EncryptionContext': self.encryption_context,
            'GrantTokens': self.grant_tokens,
            'KeyId': self.key_id,
            'EncryptionAlgorithm': self.encryption_algorithm.value if self.encryption_algorithm else None
        }


class KeyManagementService:
    """
    Service used to interface with AWS KMS.
    """

    def __init__(self, client=None):
        """
        Constructs a new Key Management Service with a boto3 kms client

        :param client: Client that will be used to interface with AWS KMS.
                        It is unlikely that you will ever need to pass another client to this constructor.
        """
        self.client = client or boto3.client('kms')

    def encrypt(self, form: EncryptForm) -> Dict[str, Any]:
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.encrypt

        :param form: Details that will be used to perform the encrypt operation
        :return: The client response
        """
        return self.client.encrypt(**form.dict())

    def decrypt(self, form: DecryptForm) -> Dict[str, Any]:
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.decrypt

        :param form: Details that will be used to perform the decrypt operation
        :return: The client response
        """
        return self.client.decrypt(**form.dict())
