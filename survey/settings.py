from django.conf import settings

# any settings that should be available to templates via
# template context processors, should be UPPERCASE
HOST_NAME = getattr(settings, "HOST_NAME", '127.0.0.1')
PORT = getattr(settings, "PORT", '8000')
HOST_URL = getattr(settings, "HOST_URL", '127.0.0.1:8000')
# tells when the cookie to prevent ballot stuffing will expire
# setting is in weeks
# defaults to 24 weeks (6 months)
COOKIE_EXPIRATION = getattr(settings, "COOKIE_EXPIRATION", 4 * 6)
