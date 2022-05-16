from collections import namedtuple
from datetime import datetime

TimeQuery = namedtuple("TimeQuery", "endTs lookback")
DATE_FORMAT = '%d/%m/%Y %H:%M:%S'


def diff_two_datetime(start_str: str, end_str: str) -> TimeQuery:
    start = datetime.strptime(start_str, DATE_FORMAT)
    end = datetime.strptime(end_str, DATE_FORMAT)
    diff = end - start
    diff_ms = round(diff.total_seconds() * 1000)
    end_ts = round(end.timestamp())

    out = TimeQuery(end_ts, diff_ms)
    return out
