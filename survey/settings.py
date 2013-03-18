from django.conf import settings

# tells when the cookie to prevent ballot stuffing will expire
# setting is in weeks
# defaults to 24 weeks (6 months)
COOKIE_EXPIRATION = getattr(settings, "COOKIE_EXPIRATION", 4 * 6)
