
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.scheduling.jobs import EngineJobs
from src.scheduling.scheduler import Scheduler
from src.scheduling.models import TraceRangeParam
from src.storage.redis import init_redis
from src.storage.repository import StorageRepository
from src.utils.logging import get_logger
from src.config import get_settings

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(title="PRA Engine", version="0.5")
app.logger = logger


@app.on_event('startup')
async def startup_event():
    logger.info("Initiating PRA Engine...")
    if settings.debug:
        logger.debug("Running in debug mode")

    app.state.redis = await init_redis()
    app.state.storage_repo = StorageRepository(app.state.redis)
    app.state.jobs = EngineJobs(app.state.storage_repo)
    scheduler = Scheduler(app.state.jobs)
    # scheduler.start()


@app.on_event('shutdown')
async def shutdown_event():
    logger.info("Shutting Down PRA Engine...")
    await app.state.redis.close()


@app.get("/")
async def root():
    return {"message": "Hello Engine Users"}


@app.get("/state")
async def get_state():
    state = await app.state.storage_repo.retrieve_state()
    return JSONResponse(content=jsonable_encoder(state))


@app.get("/regression/range")
async def check_regression_range(end_datetime: str, start_datetime: str, limit: int = 5000):
    try:
        param = TraceRangeParam(
            endDatetime=end_datetime,
            startDatetime=start_datetime,
            limit=limit
        )
        regression = await app.state.jobs.check_regression_range(param)
        if regression:
            output_str = "Regression detected"
        else:
            output_str = "Regression not detected"

        return JSONResponse(content={
            "message": output_str
        })
    except ValueError as e:
        print(e)


@app.get("/regression/fixed")
async def check_regression_realtime(limit: int = 5000):
    regression = await app.state.jobs.check_regression_realtime()
    output_str = ""
    if regression:
        output_str = "Regression detected"
    else:
        output_str = "Regression not detected"

    return JSONResponse(content={
        "message": output_str
    })


@app.post("/baseline")
async def retrieve_baseline(param: TraceRangeParam):
    try:
        logger.info(param)
        await app.state.jobs.retrieve_baseline_models(param)
        return JSONResponse(content={
            "message": "Baseline retrieved"
        })
    except ValueError:
        return HTTPException(status_code=400)


@app.delete("/baseline")
async def remove_baseline():
    await app.state.jobs.remove_baseline_model()
    return JSONResponse(content={
        "message": "Baseline removed"
    })
