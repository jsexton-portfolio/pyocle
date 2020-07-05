# Pyocle
![](https://github.com/jsexton-portfolio/pyocle/workflows/build/badge.svg)

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
from pyocle import response

ok_response = response.ok({'some': 'data'})
created_response = response.created({'some': 'data'})

# In most cases, the error handler will handle these responses for you if you defined
# the pydantic models correctly and you are using form.resolve_form for all incoming data.
bad_response = response.bad(error_details=[], schema={})

internal_error_response = response.internal_error()
```

## Error Handling
Pyocle comes with an `error_handler` decorator that can be used to decorate all endpoints that require 
error handling.

```python
from chalice import Chalice
from pyocle.error import error_handler

app = Chalice(app_name='my-portfolio-service')

app.route('/')
@error_handler
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
from pyocle.error import error_handler
from pyocle.form import resolve_form

app = Chalice(app_name='my-portfolio-service')

class SomeForm(BaseModel):
    test_data: str

app.route('/')
@error_handler
def some_portfolio_endpoint():
    incoming_data = app.current_request.raw_body
    form = resolve_form(incoming_data, SomeForm)
    
    ...
```

## Common Services
Pyocle comes with a few common services used through out portfolio services out of the box.

### Key Management Service
The `KeyManagementService` is used to interface with AWS KMS for encrypting and decrypting information. Most common
use case is decrypting connection strings for databases.
```python
from pyocle import service

kms = service.KeyManagementService()
kms_response = kms.decrypt('some cipher text')
```

