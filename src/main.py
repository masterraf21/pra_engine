from config import state
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from scheduling.jobs import perform_analysis
from storage.retrieve import retrieve_critical_path
from utils.json import jsonize
from dependencies import init_dependencies

app = FastAPI()


@app.on_event('startup')
def init():
    dep = init_dependencies()


@app.get("/")
async def root():
    return {"message": "Hello Engine Users"}


@app.get("/state")
async def get_state():
    state_data = jsonable_encoder(state)
    return JSONResponse(content=state_data)


# @app.post("/analysis")
# async def do_analysis():
#     perform_analysis()


@app.get("/result/critical_path")
async def get_critical_path_result():
    if state.resultKey.criticalPath:
        result = retrieve_critical_path(state.resultKey.criticalPath)
        result_json = jsonize(result)
        return JSONResponse(content=result_json)
    else:
        return {"message": "Result Not Available"}
