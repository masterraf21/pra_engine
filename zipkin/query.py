import requests
from config import settings

API = settings.zipkin_api


def query_traces(param: dict) -> list[dict]:
    r = requests.get(url=f'{API}/traces', params={
        "serviceName": param["serviceName"]
    })
    return r.json()


def query_trace(id: str) -> dict:
    r = requests.get(url=f'{API}/trace/{id}')


def query_trace_many(ids: list[str]) -> dict:
    pass


def query_span_names(service_name: str) -> list[str]:
    pass


def query_dependencies(end_ts: int, lokback: int) -> list[dict]:
    pass


def query_services() -> list[str]:
    pass
