from src.utils.logging import get_logger
import aiohttp
from pydantic import parse_obj_as
from src.config import get_settings
from src.utils.checking import omit_none_dict

from .models import DependencyLink, Span, TraceParam

env = get_settings()
logger = get_logger(__name__)
API = env.zipkin_url


async def query_traces(param: TraceParam) -> list[list[Span]]:
    async with aiohttp.ClientSession() as session:
        filtered_param = omit_none_dict(param.dict())
        r = await session.get(url=f'{API}/traces', params=filtered_param)
        traces = await r.json()
        m = parse_obj_as(list[list[Span]], traces)
        return m


async def query_trace(id: str) -> list[Span]:
    async with aiohttp.ClientSession() as session:
        r = await session.get(url=f'{API}/trace/{id}')
        spans = await r.json()
        m = parse_obj_as(list[Span], spans)
        return m


async def query_trace_many(ids: list[str]) -> list[list[Span]]:
    async with aiohttp.ClientSession() as session:
        ids_str = "".join(ids)
        r = await session.get(url=f'{API}/traceMany', params={
            "traceIds": ids_str
        })
        traces = await r.json()
        m = parse_obj_as(list[list[Span]], traces)
        return m


async def query_span_names(service_name: str) -> list[str]:
    async with aiohttp.ClientSession() as session:
        r = await session.get(url=f'{API}/spans', params={
            "serviceName": service_name
        })
        return await r.json()


async def query_dependencies(end_ts: int, lookback: int = None) -> list[DependencyLink]:
    async with aiohttp.ClientSession() as session:
        r = await session.get(url=f'{API}/dependencies', params={
            "endTs": end_ts,
            "lookback": lookback
        })
        deps = await r.json()
        m = parse_obj_as(list[DependencyLink], deps)
        return m


async def query_services() -> list[str]:
    async with aiohttp.ClientSession() as session:
        r = await session.get(url=f'{API}/services')
        return await r.json()
