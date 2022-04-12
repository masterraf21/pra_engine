from zipkin.models import AdjustedTrace, AdjustedSpan
from .models import *
import numpy as np


def extract_critical_path(traces: list[AdjustedTrace]) -> list[CriticalPathData]:
    res: list[CriticalPathData] = []
    for trace in traces:
        temp: dict[str, list[float]] = {}
        root_span = trace.rootSpan
        root = f"{root_span.serviceName}: {root_span.spanName}"
        for span in trace.spans:
            operation = f"{span.serviceName}: {span.spanName}"
            duration = span.duration/1000
            if operation not in temp:
                temp[operation] = [duration]
            else:
                temp[operation].append(duration)
        for key in temp.keys():
            duration_avg = np.average(temp[key])
            data = CriticalPathData(
                root=root,
                operation=key,
                duration=duration_avg
            )
            res.append(data)
    return res


def extract_spans_durations(spans: list[AdjustedSpan]) -> list[float]:
    res: list[float] = []
    for span in spans:
        # duration in microsecond
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
