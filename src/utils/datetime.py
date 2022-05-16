from collections import namedtuple
from datetime import datetime
import pytz

TimeQuery = namedtuple("TimeQuery", "endTs lookback")
timezone = pytz.timezone("Asia/Jakarta")


def diff_two_datetime(start: datetime, end: datetime) -> TimeQuery:
    start = timezone.localize(start)
    end = timezone.localize(end)
    diff = end - start

    diff_ms = round(diff.total_seconds() * 1000)
    end_ts = round(end.timestamp()*1000)

    out = TimeQuery(end_ts, diff_ms)
    return out
