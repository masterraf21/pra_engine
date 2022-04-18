import json
import time
import unittest

from transform.extract import *
from utils.testing import *
from zipkin.helper import adjust_traces
from zipkin.models import TraceParam
from zipkin.query import query_traces


class TestTransform(unittest.TestCase):
    def test_extract_critical_path(self):
        now = round(time.time() * 1000)
        lb = 60*(60*1000)
        traces = query_traces(TraceParam(
            lookback=lb,
            endTs=now,
            limit=50,
            # serviceName="kafka"
        ))
        adjusted_traces = adjust_traces(traces)
        path = extract_critical_path(adjusted_traces)
        path_json = [p.dict() for p in path]
        write_json(json.dumps(path_json), "critical_path.json")

    def test_extract_duration(self):
        traces = query_traces(TraceParam(
            lookback=900000,
            # endTs=1649486377677,
            endTs=1649570805457,
            limit=10
        ))
        # print(len(traces))
        adjusted_traces = adjust_traces(traces)
        # print(len(adjusted_traces))
        durations = extract_durations(adjusted_traces)
        print(durations)
