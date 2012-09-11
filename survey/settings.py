from django.conf import settings

# any settings that should be available to templates via
# template context processors, should be UPPERCASE
HOST_NAME = getattr(settings, "HOST_NAME", '127.0.0.1')
PORT = getattr(settings, "PORT", '8000')
HOST_URL = getattr(settings, "HOST_URL", '127.0.0.1:8000')