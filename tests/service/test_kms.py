import base64

import boto3
import pytest

from pyocle.service.kms import EncryptForm, EncryptionAlgorithm, DecryptForm, KeyManagementService
from tests.service.test_core import FormTestFixture


@pytest.fixture
def encrypt_form() -> FormTestFixture:
    return FormTestFixture(
        value=EncryptForm(
            key_id='key id',
            plain_text='plain',
            encryption_context={
                'test': 'context'
            },
            grant_tokens=['grant', 'tokens'],
            encryption_algorithm=EncryptionAlgorithm.RSAES_OAEP_SHA_1
        ),
        dict={
            'KeyId': 'key id',
            'Plaintext': 'plain',
            'EncryptionContext': {
                'test': 'context'
            },
            'GrantTokens': ['grant', 'tokens'],
            'EncryptionAlgorithm': 'RSAES_OAEP_SHA_1'
        }
    )


@pytest.fixture
def decrypt_form() -> FormTestFixture:
    return FormTestFixture(
        value=DecryptForm(
            cipher_text_blob='test',
            encryption_context={
                'test': 'context'
            },
            grant_tokens=['grant', 'tokens'],
            key_id='key id',
            encryption_algorithm=EncryptionAlgorithm.RSAES_OAEP_SHA_1
        ),
        dict={
            'CiphertextBlob': base64.b64decode('test'),
            'EncryptionContext': {
                'test': 'context'
            },
            'GrantTokens': ['grant', 'tokens'],
            'KeyId': 'key id',
            'EncryptionAlgorithm': 'RSAES_OAEP_SHA_1'
        }
    )


def test_encrypt_form_is_correctly_converted_to_dict(encrypt_form: FormTestFixture):
    actual_dict = encrypt_form.value.dict()
    expected_dict = encrypt_form.dict
    assert actual_dict == expected_dict


def test_decrypt_form_is_correctly_converted_to_dict(decrypt_form: FormTestFixture):
    actual_dict = decrypt_form.value.dict()
    expected_dict = decrypt_form.dict
    assert actual_dict == expected_dict


def test_decrypt_form_is_correctly_converted_to_dict_with_bytes_cipher_text(decrypt_form: FormTestFixture):
    blob = base64.b64decode('test')
    decrypt_form.value.cipher_text_blob = blob
    actual_dict = decrypt_form.value.dict()
    expected_dict = decrypt_form.dict
    expected_dict['CiphertextBlob'] = blob
    assert actual_dict == expected_dict


def test_key_management_service_invokes_client_encrypt_operation_correctly(mocker, encrypt_form: FormTestFixture):
    mock_client = mocker.patch.object(boto3.client('kms'), 'encrypt')
    kms = KeyManagementService(mock_client)
    kms.encrypt(encrypt_form.value)

    mock_client.encrypt.assert_called_once()
    mock_client.encrypt.assert_called_with(**encrypt_form.dict)


def test_key_management_service_invokes_client_decrypt_operation_correctly(mocker, decrypt_form: FormTestFixture):
    mock_client = mocker.patch.object(boto3.client('kms'), 'decrypt')
    kms = KeyManagementService(mock_client)
    kms.decrypt(decrypt_form.value)

    mock_client.decrypt.assert_called_once()
    mock_client.decrypt.assert_called_with(**decrypt_form.dict)
