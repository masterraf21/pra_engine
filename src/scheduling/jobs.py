import json
from datetime import datetime

from src.config import get_settings
from src.critical_path.models import ComparisonResult
from src.critical_path.process import (compare_critical_path,
                                       compare_critical_path_v3)
from src.statistic.ks import ks_test_same_dist
from src.storage.repository import StorageRepository
from src.transform import (extract_critical_path, extract_critical_path_v3,
                           extract_durations)
from src.transform.extract import extract_critical_path_v2
from src.utils.logging import get_logger

from .helper import get_ranged_traces, get_realtime_traces
from .models import AnalysisResult, TraceRangeParam

env = get_settings()
logger = get_logger(__name__)
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
        paths = extract_critical_path_v2(traces)
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

    async def check_regression_range(self, param: TraceRangeParam) -> bool:
        '''Check realtime regression by comparing ranged
        durations to baseline durations'''
        # Null Hypothesis
        regression = False

        state = await self._storage_repo.retrieve_state()
        state.lastRegressionCheck = datetime.now().strftime("%d/%m/%y %H:%M:%S")

        if not state.baselineReady:
            logger.info("Baseline Not Ready")
            await self._storage_repo.update_state(state)

            return False

        ranged_traces = await get_ranged_traces(param)
        if env.debug:
            logger.debug(f"Num of traces: {len(ranged_traces)}, limit: {param.limit}")

        ranged_durations = extract_durations(ranged_traces)
        if not ranged_durations:
            state.isRegression = regression
            await self._storage_repo.update_state(state)

            return False

        baseline_durations = await self._storage_repo.retrieve_durations(state.baselineKey.duration)
        # Reject null hypothesis if different distribution
        regression = not ks_test_same_dist(ranged_durations, baseline_durations, ALPHA, env.debug)
        if env.debug:
            if regression:
                logger.debug("Regression Detected")
            else:
                logger.debug("Regression not Detected")

        state.isRegression = regression
        await self._storage_repo.update_state(state)

        return regression

    async def check_regression_realtime(self) -> bool:
        '''Check realtime regression by comparing realtime
        durations to baseline durations'''
        regression = False

        state = await self._storage_repo.retrieve_state()
        state.lastRegressionCheck = datetime.now().strftime("%d/%m/%y %H:%M:%S")

        if not state.baselineReady:
            await self._storage_repo.update_state(state)
            raise ValueError("Baseline is not ready")

        realtime_traces = await get_realtime_traces()
        realtime_durations = extract_durations(realtime_traces)
        if not realtime_durations:
            state.isRegression = regression
            await self._storage_repo.update_state(state)
            logger.info("Realtime Durations empty, returning False")

            return regression

        baseline_durations = await self._storage_repo.retrieve_durations(state.baselineKey.duration)
        # Regression = Different Distribution
        regression = not ks_test_same_dist(realtime_durations, baseline_durations, ALPHA, env.debug)

        state.isRegression = regression
        await self._storage_repo.update_state(state)

        return regression

    async def critical_path_ranged(self, param: TraceRangeParam) -> list[ComparisonResult]:
        state = await self._storage_repo.retrieve_state()

        if not state.baselineReady:
            logger.info("Baseline Not Ready")
            return []

        ranged_traces = await get_ranged_traces(param)
        if env.debug:
            logger.debug(f"Num of traces: {len(ranged_traces)}, limit: {param.limit}")

        ranged_paths = extract_critical_path(ranged_traces)
        if not ranged_paths:
            return []

        baseline_paths = await self._storage_repo.retrieve_critical_path(state.baselineKey.criticalPath)
        result_paths = compare_critical_path(baseline_paths, ranged_paths)

        return result_paths

    async def perform_analysis(self):
        '''Perform Critical Path analysis + Correlation Analysis
        and store in redis'''
        state = await self._storage_repo.retrieve_state()
        if not state.baselineReady:
            logger.info("Baseline Not Ready")
            return

        realtime_traces = await get_realtime_traces()
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
            if env.debug:
                logger.debug("Ranged trace empty")

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
        realtime_paths = extract_critical_path_v3(ranged_traces)
        baseline_paths = await self._storage_repo.retrieve_critical_path_v2(state.baselineKey.criticalPath)
        critical_path_result = compare_critical_path_v3(baseline_paths, realtime_paths, latency_threshold)

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
        state.lastRegressionCheck = datetime.now().strftime("%d/%m/%y %H:%M:%S")

        if not state.baselineReady:
            await self._storage_repo.update_state(state)
            raise ValueError("Baseline is not ready")

        realtime_traces = await get_realtime_traces()
        realtime_durations = extract_durations(realtime_traces)
        if not realtime_durations:
            state.isRegression = regression
            await self._storage_repo.update_state(state)
            logger.info("Realtime Durations empty, returning False")

            return regression

        baseline_durations = await self._storage_repo.retrieve_durations(state.baselineKey.duration)

        # Regression = Different Distribution
        regression = not ks_test_same_dist(realtime_durations, baseline_durations, ALPHA, env.debug)
        if env.debug:
            if regression:
                logger.debug("Regression Detected")
            else:
                logger.debug("Regression not Detected")

        state.isRegression = regression
        state.currentAnalysis = AnalysisResult()

        if not regression:
            await self._storage_repo.update_state(state)
            return AnalysisResult()

        # Regression detected, perform critical path analysis
        realtime_paths = extract_critical_path_v3(realtime_traces)
        baseline_paths = await self._storage_repo.retrieve_critical_path_v2(state.baselineKey.criticalPath)
        critical_path_result = compare_critical_path_v3(baseline_paths, realtime_paths)

        analysis_result = AnalysisResult(
            critical_path_result=critical_path_result,
            regression=regression
        )
        state.currentAnalysis = analysis_result
        await self._storage_repo.update_state(state)

        return analysis_result
