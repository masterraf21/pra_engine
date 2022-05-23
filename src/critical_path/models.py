from typing import Optional
from pydantic import BaseModel


class PathDuration(BaseModel):
    operation: Optional[str]
    duration: Optional[float]
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
    operation: Optional[str]
    baseline: Optional[float]
    realtime: Optional[float]
    diff: Optional[float]
    suspected: bool = False


class Result(BaseModel):
    suspected: list[ComparisonResult] = []
    normal: list[ComparisonResult] = []
