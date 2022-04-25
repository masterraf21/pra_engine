import json
import time
from datetime import datetime

from critical_path import compare_critical_path
from src.config import ALPHA, state
from src.storage.repository import StorageRepository
from statistic.ks import ks_test_same_dist
from transform import extract_critical_path, extract_durations
from zipkin.helper import adjust_traces
from zipkin.models import AdjustedTrace, TraceParam
from zipkin.query import query_traces

from .constants import TRACE_LIMIT, BASELINE_PROBE_TIME, REALTIME_CHECK_PERIOD


class EngineJobs:
    def __init__(self, redis_repo: StorageRepository) -> None:
        self._storage_repo = redis_repo

    def get_baseline_traces(self) -> list[AdjustedTrace]:
        raw_traces = query_traces(TraceParam(
            endTs=round(time.time() * 1000),
            limit=TRACE_LIMIT,
            lookback=BASELINE_PROBE_TIME*1000
        ))
        traces = adjust_traces(raw_traces)
        return traces

    def get_realtime_traces(self) -> list[AdjustedTrace]:
        raw_traces = query_traces(TraceParam(
            endTs=round(time.time() * 1000),
            limit=TRACE_LIMIT,
            lookback=REALTIME_CHECK_PERIOD*1000
        ))
        traces = adjust_traces(raw_traces)
        return traces

    async def retrieve_baseline_models(self):
        '''Query baseline traces from zipkin, transform into models
        , store in redis, change global state'''

        traces = self.get_baseline_traces()

        durations = extract_durations(traces)
        paths = extract_critical_path(traces)
        paths_json = [p.dict() for p in paths]

        curr_dt = datetime.now()
        timestamp = int(round(curr_dt.timestamp()))
        durations_key = f"baseline_durations-{timestamp}"
        paths_key = f"baseline_critical_path-{timestamp}"

        await self._storage_repo.store_json(durations_key, json.dumps(durations))
        await self._storage_repo.store_json(paths_key, json.dumps(paths_json))

        state.baselineReady = True
        state.baselineKey.duration = durations_key
        state.baselineKey.criticalPath = paths_key

    async def check_regression(self) -> bool:
        '''Check realtime regression by comparing realtime
        durations to baseline durations'''
        if not state.baselineReady:
            return False

        realtime_traces = self.get_realtime_traces()
        realtime_durations = extract_durations(realtime_traces)
        baseline_durations = await self._storage_repo.retrieve_durations(state.baselineKey.duration)

        same_distribution = ks_test_same_dist(
            realtime_durations, baseline_durations, ALPHA)

        state.lastRegressionCheck = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        state.isRegression = not same_distribution
        return not same_distribution

    async def perform_analysis(self):
        '''Perform Critical Path analysis + Correlation Analysis
        and store in redis'''
        if not state.baselineReady:
            return

        realtime_traces = self.get_realtime_traces()
        realtime_paths = extract_critical_path(realtime_traces)
        baseline_paths = await self._storage_repo.retrieve_critical_path(state.baselineKey.criticalPath)

        result_paths = compare_critical_path(baseline_paths, realtime_paths)
        result_paths_json = [p.json() for p in result_paths]

        curr_dt = datetime.now()
        timestamp = int(round(curr_dt.timestamp()))
        result_paths_key = f"result_critical_path-{timestamp}"

        await self._storage_repo.store_json(result_paths_key,
                                            json.dumps(result_paths_json))
        state.resultKey.criticalPath = result_paths_key

    async def regression_analysis(self, debug: bool = False):
        if debug:
            print("Doing Regression Analysis")
        if self.check_regression():
            await self.perform_analysis()


def regression_analysis_fake():
    print("Doing Regression Analysis")
