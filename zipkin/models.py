from typing import Literal, Optional
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


class DependencyLink(BaseModel):
    parent: str
    child: str
    callCount: int
    errorCount: Optional[int]


class Endpoint(BaseModel):
    serviceName: Optional[str]
    ipv4: Optional[str]
    ipv6: Optional[str]
    port: Optional[int]


class Annotation(BaseModel):
    timestamp: int
    value: str


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


class AdjustedAnnotation(BaseModel):
    value: str
    timestamp: int
    endpoint: Endpoint
    relativeTime: Optional[str]


class AdjustedSpan(BaseModel):
    spanId: str
    spanName: str
    serviceName: str
    parentId: Optional[str]
    childIds: list[str]
    serviceNames: list[str]
    timestamp: int
    duration: float
    durationStr: str
    tags: list[dict[str, str]]
    annotations: list[AdjustedAnnotation]
    errorType: str
    depth: int
    width: int
    left: int


class ServiceNameAndSpanCount(BaseModel):
    serviceName: str
    spanCount: int


class RootSpan(BaseModel):
    serviceName: str
    spanName: str


class AdjustedTrace(BaseModel):
    traceId: str
    serviceNameAndSpanCounts: list[ServiceNameAndSpanCount]
    duration: int
    durationStr: str
    rootSpan: RootSpan
    spans: list[AdjustedSpan]
