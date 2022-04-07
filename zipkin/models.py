from typing import Dict, List, Literal, Optional
from pydantic import BaseModel


class TraceParam(BaseModel):
    serviceName: Optional[str]
    spanName: Optional[str]
    annotationQuery: Optional[str]
    minDuration: Optional[int]
    maxDuration: Optional[int]
    endTs: Optional[int]
    lookback: Optional[int]
    limit: Optional[int]


class Endpoint(BaseModel):
    serviceName: Optional[str]
    ipv4: Optional[str]
    ipv6: Optional[str]
    port: Optional[int]


class Annotation(BaseModel):
    timestamp: int
    value: int


class Span(BaseModel):
    id: str
    traceId: str
    parentId: Optional[str]
    name: Optional[str]
    kind: Optional[Literal["CLIENT", "SERVER", "PRODUCER", "CONSUMER"]]
    timestamp: Optional[int]
    duration: Optional[int]
    debug: Optional[bool]
    shared: Optional[bool]
    localEndpoint: Optional[Endpoint]
    remoteEndpoint: Optional[Endpoint]
    annotations: Optional[list[Annotation]]
    tags: Optional[dict[str, str]]


class AdjustedTrace(BaseModel):
    id: str
