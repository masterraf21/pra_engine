from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from .jobs import EngineJobs
from .constants import REALTIME_CHECK_PERIOD


class Scheduler:
    def __init__(self, jobs: EngineJobs, logger: logging.Logger) -> None:
        self._jobs = jobs
        self._logger = logger
        self._sch = AsyncIOScheduler()

    def start(self):
        self._logger.info("Starting Scheduler")
        self._sch.start()
        self._sch.add_job(self._jobs.regression_analysis, 'interval', seconds=REALTIME_CHECK_PERIOD)
