from datetime import *

from django.conf import settings
from django.utils import timezone
from datetime import datetime as _datetime


class datetime(_datetime):
    """
    A custom datetime.datetime class which acts as a compatibility
    layer between migrations and Django installations.

    It basically adds the default timezone (as configured in Django's
    settings) automatically if no tzinfo is given.
    """
    def __new__(cls, year, month, day,
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None):

        dt = _datetime(year, month, day,
                       hour, minute, second, microsecond,
                       tzinfo=tzinfo)
        if tzinfo is None and getattr(settings, "USE_TZ", False):
            default_timezone = timezone.get_default_timezone()
            dt = timezone.make_aware(dt, default_timezone)
        return dt
