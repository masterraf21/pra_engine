from zipkin.query import query_traces
from zipkin.models import TraceParam
from zipkin.helper import adjust_traces
from transform import transform
import unittest


class TestTransform(unittest.TestCase):
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
        durations = transform.extract_durations(adjusted_traces)
        print(durations)
