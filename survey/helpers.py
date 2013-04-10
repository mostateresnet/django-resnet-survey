from __future__ import division
from datetime import timedelta, datetime, tzinfo


if not hasattr(timedelta, 'total_seconds'):
    def total_seconds(td):
        "Return the total number of seconds contained in the duration for Python 2.6 and under."
        return (td.microseconds + (td.seconds + td.days * 86400) * 1e6) / 1e6
else:
    total_seconds = timedelta.total_seconds


# Timezone related stuff
# (mostly copied from https://github.com/django/django/blob/master/django/utils/timezone.py)
try:
    from django.utils.timezone import now, get_current_timezone
except ImportError:
    now = datetime.now
    get_current_timezone = lambda: None
