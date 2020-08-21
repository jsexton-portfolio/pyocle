# Pyocle
![](https://github.com/jsexton-portfolio/pyocle/workflows/build/badge.svg)

> Socle - A plain low block or plinth serving as a support for a column, urn, statue, etc. or as the foundation of a wall.

Common library used alongside jsexton-portfolio chalice applications.

## Responses

Portfolio APIs have a standard response structure they must follow. This library contains models and response builders
to help remain consistent with these defined standards response models.

### Models
#### Response Body
```json
{
  "success": true,
  "meta": { },
  "data": { }
}
```
#### Response Meta Field
```json
{
  "message": "Message depending on the type of response",
  "errorDetails": [],
  "schemas": {}
}
```

### Building Responses
```python
import pyocle

ok_response = pyocle.response.ok({'some': 'data'})
created_response = pyocle.response.created({'some': 'data'})

# In most cases, the error handler will handle these responses for you if you defined
# the pydantic models correctly and you are using form.resolve_form for all incoming data.
bad_response = pyocle.response.bad(error_details=[], schemas={})

internal_error_response = pyocle.response.internal_error()
```

### Serialization Helpers
#### Camel Case Property Naming Convention
It is a portfolio API standard that all field names should be camel case when serialized to the response body. Pyocle
offers a mixin to assist in this conversion.
```python
from pyocle.serialization import CamelCaseAttributesMixin

class MyResponse(CamelCaseAttributesMixin):
    def __init__(self):
        self.snake_case_attribute = 'snake_case_attribute'
```
When using jsonpickle or any built in pyocle response builders, the resulting json will contain camel cased attrbiute names.

## Error Handling
Pyocle comes with an `error_handler` decorator that can be used to decorate all endpoints that require 
error handling.

```python
from chalice import Chalice
import pyocle

app = Chalice(app_name='my-portfolio-service')

@app.route('/')
@pyocle.response.error_handler
def some_portfolio_endpoint():
    pass
```

## Resolving Forms
When resolving forms or incoming data with pyocle, use the `resolve_form` function. The function accepts the incoming
data and a form object that inherits from pydantic's BaseModel to match against. 
If the incoming data complies with the specified form, the form object is returned. Make sure the form is a subclass of BaseModel,
if not, an exception will be raised.
Otherwise an exception is raised with information detailing what went wrong. These exceptions normally work
very closely with pyocle's error_handler.

```python
from chalice import Chalice
from pydantic import BaseModel
import pyocle

app = Chalice(app_name='my-portfolio-service')

class SomeForm(BaseModel):
    test_data: str

@app.route('/')
@pyocle.response.error_handler
def some_portfolio_endpoint():
    incoming_data = app.current_request.raw_body
    form = pyocle.form.resolve_form(incoming_data, SomeForm)
    
    ...
```

## Common Services
Pyocle comes with a few common services used through out portfolio services out of the box.

### Key Management Service
The `KeyManagementService` is used to interface with AWS KMS for encrypting and decrypting information. Most common
use case is decrypting connection strings for databases.

#### Encrypt
```python
from pyocle.service.kms import KeyManagementService, EncryptForm

kms = KeyManagementService()
form = EncryptForm(
    key_id='key id',
    plain_text='some cipher text'
)
kms_response = kms.encrypt(form)
```

#### Decrypt
```python
from pyocle.service.kms import KeyManagementService, DecryptForm

kms = KeyManagementService()
form = DecryptForm(
    cipher_text_blob='some cipher text'
)
kms_response = kms.decrypt(form)
```

### Simple Email Service
The `SimpleEmailService` is used to interface with AWS SES allowing consumers to send emails.
```python
from pyocle.service.ses import SimpleEmailService, EmailForm

ses = SimpleEmailService()
form = EmailForm(
    source='the source of the email',
    to_addresses=['some', 'email', 'addresses'],
    subject='some subject line',
    text='some email message'
)
ses.send_email(form)
```

### Simple Notification Service
The `SimpleNotificationService` is used to interface with AWS SNS allowing messages to be published to
various topics.

```python
from pyocle.service.sns import SimpleNotificationService, PublishMessageForm

sns = SimpleNotificationService()
form = PublishMessageForm(
    message='some message, can also be a dictionary and will be converted to json',
    topic_arn='topic arn'
)
sns.publish(form)
```

## Configuration
### Environment Variables
In order to safely retrieve an environment variable, make use of the `env_var()` function.
A default value can be given and will be used if the given environment variable could not be found.

```python
import pyocle

environment_variable = pyocle.config.env_var('some_env_var_name', default='found')
```

### Encrypted Environment Variables
Sometimes environment variables are encrypted. Use the `encrypted_env_var()` function to retrieve these
values in their plain text forms. 

```python
import pyocle

decrypted_environment_variable = pyocle.config.encrypted_env_var('some_env_var_name')
```

By default the function makes use of a `kms decrypter`. To specify a custom decrypter simply pass the
decryption function as a `decrypter` and any additional values that may be need to decrypt to `attrs`

```python
import pyocle

additional_info = {
    'password': 'password123'
}

def my_decrypter(value, **kwargs) -> str:
    """decrypt and return"""
    
decrypted_environment_variable = pyocle.config.encrypted_env_var('some_env_var_name', decrypter=my_decrypter, attrs=additional_info)
```

### Connection Strings
Connection strings should be encrypted with KMS and stored in the correct chalice stage environment variables as 'CONNECTION_STING'.
When retrieving these values, make use of the `connection_string()` function. `connection_string()` will retrieve the environment
connection string and decrypt using KMS while only returning the actual usable connection string.
```python
import pyocle

connection_string = pyocle.config.connection_string()
```
