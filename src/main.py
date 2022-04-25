from src.config import state
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from scheduling.jobs import perform_analysis, get_baseline_traces
from storage.retrieve import retrieve_critical_path
from utils.json import jsonize
from dependencies import init_dependencies
from utils.logging import get_logger
from storage.repository import StorageRepositorySync, StorageRepositoryAsync

logger = get_logger(__name__)

app = FastAPI(title="PRA Engine", version="0.5")


@app.on_event('startup')
async def startup_event():
    logger.info("Initiating PRA Engine...")
    dep = await init_dependencies()
    app.state.dep = dep
    app.state.sync_repo = StorageRepositorySync(
        redis=app.state.dep.redis_sync)
    # app.state.async_repo = StorageRepositoryAsync(
    #     redis=app.state.dep.redis_async)


@app.on_event('shutdown')
async def shutdown_event():
    logger.info("Shutting Down PRA Engine...")
    app.state.dep.redis_sync.close()
    # await app.state.dep.redis_async.close()


@app.get("/")
async def root():
    return {"message": "Hello Engine Users"}


@app.get("/state")
async def get_state():
    state_data = jsonable_encoder(state)
    return JSONResponse(content=state_data)


@app.post("/baseline")
async def get_baseline():
    get_baseline_traces()


@app.get("/result/critical_path")
async def get_critical_path_result():
    if state.resultKey.criticalPath:
        result = retrieve_critical_path(state.resultKey.criticalPath)
        result_json = jsonize(result)
        return JSONResponse(content=result_json)
    else:
        return {"message": "Result Not Available"}