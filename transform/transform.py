from zipkin.models import AdjustedTrace, AdjustedSpan
from .models import *


def extract_critical_path(spans: list[AdjustedTrace]) -> list[CriticalPathData]:
    res: list[CriticalPathData] = []

    return res


def extract_spans_durations(spans: list[AdjustedSpan]) -> list[float]:
    res: list[float] = []
    for span in spans:
        res.append(span.duration/1000)
    return res


def extract_durations(traces: list[AdjustedTrace]) -> list[float]:
    res: list[float] = []
    for trace in traces:
        span_dur = extract_spans_durations(trace.spans)
        res.extend(span_dur)

    res.sort()
    return res


def to_cdf():
    pass
