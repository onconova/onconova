
from allauth.headless.contrib.ninja.security import XSessionTokenAuth as XSessionTokenAuthBase
from django.http import HttpRequest

class XSessionTokenAuth(XSessionTokenAuthBase):
    """
    This security class uses the X-Session-Token that django-allauth
    is using for authentication purposes.
    """
    
    openapi_type: str = "apiKey"
    openapi_in: str = "header"
    openapi_name: str = "X-SESSION-TOKEN"

    def __call__(self, request: HttpRequest):
        user = super().__call__(request)
        if user:
            request.user = user
        return user
            