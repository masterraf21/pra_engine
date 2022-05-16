from collections import namedtuple
from datetime import datetime
import pytz

TimeQuery = namedtuple("TimeQuery", "endTs lookback")
timezone = pytz.timezone("Asia/Jakarta")
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"


def diff_two_datetime_str(start_str: str, end_str: str) -> tuple:
    try:
        start = datetime.strptime(start_str, DATE_FORMAT)
        end = datetime.strptime(end_str, DATE_FORMAT)
        start = timezone.localize(start)
        end = timezone.localize(end)

        diff = end - start

        diff_ms = round(diff.total_seconds() * 1000)
        end_ts = round(end.timestamp()*1000)

        out = (end_ts, diff_ms)
        return out
    except ValueError as E:
        print(E)


def diff_two_datetime(start: datetime, end: datetime) -> TimeQuery:
    start = timezone.localize(start)
    end = timezone.localize(end)
    diff = end - start

    diff_ms = round(diff.total_seconds() * 1000)
    end_ts = round(end.timestamp()*1000)

    out = TimeQuery(end_ts, diff_ms)
    return out
