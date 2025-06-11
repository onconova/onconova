from django.http import HttpRequest
from allauth.headless.contrib.ninja.security import XSessionTokenAuth as XSessionTokenAuthBase


class XSessionTokenAuth(XSessionTokenAuthBase):
    """
    Custom security class for session-based authentication using the
    'X-SESSION-TOKEN' HTTP header, compatible with django-allauth headless.

    Adds OpenAPI metadata for schema generation.
    """

    openapi_type: str = "apiKey"
    openapi_in: str = "header"
    openapi_name: str = "X-SESSION-TOKEN"

    def __call__(self, request: HttpRequest):
        """
        Authenticate the user using the X-SESSION-TOKEN header.

        Args:
            request (HttpRequest): Incoming HTTP request.

        Returns:
            Optional[User]: The authenticated user if the token is valid, otherwise None.
        """
        user = super().__call__(request)
        if user:
            request.user = user
        return user