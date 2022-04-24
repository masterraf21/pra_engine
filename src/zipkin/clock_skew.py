from .span_node import *
from .models import *


class ClockSkew:
    def __init__(self, endpoint: Endpoint, skew) -> None:
        self._endpoint = endpoint
        self._skew = skew

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def skew(self):
        return self._skew


def ips_match(a: Optional[Endpoint], b: Optional[Endpoint]):
    if not a or not b:
        return False
    if a.ipv6 and b.ipv6 and a.ipv6 == b.ipv6:
        return True
    if not a.ipv4 and not b.ipv4:
        return False

    return a.ipv4 == b.ipv4


def adjust_timestamps(span: Span, skew):
    if not ips_match(skew.endpoint, span.localEndpoint):
        return span

    result = span
    if span.timestamp:
        result.timestamp = span.timestamp - skew.skew

    annotation_length = len(span.annotations)
    if annotation_length > 0:
        result.annotations = []
    for i in range(annotation_length):
        a = span.annotations[i]
        result.annotations[i] = Annotation(
            timestamp=a.timestamp - skew.skew,
            value=a.value
        )

    return result


def get_clock_skew(node: SpanNode):
    parent = node.parent.span if node.parent else None
    child = node.span
    if not parent:
        return None

    if parent.kind == "CLIENT" or child.kind == "SERVER":
        return None

    one_way = False
    client_timestamp = parent.timestamp
    server_timestamp = child.timestamp
    if not client_timestamp or not server_timestamp:
        return None

    client_duration = parent.duration
    server_duration = child.duration
    if not client_duration or not server_duration:
        one_way = True

    server = child.localEndpoint
    if not server:
        return None
    client = parent.localEndpoint
    if not client:
        return None

    if ips_match(server, client):
        return None

    if one_way:
        latency = server_timestamp - client_timestamp

        if latency > 0:
            return None
        return ClockSkew(server, latency-1)

    if client_duration < server_duration:
        skew = server_timestamp - client_timestamp - 1
        return ClockSkew(server, skew)

    latency = (client_duration - server_duration)/2

    if latency < 0:
        return None

    skew = server_timestamp - latency - client_timestamp
    if skew != 0:
        return ClockSkew(server, skew)

    return None


def adjust(node: SpanNode, skew_from_parent: Optional[ClockSkew] = None):
    if skew_from_parent:
        node.span = adjust_timestamps(node.span, skew_from_parent)

    skew = get_clock_skew(node)
    if skew:
        node.span = adjust_timestamps(node.span, skew)
    elif skew_from_parent:
        skew = skew_from_parent

    for child in node.children:
        adjust(child, skew)


def tree_corrected_for_clock_skew(spans: list[Span], debug=False) -> SpanNode:
    if len(spans) == 0:
        return SpanNode()

    trace = SpanNodeBuilder(debug).build(spans)

    if not trace.span:
        if debug:
            print(
                f'skipping clock skew adjustment due to missing root span: traceId={spans[0].traceId}')
        return trace

    children_of_root = trace.children
    for i in range(len(children_of_root)):
        next = children_of_root[i].span
        if next.parentId or next.shared:
            continue

        traceId = next.traceId
        span_id = next.id
        root_span_id = trace.span.id
        if debug:
            prefix = "skipping redundant root span"
            print(
                f'{prefix}: traceId={traceId}, rootId={root_span_id}, id={span_id}')
        return trace

    adjust(trace)
    return trace
