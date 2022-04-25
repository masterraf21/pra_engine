
from .clock_skew import tree_corrected_for_clock_skew
from .models import AdjustedTrace, Span, TraceParam
from .trace import detailed_trace_summary
from .query import query_traces


def adjust_trace(trace: list[Span]) -> AdjustedTrace:
    node = tree_corrected_for_clock_skew(trace)
    return detailed_trace_summary(node)


def adjust_traces(traces: list[list[Span]]) -> list[AdjustedTrace]:
    ret: list[AdjustedTrace] = []
    for trace in traces:
        ret.append(adjust_trace(trace))
    return ret


async def retrieve_traces(param: TraceParam) -> list[AdjustedTrace]:
    raw_traces = await query_traces(param)
    traces = adjust_traces(raw_traces)
    return traces
