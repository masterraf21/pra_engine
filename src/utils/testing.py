import json
import random
import string
from pathlib import Path

from pydantic import parse_obj_as
from src.zipkin.models import AdjustedTrace
from src.critical_path.models import CriticalPath, PathDuration
from src.transform.extract import extract_critical_path

JSON_RELATIVE_PATH = "../../test/json"


def get_path_v3(filename: str) -> list[PathDuration]:
    raw_json = get_json(filename)
    data_list = []
    for data in raw_json:
        data_list.append(json.loads(data))
    parsed_data = parse_obj_as(list[AdjustedTrace], data_list)
    paths = extract_critical_path(parsed_data)

    return paths


def get_traces_json(filename: str) -> list[AdjustedTrace]:
    raw_json = get_json(filename)
    data_list = []
    for data in raw_json:
        data_list.append(json.loads(data))
    parsed_data = parse_obj_as(list[AdjustedTrace], data_list)
    return parsed_data


def get_path_json(filename: str) -> list[CriticalPath]:
    data = get_json(filename)
    parsed_data = parse_obj_as(list[CriticalPath], data)
    return parsed_data


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_json(file_name: str):
    path = Path(__file__).parent / f"{JSON_RELATIVE_PATH}/{file_name}"
    with open(path, 'r') as f:
        j = json.loads(f.read())
        return j


def write_json(content: str, file_name: str):
    path = Path(__file__).parent / f"{JSON_RELATIVE_PATH}/{file_name}"
    with open(path, "w") as outfile:
        outfile.write(content)
