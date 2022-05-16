import json
import logging
import time
from datetime import datetime

from src.config import ALPHA, state
from src.critical_path import compare_critical_path
from src.statistic.ks import ks_test_same_dist
from src.storage.repository import StorageRepository
from src.transform import extract_critical_path, extract_durations
from src.utils import diff_two_datetime_str
from src.zipkin.helper import retrieve_traces
from src.zipkin.models import AdjustedTrace, TraceParam

from .constants import REALTIME_CHECK_PERIOD, TRACE_LIMIT
from .models import BaselineParam


class EngineJobs:
    def __init__(self, redis_repo: StorageRepository, logger: logging.Logger) -> None:
        self._storage_repo = redis_repo
        self._logger = logger

    async def get_baseline_traces(self, param: BaselineParam) -> list[AdjustedTrace]:
        try:
            time_param = diff_two_datetime_str(
                start_str=param.startDatetime,
                end_str=param.endDatetime
            )
            print(time_param)
            param = TraceParam(
                endTs=time_param[0],
                limit=param.limit,
                lookback=time_param[1]
            )
            traces = await retrieve_traces(param)
            return traces
        except ValueError as e:
            self._logger.exception(e)

    async def get_realtime_traces(self) -> list[AdjustedTrace]:
        param = TraceParam(
            endTs=round(time.time() * 1000),
            limit=TRACE_LIMIT,
            lookback=REALTIME_CHECK_PERIOD*1000
        )
        traces = await retrieve_traces(param)
        return traces

    def delete_baseline_model(self):
        state.baselineReady = False
        state.baselineKey.duration = ""
        state.baselineKey.criticalPath = ""

    async def retrieve_baseline_models(self, param: BaselineParam):
        '''Query baseline traces from zipkin, transform into models
        , store in redis, change global state'''

        traces = await self.get_baseline_traces(param)

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
            self._logger.info("Baseline Not Ready")
            return False

        realtime_traces = await self.get_realtime_traces()
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
            self._logger.info("Baseline Not Ready")
            return

        realtime_traces = await self.get_realtime_traces()
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

    async def regression_analysis(self):
        self._logger.info("Doing Regression Analysis")
        if self.check_regression():
            self._logger.info("Regression Detected")
            await self.perform_analysis()
        else:
            self._logger.info("No Regression Detected")

    def regression_analysis_fake(self):
        self._logger.info("Doing Regression Analysis")
