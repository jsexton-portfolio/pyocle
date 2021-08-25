# 0.4.2

- Bumped dependency versions

# 0.4.1

- Fixed issue not allowing json messages to be published correctly using sns.

# 0.4.0

- Added accepted response method
- Added service package
    - Added Simple Notification Service
    - Added Simple Email Service
    - Key Management Service overhaul

# 0.3.2

- Fixed bug causing `PaginationDetails` to not ignore unexpected attributes

# 0.3.1

- Improved error logging
- Fixed bug that was causing `resolve_query_params` to return a dict instead of the resolved model object

# 0.3.0

- Fixed bug causing `None` to be returned when no default was provided for `encrypted_env_var`.
- Added pagination details to response metadata
- Removed error module
    - `error_handler` noe resides in response module
- Restructured `ErrorDetails`
    - Renamed `field_name` to `location`
    - Removed `FieldErrorDetails`

# 0.2.2

- Fixed bug in `encrypted_env_var()` function that was using the default value as the found environment variable.

# 0.2.1

- Fixed bug that caused library to fail when no attrs were passed to `encrypted_env_var()` function
- `connection_string()` function now accepts a default

# 0.2.0

- Added `env_var` methods
- Added decryption utils for environment variables
- Added dependencies to setup.py
- Added modules to `__init__`. Modules can now be used by simply importing pyocle.

# 0.1.0

- Created initial config module
- Created initial error module
- Created initial form module
- Created initial response module
- Created initial serialization module
- Created initial service module

