from django.http import HttpResponse


class DeliciousCakeError(Exception):
    """A base exception for all delicious-cake related errors."""
    pass


class UnsupportedFormat(DeliciousCakeError):
    """
    Raised when an unsupported serialization format is requested.
    """
    pass


class UnsupportedSerializationFormat(UnsupportedFormat):
    pass


class UnsupportedDeserializationFormat(UnsupportedFormat):
    pass


class ImmediateHttpResponse(DeliciousCakeError):
    """
    This exception is used to interrupt the flow of processing to immediately
    return a custom HttpResponse.

    Common uses include::

        * for authentication (like digest/OAuth)
        * for throttling

    """

    def __init__(self, response=None, response_cls=None, **response_kwargs):
        if response is None and response_cls is None:
            raise ValueError(
                "Must specify either 'response' or 'response_cls'")

        self.response = response
        self.response_cls = response_cls
        self.response_kwargs = response_kwargs


class BadRequest(DeliciousCakeError):
    """
    A generalized exception for indicating incorrect request parameters.

    Handled specially in that the message tossed by this exception will be
    presented to the end user.
    """
    pass


class ResourceEntityError(DeliciousCakeError):
    pass


class WrongNumberOfValues(DeliciousCakeError):
    pass


class ApiFieldError(DeliciousCakeError):
    """
    Raised when there is a configuration error with a ``ApiField``.
    """
    pass


class FormValidationError(DeliciousCakeError):
    def __init__(self, form_errors):
        self.form_errors = form_errors
