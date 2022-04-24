import json
from fastapi.encoders import jsonable_encoder


def jsonize(obj: list):
    obj_dict = [o.dict() for o in obj]
    return jsonable_encoder(obj_dict)
