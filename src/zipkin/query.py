import requests
import aiohttp
from config import settings
from .models import TraceParam, Span, DependencyLink
from pydantic import parse_obj_as
from src.utils.checking import omit_none_dict

API = settings.zipkin_api


def query_traces_sync(param: TraceParam) -> list[list[Span]]:
    r = requests.get(url=f'{API}/traces', params=param.dict())
    # print(r.url)
    traces = r.json()
    m = parse_obj_as(list[list[Span]], traces)
    return m


async def query_traces(param: TraceParam) -> list[list[Span]]:
    async with aiohttp.ClientSession() as session:
        filtered_param = omit_none_dict(param.dict())
        r = await session.get(url=f'{API}/traces', params=filtered_param)
        traces = await r.json()
        m = parse_obj_as(list[list[Span]], traces)
        return m


def query_trace(id: str) -> list[Span]:
    r = requests.get(url=f'{API}/trace/{id}')
    spans = r.json()
    m = parse_obj_as(list[Span], spans)
    return m


def query_trace_many(ids: list[str]) -> list[list[Span]]:
    ids_str = "".join(ids)
    r = requests.get(url=f'{API}/traceMany', params={
        "traceIds": ids_str
    })
    traces = r.json()
    print(type(traces))
    m = parse_obj_as(list[list[Span]], traces)
    return m


def query_span_names(service_name: str) -> list[str]:
    r = requests.get(url=f'{API}/spans', params={
        "serviceName": service_name
    })
    return r.json()


def query_dependencies(end_ts: int, lookback: int = None) -> list[DependencyLink]:
    r = requests.get(url=f'{API}/dependencies', params={
        "endTs": end_ts,
        "lookback": lookback
    })
    deps = r.json()
    m = parse_obj_as(list[DependencyLink], deps)
    return m


def query_services() -> list[str]:
    r = requests.get(url=f'{API}/services')
    return r.json()
