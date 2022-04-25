from .models import *
from .clock_skew import tree_corrected_for_clock_skew
from .trace import detailed_trace_summary


def adjust_trace(trace: list[Span]) -> AdjustedTrace:
    node = tree_corrected_for_clock_skew(trace)
    return detailed_trace_summary(node)


async def adjust_traces(traces: list[list[Span]]) -> list[AdjustedTrace]:
    nodes = [tree_corrected_for_clock_skew(trace) for trace in traces]
    adjusted_traces = [detailed_trace_summary(node) for node in nodes]
    return adjusted_traces
