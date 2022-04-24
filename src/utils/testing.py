import json
import random
import string
from pathlib import Path

from pydantic import parse_obj_as
from src.zipkin.models import Span

JSON_RELATIVE_PATH = "../test/json"


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


def get_trace(file_name: str) -> list[Span]:
    j = get_json(file_name)
    trace = parse_obj_as(list[Span], j)
    return trace
