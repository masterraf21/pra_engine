from functools import cmp_to_key
from inspect import trace
from pydash import order_by
from .span_cleaner import compare
from .span_node import SpanNode
from .span_row import get_service_name, new_span_row
from .utils import *


def add_timestamps(span: dict, timestamps: list):
    if not key_exists(span, "timestamp"):
        return
    timestamps.append(span["timestamp"])
    if not key_exists(span, "duration"):
        return
    timestamps.append(span["timestamp"] + span["timestamp"])


def get_max_duration(timestamps: list):
    if len(timestamps) > 1:
        timestamps.sort()
        return timestamps[len(timestamps)-1] - timestamps[0]
    return 0


def node_by_timestamp(a: SpanNode, b: SpanNode):
    return compare(a.span["timestamp"], b.span["timestamp"])


def get_trace_timestamp_and_duration(root: SpanNode):
    timestamps = []
    root.traverse(lambda span: add_timestamps(span, timestamps))
    return timestamps[0] or 0, get_max_duration(timestamps)


def push_entry(d: dict, key, val):
    if d[key] and isinstance(d[key], list):
        d[key].append(val)
    else:
        d[key] = [val]


def make_durationStr(duration):
    if duration == 0 or duration == None:
        return ''
    if duration < 1000:
        return f'{duration:.0f}μs'
    if duration < 1000000:
        if duration % 1000 == 0:
            return f'{duration/1000:.0f}ms'
        return f'{duration/1000:.3f}ms'
    return f'{duration/1000000: .3f}s'


def add_layout_details(span_row: dict, trace_timestamp,
                       trace_duration, depth, child_ids):
    span_row["childIds"] = child_ids
    span_row["depth"] = depth+1
    span_row["depthClass"] = (depth-1) % 6

    if key_exists(span_row, "duration"):
        width = (span_row["duration"]/trace_duration *
                 100) if trace_duration else 0
        span_row["width"] = 0.1 if width < 0.1 else width
        span_row["durationStr"] = make_durationStr(span_row["duration"])
    else:
        span_row["width"] = 0.1
        span_row["durationStr"] = ''

    if trace_duration:
        span_row["left"] = (
            (span_row["timestamp"]-trace_timestamp)/trace_duration)*100

        if key_exists(span_row, "annotations") and check_list(span_row["annotations"]):
            for a in span_row["annotations"]:
                if key_exists(span_row, "duration"):
                    a["left"] = (
                        (a["timestamp"]-span_row["timestamp"])/span_row["duration"]) * 100
                else:
                    a["left"] = 0
                a["relativeTime"] = make_durationStr(
                    a["timestamp"]-trace_timestamp)
                a["width"] = 0
    else:
        span_row["left"] = 0


def increment_entry(d: dict, key):
    if key in d:
        d[key] += 1
    else:
        d[key] = 1


def trace_summary(root: SpanNode):
    pass


def detailed_trace_summary(root: SpanNode):
    service_name_to_count = {}
    queue = root.queue_root_most_spans()
    model_view = {
        "traceId": queue[0].span["traceId"],
        "depth": 0,
        "spans": []
    }

    timestamp, duration = get_trace_timestamp_and_duration(root)

    if not timestamp:
        raise ValueError(
            f'Trace {model_view["traceId"]} is missing a timestamp')

    while len(queue) > 0:
        current = queue.popleft()

        spans_to_merge = [current.span]
        children = []
        for child in current.children:
            if current.span["id"] == child.span["id"]:
                spans_to_merge.append(child.span)
                for grand_child in child.children:
                    children.append(grand_child)
            else:
                children.append(child)

        sorted(children, key=cmp_to_key(node_by_timestamp))
        queue = children.extend(queue)
        child_ids = list(map(lambda child: child.span["id"], children))

        depth = 1
        while (current.parent and current.parent.span):
            if current.parent.span["id"] != current.span["id"]:
                depth += 1
            current = current.parent

        if depth > model_view["depth"]:
            model_view["depth"] = depth

        is_leaf_span = len(children) == 0
        span_row = new_span_row(spans_to_merge, is_leaf_span)

        add_layout_details(span_row, timestamp, duration, depth, child_ids)

        for service_name in span_row["serviceNames"]:
            increment_entry(service_name_to_count, service_name)

        model_view["spans"].append(span_row)

    model_view["rootSpan"] = {}
    root_span = root.queue_root_most_spans()[0]
    model_view["rootSpan"]["serviceName"] = get_service_name(
        root_span.span["localEndpoint"]) or get_service_name(
        root_span.span["remoteEndpoint"]) or 'unknown'
    model_view["rootSpan"]["spanName"] = root_span.span["name"] or 'unknown'

    service_names = list(service_name_to_count.keys()).sort()
    model_view["serviceNameAndSpanCounts"] = list(map(lambda service_name: {
        "serviceName": service_name,
        "spanCount": service_name_to_count[service_name]
    }, service_names))

    model_view["spansBackup"] = model_view["spans"]

    time_markers = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    model_view["timeMarkers"] = []
    for i, p in enumerate(time_markers):
        model_view["timeMarkers"].append({
            "index": i,
            "time": make_durationStr(duration*p)
        })
    model_view["timeMarkersBackup"] = model_view["timeMarkers"]

    model_view["duration"] = duration
    model_view["durationStr"] = make_durationStr(duration)

    return model_view
