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


class CleanedSpan(BaseModel):
    id: str
    traceId: str
    parentId: str
    name: str
    kind: Literal["CLIENT", "SERVER", "PRODUCER", "CONSUMER"]
    timestamp: int
    duration: int
    debug: bool
    shared: bool
    localEndpoint: Endpoint
    remoteEndpoint: Endpoint
    annotations: list[Annotation]
    tags: dict[str, str]


class AdjustedAnnotation(BaseModel):
    isDerived: Optional[bool]
    value: str
    timestamp: int
    endpoint: str
    relativeTime: Optional[str]
    left: Optional[int]
    width: Optional[int]


class AdjustedTag(BaseModel):
    key: str
    value: str
    endpoints: Optional[list[str]]


class AdjustedSpan(BaseModel):
    spanId: str
    spanName: str
    serviceName: Optional[str]
    parentId: Optional[str]
    childIds: list[str]
    serviceNames: list[str]
    timestamp: Optional[int]
    duration: Optional[float]
    durationStr: str
    tags: list[AdjustedTag]
    annotations: list[AdjustedAnnotation]
    errorType: str
    depth: int
    width: float
    left: int
    debug: bool


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
    depth: int
    durationStr: str
    rootSpan: RootSpan
    spans: list[AdjustedSpan]
