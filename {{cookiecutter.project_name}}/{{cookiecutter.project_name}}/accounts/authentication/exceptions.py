class AuthenticationError(Exception):
    error_code = "authentication_error"


class NoSuchUserError(AuthenticationError):
    pass


class InvalidCredentials(AuthenticationError):
    pass


class DisabledAccountError(AuthenticationError):
    error_code = "account_disabled"
