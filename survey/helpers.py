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
    from django.utils.timezone import now, get_current_timezone, utc
except ImportError:
    now = datetime.now
    get_current_timezone = lambda: None

    class UTC(tzinfo):
        """
        UTC implementation taken from Python's docs.
        """

        def __repr__(self):
            return "<UTC>"

        def utcoffset(self, dt):
            return timedelta(0)

        def tzname(self, dt):
            return "UTC"

        def dst(self, dt):
            return timedelta(0)

    utc = UTC()
