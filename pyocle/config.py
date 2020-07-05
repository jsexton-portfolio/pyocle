import os
from typing import Optional

from pyocle.service import KeyManagementService


def connection_string() -> Optional[str]:
    """
    Retrieves the environment's connection string cipher text and decrypts with Key Management Service to
    connection string plain text

    :return: Environment connection string plain text.
    """
    connection_string_cipher_text = os.getenv('CONNECTION_STRING')

    if connection_string_cipher_text is None:
        return None

    key_management_service = KeyManagementService()
    response = key_management_service.decrypt(connection_string_cipher_text)

    # plaintext comes back in the form of bytes. Need to decode to utf-8
    return response['Plaintext'].decode('utf-8')
