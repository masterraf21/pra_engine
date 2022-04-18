from zipkin.models import AdjustedTrace, AdjustedSpan
from critical_path.models import CriticalPath, PathDuration
import numpy as np


def extract_critical_path(traces: list[AdjustedTrace]) -> list[CriticalPath]:
    res: list[CriticalPath] = []
    lookup: dict[str, dict[str, list[float]]] = {}
    for trace in traces:
        temp: dict[str, list[float]] = {}
        root_span = trace.rootSpan
        root = f"{root_span.serviceName}: {root_span.spanName}"
        if root not in lookup:
            lookup[root] = {}
        for span in trace.spans:
            operation = f"{span.serviceName}: {span.spanName}"
            duration = span.duration/1000
            if operation not in lookup[root]:
                lookup[root][operation] = [duration]
            else:
                lookup[root][operation].append(duration)
    for root in lookup.keys():
        operations_lookup = lookup[root]
        durations: list[PathDuration] = []
        for operation in operations_lookup.keys():
            duration_avg = round(np.average(operations_lookup[operation]), 3)
            durations.append(PathDuration(
                duration=duration_avg,
                operation=operation,
                counter=len(operations_lookup[operation])
            ))
        res.append(CriticalPath(
            root=root,
            durations=durations
        ))

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


def extract_features_occurence(traces: list[AdjustedTrace]) -> dict[str, int]:
    res: dict[str, int] = {}
    for trace in traces:
        for span in trace.spans:
            pass

    return res
