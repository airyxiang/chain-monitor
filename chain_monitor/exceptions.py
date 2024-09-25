class BaseException(Exception):

    def __init__(self, message=None, code=None, data=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data

    def __str__(self):
        components = []
        if self.message:
            components.append(self.message)
        if self.code:
            components.append('[code={}]'.format(self.code))
        if self.data:
            components.append('[data={}]'.format(self.data))

        output = ' '.join(components)
        return output


class FieldError:
    def __init__(self, field, message=None, code=None):
        self.field = field
        self.message = message
        self.code = code


class FieldErrorsMixin:
    """
    Mixin to add field_errors property to an exception class
    """

    def __init__(self, *args, field_errors=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_errors = field_errors or []


class FieldErrorsException(FieldErrorsMixin, BaseException):
    pass


class APIRequestError(BaseException):
    pass


class BadRequestError(FieldErrorsMixin, APIRequestError):
    pass


class UnauthenticatedError(APIRequestError):
    pass


class UnauthorizedError(APIRequestError):
    pass


class NotFoundError(APIRequestError):
    pass


class ServerError(APIRequestError):
    pass
