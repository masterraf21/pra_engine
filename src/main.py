
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.scheduling.jobs import EngineJobs
from src.scheduling.scheduler import Scheduler
from src.config import state
from src.storage.redis import init_redis
from src.storage.repository import StorageRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)
app = FastAPI(title="PRA Engine", version="0.5")


@app.on_event('startup')
async def startup_event():
    logger.info("Initiating PRA Engine...")
    app.state.redis = await init_redis()
    app.state.storage_repo = StorageRepository(app.state.redis)
    app.state.jobs = EngineJobs(app.state.storage_repo, logger)

    scheduler = Scheduler(app.state.jobs, logger)
    scheduler.start()


@app.on_event('shutdown')
async def shutdown_event():
    logger.info("Shutting Down PRA Engine...")
    await app.state.redis.close()


@app.get("/")
async def root():
    return {"message": "Hello Engine Users"}


@app.get("/state")
async def get_state():
    state_data = jsonable_encoder(state)
    return JSONResponse(content=state_data)


@app.post("/baseline")
async def get_baseline():
    await app.state.jobs.retrieve_baseline_models()
