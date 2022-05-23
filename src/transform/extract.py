from src.zipkin.models import AdjustedTrace, AdjustedSpan
from src.critical_path.models import PathDuration
import numpy as np


def extract_critical_path(traces: list[AdjustedTrace]) -> list[PathDuration]:
    res: list[PathDuration] = []
    lookup: dict[str, list[float]] = {}

    for trace in traces:
        for span in trace.spans:
            operation = f"{span.spanName}"
            duration = span.duration/1000
            if operation not in lookup:
                lookup[operation] = [duration]
            else:
                lookup[operation].append(duration)

    for operation in lookup.keys():
        durations = lookup[operation]
        duration_avg = round(np.average(durations), 3)
        res.append(PathDuration(
            duration=duration_avg,
            operation=operation,
            counter=len(durations)
        ))

    return res


def extract_spans_durations(spans: list[AdjustedSpan]) -> list[float]:
    res: list[float] = []
    for span in spans:
        # duration in microsecond, convert to milisecond
        res.append(span.duration/1000)
    return res


def extract_durations(traces: list[AdjustedTrace]) -> list[float]:
    res: list[float] = []
    for trace in traces:
        span_dur = extract_spans_durations(trace.spans)
        res.extend(span_dur)

    res.sort()
    return res
