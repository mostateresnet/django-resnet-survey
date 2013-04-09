from __future__ import division
from datetime import timedelta


if not hasattr(timedelta, 'total_seconds'):
    def total_seconds(td):
        "Return the total number of seconds contained in the duration for Python 2.6 and under."
        return (td.microseconds + (td.seconds + td.days * 86400) * 1e6) / 1e6
else:
    total_seconds = timedelta.total_seconds
