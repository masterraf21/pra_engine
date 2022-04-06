
from __future__ import annotations
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class Endpoint(BaseModel):
    serviceName: Optional[str]
    ipv4: Optional[str]
    ipv6: Optional[str]
    port: Optional[int]


class Annotation(BaseModel):
    timestamp: int
    value: int


class Model(BaseModel):
    id: str
    traceId: str
    parentId: Optional[str]
    name: Optional[str]
    kind: Optional[Literal["CLIENT", "SERVER", "PRODUCER", "CONSUMER"]]
    timestamp: Optional[int]
    duration: Optional[int]
    debug: Optional[bool]
    localEndpoint: Endpoint
    remoteEndpoint: Endpoint
    annotations: List[Annotation]
    tags: Dict[str, str]


class AdjustedTrace(BaseModel):
    id: str
