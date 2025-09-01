"""
ASGI config for the Onconova Django project.

This file sets up the ASGI (Asynchronous Server Gateway Interface) application, 
which allows Django to handle asynchronous web protocols such as WebSockets, 
in addition to traditional HTTP requests.

Key points:
- ASGI is the successor to WSGI, enabling asynchronous features in Django.
- The `application` object defined here is used by ASGI servers (e.g., Daphne, Uvicorn) 
  to communicate with your Django project.
- The environment variable `DJANGO_SETTINGS_MODULE` is set to specify which settings 
  file Django should use for configuration.

For more details, see:
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/

Usage in the server:
- When you deploy your Django project with an ASGI server, this file is the entry point.
- The ASGI server loads the `application` object to route incoming requests to Django.
"""


import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_asgi_application()
"""
ASGI application callable for the Django project.

This object is used by ASGI servers to forward HTTP requests to Django.
It is created using Django's `get_asgi_application()` function, which
sets up the request handling pipeline according to the project's settings.
"""

