from typing import Optional
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
    baseline: Optional[float]
    realtime: Optional[float]
    suspected: bool = False


class ComparisonResult(BaseModel):
    root: str
    operation: str
    baseline: Optional[float]
    realtime: Optional[float]
    suspected: bool = False
