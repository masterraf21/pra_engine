import json
from datetime import datetime

import pytz
from src.config import get_settings
from src.critical_path.process import compare_critical_path
from src.statistic.ks import ks_test_same_dist
from src.storage.repository import StorageRepository
from src.transform.extract import extract_critical_path, extract_durations
from src.utils.logging import get_logger

from .helper import get_ranged_traces, get_realtime_traces
from .models import AnalysisResult, TraceRangeParam

env = get_settings()
logger = get_logger(__name__)
timezone = pytz.timezone("Asia/Jakarta")
ALPHA = env.alpha


class EngineJobs:
    def __init__(self, redis_repo: StorageRepository) -> None:
        self._storage_repo = redis_repo

    async def remove_baseline_model(self):
        state = await self._storage_repo.retrieve_state()
        state.baselineReady = False
        state.baselineKey.duration = ""
        state.baselineKey.criticalPath = ""
        await self._storage_repo.update_state(state)

    async def retrieve_baseline_models(self, param: TraceRangeParam):
        '''Query baseline traces from zipkin, transform into models
        , store in redis, change global state'''

        traces = await get_ranged_traces(param)
        if env.debug:
            logger.debug(f"Num of traces: {len(traces)} limit: {param.limit}")

        durations = extract_durations(traces)
        paths = extract_critical_path(traces)
        paths_json = [p.dict() for p in paths]

        curr_dt = datetime.now()
        timestamp = int(round(curr_dt.timestamp()))
        durations_key = f"baseline_durations-{timestamp}"
        paths_key = f"baseline_critical_path-{timestamp}"

        await self._storage_repo.store_json(durations_key, json.dumps(durations))
        await self._storage_repo.store_json(paths_key, json.dumps(paths_json))

        state = await self._storage_repo.retrieve_state()
        state.baselineReady = True
        state.baselineKey.duration = durations_key
        state.baselineKey.criticalPath = paths_key
        await self._storage_repo.update_state(state)

    async def regression_analysis_range(self, param: TraceRangeParam, latency_threshold: int) -> AnalysisResult:
        '''
            Perform regression analysis with specified time range
        '''
        regression = False

        state = await self._storage_repo.retrieve_state()
        if not state.baselineReady:
            raise ValueError("Baseline is not ready")

        ranged_traces = await get_ranged_traces(param)
        if env.debug:
            logger.debug(f"Num of traces: {len(ranged_traces)}, limit: {param.limit}")

        ranged_durations = extract_durations(ranged_traces)
        if not ranged_durations:
            logger.info("Ranged trace empty")

            return AnalysisResult()

        baseline_durations = await self._storage_repo.retrieve_durations(state.baselineKey.duration)
        # Regression = Different Distribution
        regression = not ks_test_same_dist(ranged_durations, baseline_durations, ALPHA, env.debug)
        if env.debug:
            if regression:
                logger.debug("Regression Detected")
            else:
                logger.debug("Regression not Detected")

        if not regression:
            return AnalysisResult()

        # Regression detected, perform critical path analysis
        realtime_paths = extract_critical_path(ranged_traces)
        baseline_paths = await self._storage_repo.retrieve_critical_path_v2(state.baselineKey.criticalPath)
        critical_path_result = compare_critical_path(baseline_paths, realtime_paths, latency_threshold)

        analysis_result = AnalysisResult(
            critical_path_result=critical_path_result,
            regression=regression
        )

        return analysis_result

    async def regression_analysis_realtime(self) -> AnalysisResult:
        '''
            Perform regression analysis realtime in periodical interval
        '''
        regression = False

        state = await self._storage_repo.retrieve_state()
        state.lastRegressionCheck = datetime.now(timezone).strftime("%d/%m/%y %H:%M:%S")

        if not state.baselineReady:
            await self._storage_repo.update_state(state)
            raise ValueError("Baseline is not ready")

        realtime_traces = await get_realtime_traces()
        realtime_durations = extract_durations(realtime_traces)
        if not realtime_durations:
            state.isRegression = regression
            await self._storage_repo.update_state(state)
            logger.info("Realtime Durations empty, returning False")

            return AnalysisResult()

        baseline_durations = await self._storage_repo.retrieve_durations(state.baselineKey.duration)

        # Regression = Different Distribution
        regression = not ks_test_same_dist(realtime_durations, baseline_durations, ALPHA, env.debug)
        if env.debug:
            if regression:
                logger.debug("Regression Detected")
            else:
                logger.debug("Regression not Detected")

        state.isRegression = regression

        if not regression:
            await self._storage_repo.update_state(state)
            return AnalysisResult()

        # Regression detected, perform critical path analysis
        realtime_paths = extract_critical_path(realtime_traces)
        baseline_paths = await self._storage_repo.retrieve_critical_path_v2(state.baselineKey.criticalPath)
        critical_path_result = compare_critical_path(baseline_paths, realtime_paths)

        analysis_result = AnalysisResult(
            critical_path_result=critical_path_result,
            regression=regression
        )
        state.suspectedCriticalPath = critical_path_result.suspected
        await self._storage_repo.update_state(state)

        return analysis_result
