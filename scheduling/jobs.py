import time

import schedule
from numpy import extract
from statistic.ks import ks_test_same_dist
from transform import extract_durations
from zipkin.helper import adjust_traces
from zipkin.models import AdjustedTrace, TraceParam
from zipkin.query import query_traces

from .constants import *


def get_baseline_traces() -> list[AdjustedTrace]:
    pass


# def store_durations(dur: list[]) -> list[AdjustedTrace]:
#     pass


def get_realtime_traces() -> list[AdjustedTrace]:
    raw_traces = query_traces(TraceParam(
        endTs=round(time.time() * 1000),
        limit=TRACE_LIMIT,
        lookback=REALTIME_CHECK_PERIOD*1000
    ))
    traces = adjust_traces(raw_traces)
    return traces


def check_regression() -> bool:
    realtime_traces = get_realtime_traces()
    realtime_durations = extract_durations(realtime_traces)

    return True


def perform_analysis():
    pass
