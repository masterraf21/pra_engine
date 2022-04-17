from config import state
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from scheduling.jobs import perform_analysis

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Engine Users"}


@app.get("/state")
async def get_state():
    state_data = jsonable_encoder(state)
    return JSONResponse(content=state_data)


@app.post("/analysis")
async def do_analysis():
    perform_analysis()
