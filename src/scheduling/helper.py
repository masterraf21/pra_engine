
from src.utils import diff_two_datetime_str
import time
from .constants import REALTIME_CHECK_PERIOD, TRACE_LIMIT
from .models import TraceRangeParam
from src.zipkin.helper import retrieve_traces
from src.zipkin.models import AdjustedTrace, TraceParam


async def get_ranged_traces(param: TraceRangeParam) -> list[AdjustedTrace]:
    time_param = diff_two_datetime_str(
        start_str=param.startDatetime,
        end_str=param.endDatetime
    )
    param = TraceParam(
        endTs=time_param.endTs,
        limit=param.limit,
        lookback=time_param.lookback
    )
    traces = await retrieve_traces(param)
    return traces


async def get_realtime_traces() -> list[AdjustedTrace]:
    param = TraceParam(
        endTs=round(time.time() * 1000),
        limit=TRACE_LIMIT,
        lookback=REALTIME_CHECK_PERIOD*1000
    )
    traces = await retrieve_traces(param)
    return traces
