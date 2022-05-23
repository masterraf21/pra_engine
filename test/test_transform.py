import json
import time
import unittest

from src.transform.extract import extract_critical_path, extract_critical_path
from src.transform.extract import extract_critical_path_v2, extract_durations
from src.utils.testing import write_json, get_traces_json
from src.zipkin.helper import adjust_traces
from src.zipkin.models import TraceParam
from src.zipkin.query import query_traces


class TestTransform(unittest.TestCase):
    def test_extract_critical_path_v3(self):
        traces = get_traces_json('/data/traces_regress.json')
        path = extract_critical_path(traces)
        path_json = [p.dict() for p in path]

        write_json(json.dumps(path_json), '/testing/critical_path_v3.json')

    def test_extract_critical_path_v2(self):
        traces = get_traces_json('/data/traces_regress.json')
        path = extract_critical_path_v2(traces)
        path_json = [p.dict() for p in path]

        write_json(json.dumps(path_json), '/testing/critical_path_v2.json')

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
