import requests
from config import settings
from .models import TraceParam, Span
from pydantic import parse_obj_as

API = settings.zipkin_api


def query_traces(param: TraceParam) -> list[list[Span]]:
    r = requests.get(url=f'{API}/traces', params=param.dict())
    # r = requests.get(url=f'{API}/traces', params={
    #     "serviceName": d["serviceName"],
    #     "spanName": d["spanName"],
    #     "annotationQuery": d["annotationQuery"],
    #     "minDurataion": d["minDuration"],
    #     "maxDuration": d["maxDuration"],
    #     "endTs": d["endTs"],
    #     "lookback": d["lookback"],
    #     "limit": d["limit"],
    # })
    traces = r.json()
    m = parse_obj_as(list[list[Span]], traces)
    return m


def query_trace(id: str) -> list[Span]:
    r = requests.get(url=f'{API}/trace/{id}')
    spans = r.json()
    m = parse_obj_as(list[Span], spans)
    return m


def query_trace_many(ids: list[str]) -> list[list[Span]]:
    pass


def query_span_names(service_name: str) -> list[str]:
    pass


def query_dependencies(end_ts: int, lokback: int) -> list[dict]:
    pass


def query_services() -> list[str]:
    pass
