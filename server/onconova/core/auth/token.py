"""
Module providing a custom authentication class for session-based authentication using the X-SESSION-TOKEN HTTP header in Django.
"""
from django.http import HttpRequest
from allauth.headless.contrib.ninja.security import (
    XSessionTokenAuth as XSessionTokenAuthBase,
)

class XSessionTokenAuth(XSessionTokenAuthBase):
    """
    Custom authentication class for session-based authentication using the `X-SESSION-TOKEN` HTTP header.

    This class extends XSessionTokenAuthBase to provide compatibility with django-allauth in headless mode.
    It also adds OpenAPI metadata for schema generation, specifying the authentication type, location, and header name.

    Attributes:
        openapi_type (str): The OpenAPI security scheme type (`'apiKey'`).
        openapi_in (str): The location of the API key (`'header'`).
        openapi_name (str): The name of the header containing the session token (`'X-SESSION-TOKEN'`).

    Methods:
        __call__(request: HttpRequest) -> Optional[User]:
            Authenticates the user using the `X-SESSION-TOKEN` header.
            If authentication is successful, sets `request.user` to the authenticated user.
            Returns the authenticated user if the token is valid, otherwise `None`.
    """

    openapi_type: str = "apiKey"
    openapi_in: str = "header"
    openapi_name: str = "X-SESSION-TOKEN"

    def __call__(self, request: HttpRequest):
        """
        Authenticate the user using the `X-SESSION-TOKEN` header.

        Args:
            request (HttpRequest): Incoming HTTP request.

        Returns:
            (User | None): The authenticated user if the token is valid, otherwise None.
        """
        user = super().__call__(request)
        if user:
            request.user = user
        return user
