import asyncio
import json
import time
from datetime import datetime

from src.config import get_settings
from src.critical_path import compare_critical_path
from src.critical_path.models import ComparisonResult
from src.statistic.ks import ks_test_same_dist
from src.storage.repository import StorageRepository
from src.transform import extract_critical_path, extract_durations
from src.utils import diff_two_datetime_str
from src.utils.logging import get_logger
from src.zipkin.helper import retrieve_traces
from src.zipkin.models import AdjustedTrace, TraceParam

from .constants import REALTIME_CHECK_PERIOD, TRACE_LIMIT
from .models import TraceRangeParam

settings = get_settings()
logger = get_logger(__name__)
ALPHA = settings.alpha


class EngineJobs:
    def __init__(self, redis_repo: StorageRepository) -> None:
        self._storage_repo = redis_repo

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

    async def get_realtime_traces(self) -> list[AdjustedTrace]:
        param = TraceParam(
            endTs=round(time.time() * 1000),
            limit=TRACE_LIMIT,
            lookback=REALTIME_CHECK_PERIOD*1000
        )
        traces = await retrieve_traces(param)
        return traces

    async def remove_baseline_model(self):
        state = await self._storage_repo.retrieve_state()
        state.baselineReady = False
        state.baselineKey.duration = ""
        state.baselineKey.criticalPath = ""
        await self._storage_repo.update_state(state)

    async def retrieve_baseline_models(self, param: TraceRangeParam):
        '''Query baseline traces from zipkin, transform into models
        , store in redis, change global state'''

        traces = await self.get_ranged_traces(param)
        if settings.debug:
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

        ranged_traces = await self.get_ranged_traces(param)
        if settings.debug:
            logger.debug(f"Num of traces: {len(ranged_traces)}, limit: {param.limit}")

        ranged_durations = extract_durations(ranged_traces)
        if not ranged_durations:
            state.isRegression = regression
            await self._storage_repo.update_state(state)

            return False

        baseline_durations = await self._storage_repo.retrieve_durations(state.baselineKey.duration)
        # Reject null hypothesis if different distribution
        regression = not ks_test_same_dist(ranged_durations, baseline_durations, ALPHA, settings.debug)
        if settings.debug:
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
        # Null Hypothesis
        regression = False

        state = await self._storage_repo.retrieve_state()
        state.lastRegressionCheck = datetime.now().strftime("%d/%m/%y %H:%M:%S")

        if not state.baselineReady:
            logger.info("Baseline Not Ready")
            await self._storage_repo.update_state(state)

            return False

        realtime_traces = await self.get_realtime_traces()
        realtime_durations = extract_durations(realtime_traces)
        if not realtime_durations:
            state.isRegression = regression
            await self._storage_repo.update_state(state)
            if settings.debug:
                logger.debug("Realtime Durations empty, returning False")

            return False

        baseline_durations = await self._storage_repo.retrieve_durations(state.baselineKey.duration)
        # Reject null hypothesis if different distribution
        regression = not ks_test_same_dist(realtime_durations, baseline_durations, ALPHA, settings.debug)

        state.isRegression = regression
        await self._storage_repo.update_state(state)

        return regression

    async def critical_path_ranged(self, param: TraceRangeParam) -> list[ComparisonResult]:
        state = await self._storage_repo.retrieve_state()

        if not state.baselineReady:
            logger.info("Baseline Not Ready")
            return []

        ranged_traces = await self.get_ranged_traces(param)
        if settings.debug:
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
        await self._storage_repo.update_state(state)

    async def regression_analysis(self):
        logger.info("Doing Regression Analysis")
        regression = await self.check_regression_realtime()
        if regression:
            logger.info("Regression Detected")
            await self.perform_analysis()
        else:
            logger.info("No Regression Detected")

    async def regression_analysis_fake(self):
        logger.info("Sleeping for")
        # logger.info("Doing Regression Analysis")
        await asyncio.sleep(1)
        logger.info("1 second")
