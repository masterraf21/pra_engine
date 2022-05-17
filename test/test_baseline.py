import json
import unittest

from src.critical_path.models import CriticalPath
from src.scheduling.models import TraceRangeParam
from src.transform import extract_critical_path, extract_durations
from src.utils import diff_two_datetime_str, write_json
from src.zipkin.helper import retrieve_traces
from src.zipkin.models import AdjustedTrace, TraceParam


class TestBaseline(unittest.IsolatedAsyncioTestCase):
    async def get_ranged_duration_path(self, param: TraceRangeParam) -> tuple[list[float], list[CriticalPath]]:
        traces = await self.get_ranged_traces(param)
        durations = extract_durations(traces)
        paths = extract_critical_path(traces)
        return (durations, paths)

    async def get_ranged_traces(self, param: TraceRangeParam) -> list[AdjustedTrace]:
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

    async def test_get_traces(self):
        baseline_param = TraceRangeParam(
            endDatetime="16/05/2022 09:00:00",
            startDatetime="16/05/2022 08:00:00",
            limit=10000
        )
        regress_param = TraceRangeParam(
            endDatetime="17/05/2022 10:59:00",
            startDatetime="17/05/2022 10:52:00",
            limit=5000
        )

        baseline_traces = await self.get_ranged_traces(baseline_param)
        regress_traces = await self.get_ranged_traces(regress_param)
        b_json = [b.json() for b in baseline_traces]
        r_json = [r.json() for r in regress_traces]

        write_json(json.dumps(b_json), "/data/traces_baseline.json")
        write_json(json.dumps(r_json), "/data/traces_regress.json")

    async def test_get_baselines(self):
        start_time = "16/05/2022 08:00:00"
        end_time = "16/05/2022 09:00:00"
        limit = 10000

        durations, paths = await self.get_ranged_duration_path(TraceRangeParam(
            endDatetime=end_time, startDatetime=start_time, limit=limit
        ))
        paths_json = [p.dict() for p in paths]
        write_json(json.dumps(durations), "/data/durations_baseline.json")
        write_json(json.dumps(paths_json), "/data/paths_baseline.json")

    async def test_get_regressed(self):
        start_time = "17/05/2022 10:52:00"
        end_time = "17/05/2022 10:59:00"
        limit = 5000
        durations, paths = await self.get_ranged_duration_path(TraceRangeParam(
            endDatetime=end_time, startDatetime=start_time, limit=limit
        ))
        paths_json = [p.dict() for p in paths]
        write_json(json.dumps(durations), "/data/durations_regress.json")
        write_json(json.dumps(paths_json), "/data/paths_regress.json")
