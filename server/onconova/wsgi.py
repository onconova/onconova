"""
WSGI config for the Onconova Django project.

This file sets up the WSGI (Web Server Gateway Interface) application, 
which allows Django to handle synchronous HTTP requests.

Key points:

- WSGI is the standard interface between web servers and Python web applications.

- The `application` object defined here is used by WSGI servers (e.g., Gunicorn, uWSGI, mod_wsgi) 
  to communicate with your Django project.

- The environment variable `DJANGO_SETTINGS_MODULE` is set to specify which settings 
  file Django should use for configuration.

For more details, see:
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/

Usage in the server:
- When you deploy your Django project with a WSGI server, this file is the entry point.
- The WSGI server loads the `application` object to route incoming HTTP requests to Django.

"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onconova.settings")

application = get_wsgi_application()
"""
WSGI application callable for the Django project.

This object is used by WSGI servers to forward HTTP requests to Django.
It is created using Django's `get_wsgi_application()` function, which
sets up the request handling pipeline according to the project's settings.
"""

