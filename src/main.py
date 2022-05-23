
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import State

from src.config import get_settings
from src.scheduling.jobs import EngineJobs
from src.scheduling.models import (AnalysisParam, AnalysisResult, GlobalState,
                                   TraceRangeParam)
from src.scheduling.scheduler import Scheduler
from src.storage.redis import init_redis
from src.storage.repository import StorageRepository
from src.utils.logging import get_logger

env = get_settings()
logger = get_logger(__name__)
origins = ["*"]


def get_repo(state: State) -> StorageRepository:
    repo: StorageRepository = state.storage_repo
    return repo


def get_jobs(state: State) -> EngineJobs:
    jobs: EngineJobs = state.jobs
    return jobs


app = FastAPI(title="PRA Engine", version="0.5")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
async def startup_event():
    logger.info("Initiating PRA Engine...")
    logger.info(f"Running in {env.environment} environment")
    if env.debug:
        logger.debug("Running in debug mode")

    app.state.redis = await init_redis()
    app.state.storage_repo = StorageRepository(app.state.redis)
    app.state.jobs = EngineJobs(app.state.storage_repo)
    if env.scheduler:
        scheduler = Scheduler(app.state.jobs)
        scheduler.start()


@app.on_event('shutdown')
async def shutdown_event():
    logger.info("Shutting Down PRA Engine...")
    await app.state.redis.close()


@app.get("/")
async def root():
    return {"message": "Hello Engine Users"}


@app.get("/state", response_model=GlobalState)
async def get_state():
    repo = get_repo(app.state)
    state = await repo.retrieve_state()
    return JSONResponse(content=jsonable_encoder(state))


@app.post("/baseline")
async def retrieve_baseline(param: TraceRangeParam):
    try:
        jobs = get_jobs(app.state)
        await jobs.retrieve_baseline_models(param)
        return JSONResponse(content={
            "message": "Baseline retrieved"
        })
    except ValueError as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete("/baseline")
async def remove_baseline():
    jobs = get_jobs(app.state)
    await jobs.remove_baseline_model()
    return JSONResponse(content={
        "message": "Baseline removed"
    })


@app.get("/analysis/realtime", response_model=AnalysisResult)
async def regression_analysis_realtime():
    try:
        jobs = get_jobs(app.state)

        result = await jobs.regression_analysis_realtime()
        return JSONResponse(content=jsonable_encoder(result))
    except ValueError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/analysis/range", response_model=AnalysisResult)
async def regression_analysis_range(param: AnalysisParam = Depends()):
    try:
        jobs = get_jobs(app.state)

        trace_param = TraceRangeParam(
            endDatetime=param.endDatetime,
            startDatetime=param.startDatetime,
            limit=param.limit
        )
        result = await jobs.regression_analysis_range(trace_param, param.latencyThreshold)
        return JSONResponse(content=jsonable_encoder(result))
    except ValueError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
