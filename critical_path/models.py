from typing import Optional
from path import Path
from pydantic import BaseModel


class PathDuration(BaseModel):
    operation: str
    duration: float
    counter: Optional[int]


class CriticalPath(BaseModel):
    root: str
    durations: list[PathDuration]


class Comparison(BaseModel):
    operation: str
    baseline: float
    realtime: float
    suspected: bool


class CriticalPathResuilt(BaseModel):
    root: str
    comparisonResult: list[Comparison]
