import base64
from typing import Dict, Any

import boto3


class KeyManagementService:
    """
    Service used to interface with aws kms (Key Management Service)

    WARNING: Currently does not gracefully handle when a key identifier is unauthorized for use.
    """

    def __init__(self, client=None):
        if client is None:
            client = boto3.client('kms')

        self.client = client

    def encrypt(self, plaintext: str, key_id: str) -> Dict[str, Any]:
        """
        Encrypts given plaintext with specified key identifier.

        :param plaintext: The plaintext to encrypt
        :param key_id: The key identifier to use when encrypting the given plaintext
        :return: The kms encryption response
        """

        encryption_response = self.client.encrypt(KeyId=key_id, Plaintext=plaintext)
        return encryption_response

    def decrypt(self, ciphertext: str) -> Dict[str, Any]:
        """
        Decrypts given ciphertext

        :param ciphertext: The ciphertext to decrypt
        :return: The kms decrypting response
        """

        base64_decoded_connection_string_cipher_text = base64.b64decode(ciphertext)
        decryption_response = self.client.decrypt(CiphertextBlob=base64_decoded_connection_string_cipher_text)
        return decryption_response
