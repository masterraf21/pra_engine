
import json
import time
import unittest
from datetime import datetime

from src.transform import extract_durations
from src.utils import diff_two_datetime, write_json
from src.zipkin.helper import retrieve_traces
from src.zipkin.models import TraceParam
from src.zipkin.query import query_traces


class TestLive(unittest.IsolatedAsyncioTestCase):
    async def test_extract_baseline(self):
        # now = round(time.time() * 1000)
        # lb = 60*(60*1000)
        param = diff_two_datetime(
            end=datetime(2022, 5, 16, 8, 55, 47),
            start=datetime(2022, 5, 16, 8, 10, 47)
        )
        traces = await retrieve_traces(TraceParam(
            endTs=param.endTs,
            lookback=param.lookback,
            limit=500
        ))
        print(len(traces))
        # # print(traces)

        # durations = extract_durations(traces)

        # t_json = [t.dict() for t in traces]
        # write_json(json.dumps(t_json), "test_live.json")

        # write_json(json.dumps(durations), "durations_baseline_1405_939pm.json")

    async def test_debug(self):
        now = round(time.time() * 1000)
        lb = 60*(60*1000)
        traces = await query_traces(TraceParam(
            endTs=now,
            lookback=lb,
            limit=2
        ))
        t_json = []
        for trace in traces:
            spans = [s.dict() for s in trace]
            t_json.append(spans)
        write_json(json.dumps(t_json), "test_raw.json")
