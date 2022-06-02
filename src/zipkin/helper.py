
from src.config import get_settings
from src.utils.logging import get_logger
from .clock_skew import tree_corrected_for_clock_skew
from .models import AdjustedTrace, Span, TraceParam
from .trace import detailed_trace_summary
from .query import query_traces
import time
env = get_settings()
logger = get_logger(__name__)


def adjust_trace(trace: list[Span]) -> AdjustedTrace:
    node = tree_corrected_for_clock_skew(trace)
    return detailed_trace_summary(node)


def adjust_traces(traces: list[list[Span]]) -> list[AdjustedTrace]:
    ret: list[AdjustedTrace] = []
    for trace in traces:
        ret.append(adjust_trace(trace))
    return ret


async def retrieve_traces(param: TraceParam) -> list[AdjustedTrace]:
    query_t0 = time.time()
    raw_traces = await query_traces(param)
    query_t1 = time.time()
    if env.debug:
        logger.debug(f"Query time: {query_t1-query_t0:.2f}s")

    adjust_t0 = time.time()
    traces = adjust_traces(raw_traces)
    adjust_t1 = time.time()
    if env.debug:
        logger.debug(f"Trace Adjust time: {adjust_t1-adjust_t0:.2f}s")

    return traces
